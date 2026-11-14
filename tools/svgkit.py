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

    def __init__(self, fits, ref, w, h, tones=None, origin=(0, 0)):
        """`tones` marks the metal's colours for the colour sets; `origin` is the drawing position at the picture's top left."""
        self.fits, self.ref, self.w, self.h = fits, ref, w, h
        self.tones, self.origin = tones, origin
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

    def _bands(self, sx, sy, sw, sh, axis):
        return self._fit("bands", (sx, sy, sw, sh, axis), lambda img: _fit().bands(img, sx, sy, sw, sh, axis))

    def vfill(self, x, y, w, h, sx, sw=1, sy=None):
        """One rectangle under one vertical gradient: the colours of `h` rows measured on columns `sx`..`sx + sw`."""
        self.rect(x, y, w, h, self.vgrad(y, h, sx, sw, sy))

    def vgrad(self, y, h, sx, sw=1, sy=None):
        """A vertical gradient over rows `y`..`y + h`: the colours measured on columns `sx`..`sx + sw`."""
        return {"lin": [0, y, 0, y + h], "stops": self._bands(sx, y if sy is None else sy, sw, h, "y")}

    def hfill(self, x, y, w, h, sy, sh=1, sx=None):
        """One rectangle under one horizontal gradient: the colours of `w` columns measured on rows `sy`..`sy + sh`."""
        stops = self._bands(x if sx is None else sx, sy, w, sh, "x")
        self.rect(x, y, w, h, {"lin": [x, 0, x + w, 0], "stops": stops})

    def line(self, x, y, h):
        """A one-pixel vertical bevel line."""
        self.rect(x, y, 1, h, self.lin(x, y, 1, h, "y"))

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

    def ring_paints(self, x, y, w, h):
        """The fitted paints of a bevel's top-left and bottom-right edges."""
        tl = self._fit("ring-tl", (x, y, w, h), lambda img: _fit().lin_ring(img, x, y, w, h, True))
        br = self._fit("ring-br", (x, y, w, h), lambda img: _fit().lin_ring(img, x, y, w, h, False))
        return tl, br

    def ring(self, x, y, w, h):
        """A 1-pixel bevel: top and left edge in one fitted paint, bottom and right in another."""
        tl, br = self.ring_paints(x, y, w, h)
        self.rect(x, y, w, h, br)
        self.rect(x, y, w - 1, h - 1, tl)
        return x + 1, y + 1, w - 2, h - 2

    def edge(self, x, y, w, h):
        """Only a top and left edge in a fitted paint (the bottom and right belong to the next ring)."""
        self.rect(x, y, w, h, self._fit("edge", (x, y, w, h), lambda img: _fit().lin_edge(img, x, y, w, h)))
        return x + 1, y + 1, w - 1, h - 1

    def outlined(self, x, y, w, h, bg):
        """Flat-coloured pixel art (the original's bitmap fonts) as one outlined shape per colour; `bg` is left out."""
        for colour, d in self._fit("outlines", (x, y, w, h, bg), lambda img: _fit().outlines(img, x, y, w, h, bg)):
            self.path(d, colour)

    def save(self, path):
        x0, y0 = self.origin
        text = (
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{self.w}" height="{self.h}" '
            f'viewBox="{x0} {y0} {self.w} {self.h}">\n'
            + ("<defs>\n" + "\n".join(self.defs) + "\n</defs>\n" if self.defs else "")
            + "\n".join(self.body)
            + "\n</svg>\n"
        )
        if self.tones:
            text = self.tones.mark(text)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
