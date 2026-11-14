"""Lettering as outlines of Roboto: it scales with the window and needs no font at run time."""
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROBOTO = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-%s.ttf"
FONTS = {weight: TTFont(ROBOTO % weight) for weight in ("Bold", "Regular")}
KERN = {"PA": -1.0, "AY": -0.7, "YL": -0.3}  # pixels at title size; pairs whose shapes leave a hole at even spacing


def ntos(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Face:
    """One weight of the font, at capitals `cap` pixels high."""

    def __init__(self, weight, cap):
        font = FONTS[weight]
        self.glyphs, self.cmap = font.getGlyphSet(), font.getBestCmap()
        self.scale = cap / font["OS/2"].sCapHeight

    def ink(self, glyph):
        pen = BoundsPen(self.glyphs)
        self.glyphs[glyph].draw(pen)
        return pen.bounds

    def names(self, text):
        return [self.cmap[ord(c)] for c in text]

    def natural(self, text):
        """The ink's extent from the first letter's left edge, at the font's own spacing."""
        glyphs = self.names(text)
        advances = sum(self.glyphs[g].width for g in glyphs[:-1]) * self.scale
        return advances + (self.ink(glyphs[-1])[2] - self.ink(glyphs[0])[0]) * self.scale

    def draw(self, text, placed, baseline):
        path = SVGPathPen(self.glyphs, ntos=ntos)
        for glyph, x in placed:
            self.glyphs[glyph].draw(TransformPen(path, (self.scale, 0, 0, -self.scale, x, baseline)))
        return path.getCommands()


def spanned(text, left, right, baseline, cap=7, weight="Bold"):
    """Path data of `text` with its ink tracked evenly from `left` to `right`."""
    face = Face(weight, cap)
    glyphs = face.names(text)
    kerns = [KERN.get(text[i : i + 2], 0) for i in range(len(text) - 1)]
    tracking = (right - left - face.natural(text) - sum(kerns)) / (len(glyphs) - 1)
    pen, placed = left - face.ink(glyphs[0])[0] * face.scale, []
    for glyph, kern in zip(glyphs, kerns + [0]):
        placed.append((glyph, pen))
        pen += face.glyphs[glyph].width * face.scale + kern + tracking
    return face.draw(text, placed, baseline)


def centred(text, cx, baseline, cap, weight="Regular"):
    """Path data of `text` at the font's own spacing, its ink centred on `cx`."""
    face = Face(weight, cap)
    pen, placed = cx - face.natural(text) / 2 - face.ink(face.names(text)[0])[0] * face.scale, []
    for glyph in face.names(text):
        placed.append((glyph, pen))
        pen += face.glyphs[glyph].width * face.scale
    return face.draw(text, placed, baseline)


def spaced_like(text, model, left, right, cap=7, weight="Bold"):
    """Where `text` starts and ends, centred on `model`'s span, with the tracking `model` has there."""
    face = Face(weight, cap)
    kerned = lambda t: face.natural(t) + sum(KERN.get(t[i : i + 2], 0) for i in range(len(t) - 1))
    tracking = (right - left - kerned(model)) / (len(model) - 1)
    w = kerned(text) + tracking * (len(text) - 1)
    return (left + right - w) / 2, (left + right + w) / 2


def fitted_cap(text, width, cap, weight="Regular"):
    """The capital height, at most `cap`, at which `text` is no wider than `width`."""
    return min(cap, cap * width / Face(weight, cap).natural(text))
