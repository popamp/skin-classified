"""SVG sheets whose colours are fitted to the reference skin.

Geometry is written by hand in the art modules; colours come from `Fits`:
with the reference bitmaps at hand (`--ref`) each fit is measured from
them and stored in `fits.json`, otherwise the stored value is used. So the
skin builds without the reference, and a rebuild from it is idempotent.
"""
import json
import os
from contextlib import contextmanager


def hexc(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in rgb)


def _fit():
    """The fitting module; it needs numpy and Pillow, so only a build with --ref loads it."""
    import fit

    return fit


def _shifted(img, dx, dy):
    """The image moved so that drawing position (x, y) reads pixel (x + dx, y + dy)."""
    if not (dx or dy):
        return img
    import numpy as np

    h, w = img.shape[:2]
    out = np.zeros((max(h, h - dy), max(w, w - dx), 3))
    y0, x0 = max(0, -dy), max(0, -dx)
    y1, x1 = min(out.shape[0], h - dy), min(out.shape[1], w - dx)
    out[y0:y1, x0:x1] = img[y0 + dy : y1 + dy, x0 + dx : x1 + dx]
    return out


class Fits:
    """Fitted values by key: measured from the reference, or read back from the cache."""

    def __init__(self, cache_path, ref_dir=None):
        self.path, self.used = cache_path, {}
        self.data = {}
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                self.data = json.load(f)
        self.ref = None
        if ref_dir:
            self.ref = _fit().Reference(ref_dir)

    def get(self, key, measure):
        if self.ref:
            value = measure(self.ref)
        elif key in self.data:
            value = self.data[key]
        else:
            raise SystemExit(f"no fitted value for {key}; build once with --ref")
        self.used[key] = value
        return value

    def save(self):
        if self.ref:
            with open(self.path, "w") as f:
                json.dump(dict(sorted(self.used.items())), f, indent=0, separators=(",", ":"))
                f.write("\n")


