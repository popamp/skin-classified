"""Window titles as outlines of Roboto Bold: they scale with the window and need no font at run time."""
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT = TTFont("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf")
GLYPHS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
SCALE = 7 / FONT["OS/2"].sCapHeight  # capitals fill 7 whole rows of the strip, as in the classic lettering
KERN = {"PA": -1.0, "AY": -0.7, "YL": -0.3}  # pixels; the pairs whose shapes leave a hole at even spacing


def ntos(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _ink(glyph):
    pen = BoundsPen(GLYPHS)
    GLYPHS[glyph].draw(pen)
    return pen.bounds


def _layout(text, left, right):
    """The pen position of each letter so that the word's ink spans `left`..`right`, evenly tracked."""
    glyphs = [CMAP[ord(c)] for c in text]
    kerns = [KERN.get(text[i : i + 2], 0) for i in range(len(text) - 1)]
    advances = [GLYPHS[g].width * SCALE for g in glyphs[:-1]]
    first, last = _ink(glyphs[0])[0] * SCALE, _ink(glyphs[-1])[2] * SCALE
    natural = sum(advances) + sum(kerns) + last - first
    tracking = (right - left - natural) / (len(glyphs) - 1)
    pen, placed = left - first, []
    for glyph, advance, kern in zip(glyphs, advances + [0], kerns + [0]):
        placed.append((glyph, pen))
        pen += advance + kern + tracking
    return placed


def title_path(text, left, right, baseline):
    """SVG path data of `text`, its ink from `left` to `right`, standing on `baseline`."""
    path = SVGPathPen(GLYPHS, ntos=ntos)
    for glyph, x in _layout(text, left, right):
        GLYPHS[glyph].draw(TransformPen(path, (SCALE, 0, 0, -SCALE, x, baseline)))
    return path.getCommands()
