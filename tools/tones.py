"""Colour sets: the metal's greys get names, and each set gives the names its own colours.

The theme is blue-grey metal with cream buttons, gold rules and a black
display. A set changes only the metal: the greys of the metal's hue and the
neutral greys, but not pure black or white, which the display and the
lettering are drawn in. A picture keeps its colours and marks the metal's
with a class (`tone-<lightness in thousandths>`), which a set's style sheet
overrides.
"""
import colorsys
import re

from art_title import TITLE_COLOR

FIRST_SET = "Silver"
# The metal's hue and how far from grey it goes; the cream is 20..40 degrees
METAL_HUE, METAL_SATURATION = (220, 290), 0.25
NEUTRAL = 0.02
# (name, hue in degrees, saturation added, lightness as a function of the theme's)
OTHER_SETS = (
    ("Graphite", 230, -0.05, lambda l: 0.06 + 0.5 * l),
    ("Olive", 75, 0.12, lambda l: l * 0.92),
    ("Bronze", 28, 0.18, lambda l: l * 0.92),
)
# Lettering in the metal's hue: an unfocused window's title, which stays readable on any set
LETTERING = set(TITLE_COLOR.values())
COLOUR = re.compile(r'\b(fill|stroke|stop-color)="(#[0-9a-f]{6})"')
SUFFIX = {"fill": "", "stroke": "-stroke", "stop-color": "-stop"}


def hls(colour):
    return colorsys.rgb_to_hls(*(int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5)))


def metal(colour):
    """Whether a colour is the metal's: a grey of its hue or a neutral one, but not pure black or white or lettering."""
    h, l, s = hls(colour)
    if colour in LETTERING or l in (0, 1):
        return False
    return s <= NEUTRAL or (METAL_HUE[0] <= h * 360 <= METAL_HUE[1] and s <= METAL_SATURATION)


def hexc(rgb):
    return "#%02x%02x%02x" % tuple(round(v * 255) for v in rgb)


class Tones:
    """The metal's greys met so far, as name by colour."""

    def __init__(self):
        self.names = {}

    def name(self, colour):
        """The name a colour of the metal has in the sets, None for any other colour."""
        if not metal(colour):
            return None
        if colour not in self.names:
            base = f"tone-{round(hls(colour)[1] * 1000)}"
            taken = set(self.names.values())
            self.names[colour] = next(n for n in (base, *(f"{base}{c}" for c in "bcdefgh")) if n not in taken)
        return self.names[colour]

    def named(self, colour):
        """A colour for skin.toml: its name if a set changes it."""
        return self.name(colour) or colour

    def mark(self, svg):
        """The SVG with a class on every element painted in the metal's colours."""

        def tag(m):
            classes = [f"{n}{SUFFIX[attr]}" for attr, c in COLOUR.findall(m.group(0)) if (n := self.name(c))]
            return m.group(0) if not classes else f'{m.group(1)} class="{" ".join(classes)}"{m.group(2)}'

        return re.sub(r"(<\w+)([^>]*>)", tag, svg)

    def sets(self):
        """The [colors] tables: the first set as the theme is, the others in their hue."""
        greys = sorted(self.names.items(), key=lambda g: (hls(g[0])[1], g[1]))
        lines = [f"[colors.{FIRST_SET}]", *(f'{name} = "{colour}"' for colour, name in greys)]
        for set_name, hue, more, light in OTHER_SETS:
            lines += ["", f"[colors.{set_name}]"]
            for colour, name in greys:
                _, l, s = hls(colour)
                rgb = colorsys.hls_to_rgb(hue / 360, min(1, light(l)), max(0, min(1, s + more)))
                lines.append(f'{name} = "{hexc(rgb)}"')
        return lines + [""]