class Sheet:
    """One SVG picture; `ref` names the reference bitmap its fits are measured on."""

    def __init__(self, fits, ref, w, h):
        self.fits, self.ref, self.w, self.h = fits, ref, w, h
        self.defs, self.body, self.n = [], [], 0
        self.src = (ref, 0, 0)  # where fits are measured: sheet, and offset from the drawing position

    @contextmanager
    def source(self, ref=None, dx=0, dy=0, absolute=False):
        """Measure on another sheet and/or `dx`, `dy` away from where the drawing goes
        (added to an enclosing `source`, unless `absolute`)."""
        old = self.src
        bx, by = (0, 0) if absolute else old[1:]
        self.src = (ref or old[0], bx + dx, by + dy)
        try:
            yield
        finally:
            self.src = old

    # --- paints ---------------------------------------------------------------
    def paint(self, spec):
        """A fill attribute value for "#rrggbb", a fitted paint dict, or None."""
        if spec is None:
            return "none"
        if isinstance(spec, str):
            return spec
        if "solid" in spec:
            return spec["solid"]
        self.n += 1
        gid = f"p{self.n}"
        x1, y1, x2, y2 = spec["lin"]
        stops = "".join(f'<stop offset="{o:.3f}" stop-color="{c}"/>' for o, c in spec["stops"])
        self.defs.append(
            f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
            f'x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}">{stops}</linearGradient>'
        )
        return f"url(#{gid})"

    def _fit(self, op, args, measure):
        ref, dx, dy = self.src
        shift = f"@{dx},{dy}" if dx or dy else ""
        key = f"{ref}{shift}|{op}|{','.join(map(str, args))}"
        return self.fits.get(key, lambda r: measure(_shifted(r.sheet(ref), dx, dy)))

    def lin(self, x, y, w, h, axis="auto"):
        """A two-stop gradient (or a flat colour) fitted to the area's pixels."""
        return self._fit("lin", (x, y, w, h, axis), lambda img: _fit().lin_area(img, x, y, w, h, axis))

    def prof(self, x, y, w, h, axis, n, skip=()):
        """A gradient of `n` stops along `axis` ("x" or "y"): the area's mean colours, `skip` rectangles left out."""
        flat = tuple(v for r in skip for v in r)
        return self._fit("prof", (x, y, w, h, axis, n, *flat), lambda img: _fit().profile(img, x, y, w, h, axis, n, skip))

    def rows(self, x, y, w, h, n, skip=(), sample=None):
        """A surface as one horizontal gradient per row; `sample` maps a row to the row(s) measured instead."""
        for j in range(y, y + h):
            sy, sh = sample(j) if sample else (j, 1)
            # each row reaches half a pixel under the next one: no seams at fractional sizes
            self.rect(x, j, w, 1.5 if j < y + h - 1 else 1, self.prof(x, sy, w, sh, "x", n, skip))

    def cols(self, x, y, w, h):
        """Exact columns: each one a vertical gradient through its pixels."""
        for i in range(x, x + w):
            self.rect(i, y, 1.5 if i < x + w - 1 else 1, h, self.prof(i, y, 1, h, "y", h))

    def frame(self, x, y, w, h):
        """A gradient across an area, from the 1-pixel frame round it (to paint over what was in it)."""
        return self._fit("frame", (x, y, w, h), lambda img: _fit().lin_frame(img, x, y, w, h))

    def color(self, x, y, w=1, h=1):
        return self._fit("color", (x, y, w, h), lambda img: _fit().mean(img, x, y, w, h))

    # --- shapes ---------------------------------------------------------------
    def add(self, s):
        self.body.append(s)

    def rect(self, x, y, w, h, fill, extra=""):
        if w > 0 and h > 0:
            self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{self.paint(fill)}"{extra}/>')

    def rrect(self, x, y, w, h, r, fill, extra=""):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{self.paint(fill)}"{extra}/>')

    def path(self, d, fill, extra=""):
        self.add(f'<path d="{d}" fill="{self.paint(fill)}"{extra}/>')

    def stroke(self, d, color, width=1, extra=""):
        self.add(f'<path d="{d}" fill="none" stroke="{self.paint(color)}" stroke-width="{width}"{extra}/>')

    @contextmanager
    def group(self, gid):
        """Shapes drawn inside become a group that `use` can repeat elsewhere."""
        self.add(f'<g id="{gid}">')
        try:
            yield
        finally:
            self.add("</g>")

    def use(self, gid, dx, dy):
        self.add(f'<use xlink:href="#{gid}" transform="translate({dx},{dy})"/>')

    def ring(self, x, y, w, h):
        """A 1-pixel bevel: top and left edge in one fitted paint, bottom and right in another."""
        tl = self._fit("ring-tl", (x, y, w, h), lambda img: _fit().lin_ring(img, x, y, w, h, True))
        br = self._fit("ring-br", (x, y, w, h), lambda img: _fit().lin_ring(img, x, y, w, h, False))
        self.rect(x, y, w, h, br)
        self.rect(x, y, w - 1, h - 1, tl)
        return x + 1, y + 1, w - 2, h - 2

    def edge(self, x, y, w, h):
        """Only a top and left edge in a fitted paint (the bottom and right belong to the next ring)."""
        self.rect(x, y, w, h, self._fit("edge", (x, y, w, h), lambda img: _fit().lin_edge(img, x, y, w, h)))
        return x + 1, y + 1, w - 1, h - 1

    def bevel(self, x, y, w, h, n, face="lin"):
        """`n` nested rings and a fitted face inside them; returns the face rectangle."""
        for _ in range(n):
            x, y, w, h = self.ring(x, y, w, h)
        if face == "lin":
            self.rect(x, y, w, h, self.lin(x, y, w, h))
        return x, y, w, h

    def pix(self, x, y, w, h, bg, tol=24, skip=()):
        """Pixel art: the area's pixels that differ from `bg` by more than `tol`, as exact rectangles.

        `bg` is a colour, "lin" (a gradient fitted to the area), "col:X" (column X, row by row)
        or "all"; pixels inside the `skip` rectangles are left out.
        """
        self.add_pixels(self.pix_mask(x, y, w, h, bg, tol, skip))

    def pix_mask(self, x, y, w, h, bg, tol=24, skip=()):
        """The pixel art of `pix` without drawing it (for moving or recolouring)."""
        flat = tuple(v for r in skip for v in r)
        return self._fit("pix", (x, y, w, h, bg, tol, *flat), lambda img: _fit().pixels(img, x, y, w, h, bg, tol, skip))

    def pix_tiles(self, x, y, w, h, tile, tol, skip=()):
        """`pix` against a gradient fitted tile by tile: markings on a surface that is only locally even."""
        for ty in range(y, y + h, tile):
            for tx in range(x, x + w, tile):
                tw, th = min(tile, x + w - tx), min(tile, y + h - ty)
                inside = [r for r in skip if r[0] < tx + tw and r[0] + r[2] > tx and r[1] < ty + th and r[1] + r[3] > ty]
                self.pix(tx, ty, tw, th, "lin", tol, inside)

    def add_pixels(self, rects, dx=0, dy=0, color=None):
        by_color = {}
        for rx, ry, rw, rh, c in rects:
            by_color.setdefault(color or c, []).append(f"M{rx + dx} {ry + dy}h{rw}v{rh}h{-rw}z")
        for c, parts in by_color.items():
            self.add(f'<path d="{"".join(parts)}" fill="{c}"/>')

    def save(self, path):
        text = (
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}">\n'
            + ("<defs>\n" + "\n".join(self.defs) + "\n</defs>\n" if self.defs else "")
            + "\n".join(self.body)
            + "\n</svg>\n"
        )
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
