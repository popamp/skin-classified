"""Measures paints and pixel art on the reference skin's bitmaps (numpy, Pillow)."""
import os
import zipfile
from io import BytesIO

import numpy as np
from PIL import Image

from svgkit import hexc

LUMA = np.array([0.299, 0.587, 0.114])


class Reference:
    """The reference skin: a .wsz file or a folder of its bitmaps."""

    def __init__(self, path):
        self.path, self.cache = path, {}

    def sheet(self, name):
        if name not in self.cache:
            self.cache[name] = np.asarray(Image.open(self._open(name + ".bmp")).convert("RGB"), dtype=float)
        return self.cache[name]

    def _open(self, file):
        if os.path.isdir(self.path):
            return os.path.join(self.path, file)
        with zipfile.ZipFile(self.path) as z:
            real = {n.lower().rsplit("/", 1)[-1]: n for n in z.namelist()}
            return BytesIO(z.read(real[file]))


def _points(img, x, y, w, h):
    ys, xs = np.mgrid[y : y + h, x : x + w]
    return xs.ravel() + 0.5, ys.ravel() + 0.5, img[y : y + h, x : x + w].reshape(-1, 3)


def mean(img, x, y, w, h):
    return {"solid": hexc(img[y : y + h, x : x + w].reshape(-1, 3).mean(0))}


def _model(xs, ys, cs):
    """Colour as a linear function of position, fitted while ignoring outliers (icons, texture specks)."""
    a = np.column_stack([np.ones_like(xs), xs, ys])
    keep = np.ones(len(xs), bool)
    for _ in range(3):
        coef, *_ = np.linalg.lstsq(a[keep], cs[keep], rcond=None)
        res = np.abs(a @ coef - cs).max(1)
        new = res < max(12.0, 2.5 * np.median(res))
        if new.sum() < 3 or (new == keep).all():
            break
        keep = new
    return a @ coef, keep


def lin_points(xs, ys, cs, axis="auto"):
    """A linear gradient fitted to coloured points, or a flat colour when it barely changes."""
    _, keep = _model(xs, ys, cs)
    xs, ys, cs = xs[keep], ys[keep], cs[keep]
    if axis == "x":
        u = np.array([1.0, 0.0])
    elif axis == "y":
        u = np.array([0.0, 1.0])
    else:
        a = np.column_stack([np.ones_like(xs), xs, ys])
        coef, *_ = np.linalg.lstsq(a, cs @ LUMA, rcond=None)
        g = coef[1:]
        if np.hypot(*g) < 1e-6:
            return {"solid": hexc(cs.mean(0))}
        u = g / np.hypot(*g)
    t = xs * u[0] + ys * u[1]
    t0, t1 = t.min() - 0.5, t.max() + 0.5
    if t1 - t0 < 1e-6:
        return {"solid": hexc(cs.mean(0))}
    a = np.column_stack([np.ones_like(t), t])
    coef, *_ = np.linalg.lstsq(a, cs, rcond=None)
    c0, c1 = coef[0] + coef[1] * t0, coef[0] + coef[1] * t1
    if np.abs(c1 - c0).max() < 3:
        return {"solid": hexc(cs.mean(0))}
    return {"lin": [float(u[0] * t0), float(u[1] * t0), float(u[0] * t1), float(u[1] * t1)], "stops": [[0, hexc(c0)], [1, hexc(c1)]]}


def lin_area(img, x, y, w, h, axis):
    return lin_points(*_points(img, x, y, w, h), axis)


def lin_ring(img, x, y, w, h, top_left):
    """The top and left edge of a ring (without the far corners), or its bottom and right edge."""
    if top_left:
        parts = [_points(img, x, y, w - 1, 1), _points(img, x, y + 1, 1, h - 2)]
    else:
        parts = [_points(img, x + w - 1, y, 1, h), _points(img, x, y + h - 1, w - 1, 1)]
    xs, ys, cs = (np.concatenate(p) for p in zip(*parts))
    return lin_points(xs, ys, cs)


def lin_edge(img, x, y, w, h):
    """The whole top row and left column of an area."""
    parts = [_points(img, x, y, w, 1), _points(img, x, y + 1, 1, h - 1)]
    xs, ys, cs = (np.concatenate(p) for p in zip(*parts))
    return lin_points(xs, ys, cs)


def profile(img, x, y, w, h, axis, n, skip=()):
    """`n` stops of the area's mean colour along `axis`, ignoring the `skip` rectangles."""
    area = img[y : y + h, x : x + w]
    use = np.ones((h, w), bool)
    for sx, sy, sw, sh in skip:
        use[max(0, sy - y) : max(0, sy + sh - y), max(0, sx - x) : max(0, sx + sw - x)] = False
    if axis == "y":
        area, use = area.transpose(1, 0, 2), use.T
    length = area.shape[1]
    edges = np.linspace(0, length, n + 1)
    pos, cols = [], []
    for i in range(n):
        a, b = int(edges[i]), max(int(edges[i]) + 1, int(edges[i + 1]))
        m = use[:, a:b]
        if m.any():
            pos.append((a + b) / 2 / length)
            cols.append(np.median(area[:, a:b][m], 0))  # the median ignores thin markings
    stops = [[float(p), hexc(c)] for p, c in zip(pos, cols)]
    if axis == "x":
        vec = [x, 0, x + w, 0]
    else:
        vec = [0, y, 0, y + h]
    return {"lin": [float(v) for v in vec], "stops": stops}


def _mask(x, y, w, h, skip):
    """True where the area is not inside one of the `skip` rectangles."""
    use = np.ones((h, w), bool)
    for sx, sy, sw, sh in skip:
        use[max(0, sy - y) : max(0, sy + sh - y), max(0, sx - x) : max(0, sx + sw - x)] = False
    return use


def _background(img, x, y, w, h, bg, use):
    """The colour each pixel is compared with (see `pixels`), or None when there is too little to fit."""
    if bg == "lin":
        xs, ys, cs = _points(img, x, y, w, h)
        u = use.ravel()
        if u.sum() < 3:
            return None
        a = np.column_stack([np.ones_like(xs), xs, ys])
        _, keep = _model(xs[u], ys[u], cs[u])
        coef, *_ = np.linalg.lstsq(a[u][keep], cs[u][keep], rcond=None)
        return (a @ coef).reshape(h, w, 3)
    if bg.startswith("col:"):
        return img[y : y + h, int(bg[4:])][:, None, :]
    if bg == "all":
        return np.full(3, -1000)
    return np.array([int(bg[i : i + 2], 16) for i in (1, 3, 5)])


def _row_runs(area, keep, j):
    """Runs of one colour in row `j` of the kept pixels: (first column, length, colour)."""
    row, i, w = [], 0, keep.shape[1]
    while i < w:
        if not keep[j, i]:
            i += 1
            continue
        c, k = tuple(area[j, i]), i
        while k < w and keep[j, k] and tuple(area[j, k]) == c:
            k += 1
        row.append((i, k - i, hexc(c)))
        i = k
    return row


def _rectangles(area, keep, x, y):
    """Kept pixels as rectangles [x, y, w, h, colour]: runs along rows, stacked where rows repeat them."""
    runs, open_runs = [], {}
    for j in range(keep.shape[0]):
        still = {}
        for i, rw, c in _row_runs(area, keep, j):
            prev = open_runs.get((i, rw, c))
            if prev is None:
                prev = [x + i, y + j, rw, 0, c]
                runs.append(prev)
            prev[3] += 1
            still[(i, rw, c)] = prev
        open_runs = still
    return runs


def pixels(img, x, y, w, h, bg, tol, skip=()):
    """Pixels differing from `bg` by more than `tol`, merged into same-coloured rectangles.

    `bg` is a colour, "lin" (a gradient fitted to the area), "col:X" (column X, row by row) or
    "all"; pixels in the `skip` rectangles are left out.
    """
    use = _mask(x, y, w, h, skip)
    ref = _background(img, x, y, w, h, bg, use)
    if ref is None:
        return []
    area = img[y : y + h, x : x + w].astype(int)
    keep = (np.abs(area - ref).max(2) > tol) & use
    return _rectangles(area, keep, x, y)
