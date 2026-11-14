"""The bar view's own pictures: a strip of the main window's metal with the wells its sprites sit in.

Whatever the main window has too (the transport's and the toggles' wells)
is drawn by the main window's own code in the main window's coordinates,
moved onto the bar, so both look the same and the fits are the same ones.
"""
from contextlib import contextmanager

from art_main import PLAY_MODE_WELLS, REPEAT_WELL, TOGGLE_WELLS, TRANSPORT_WELLS, wells
from art_parts import BLACK, face, glyph, socket
from art_sliders import panel_fit

BAR_H = 22
# The bar's fixed ends, and the narrowest bar
BAR_LEFT, BAR_RIGHT, BAR_MIN = 322, 227, 640
# The title bar's buttons a pixel larger, in a black box, so they sit in the middle of the bar
BAR_BUTTON = 10
# Where the main window's transport row (its wells start at 14, 86) goes on the bar
TRANSPORT_AT = (2, -86)
# Where the main window's EQ and PL wells, and its shuffle and repeat wells, go on the bar
TOGGLES_AT = (-137, -53)
PLAY_MODES_AT = (-31, -86)
# The display: its well from x, the clock's colon from the clock's left
DISPLAY_X = 163
CLOCK, COLON = (178, 4), (36, 4, 7)
# The position slider's groove under the title, on the display
GROOVE_Y = 14


@contextmanager
def moved(s, dx, dy):
    """Draws in the main window's coordinates, `dx`, `dy` away on the bar."""
    s.add(f'<g transform="translate({dx} {dy})">')
    try:
        yield
    finally:
        s.add("</g>")


def first(paint):
    """A flat colour from a fitted paint."""
    if isinstance(paint, str):
        return paint
    return paint["solid"] if "solid" in paint else paint["stops"][0][1]


def colours(s):
    """The bar's colours from the main window: its two outer bevels, panel and display rims."""
    with s.source(ref="main", absolute=True):
        outer, inner = s.ring_paints(0, 0, 275, 116), s.ring_paints(1, 1, 273, 114)
        rims = {k: first(s.color(*at)) for k, at in (("top", (150, 20)), ("left", (10, 40)), ("bottom", (50, 67)), ("right", (265, 30)))}
        panel = panel_fit(s)["stops"][7][1]  # the panel's colour round the volume slider
    return [first(p) for p in (*outer, *inner)], panel, rims


def body(s, x, w):
    """The metal across the bar: the window's two outer bevels top and bottom, the panel between."""
    (tl0, br0, tl1, br1), panel, _ = colours(s)
    s.rect(x, 0, w, BAR_H, panel)
    for y, c in ((0, tl0), (1, tl1), (BAR_H - 2, br1), (BAR_H - 1, br0)):
        s.rect(x, y, w, 1, c)


def display(s, x, w, left=False, right=False):
    """The display's well: dark rim at the top and left, light at the bottom and right."""
    _, _, rims = colours(s)
    s.rect(x, 1, w, BAR_H - 2, rims["bottom"])
    s.rect(x, 1, w, 1, rims["top"])
    if right:
        s.rect(x + w - 1, 2, 1, BAR_H - 3, rims["right"])
    if left:
        s.rect(x, 1, 1, BAR_H - 3, rims["left"])
    s.rect(x + left, 2, w - left - right, BAR_H - 4, BLACK)


def left(s):
    body(s, 0, BAR_LEFT)
    with moved(s, *TRANSPORT_AT):
        wells(s, TRANSPORT_WELLS)
    display(s, DISPLAY_X, BAR_LEFT - DISPLAY_X, left=True)
    cx, cy = CLOCK
    dx, *rows = COLON
    for y in rows:
        s.rect(cx + dx, cy + y, 3, 1, "#ffffff")


def mid(s):
    body(s, 0, 8)
    display(s, 0, 8)
    with s.source(ref="posbar", absolute=True):
        s.rect(0, GROOVE_Y, 8, 2, s.prof(1, 3, 245, 4, "x", 8)["stops"][4][1])


def right(s):
    body(s, 0, BAR_RIGHT)
    display(s, 0, 4, right=True)
    with moved(s, *TOGGLES_AT):
        for frame, _ in TOGGLE_WELLS:
            socket(s, frame)
    with moved(s, *PLAY_MODES_AT):
        for frame, *_ in PLAY_MODE_WELLS:
            socket(s, frame)
        socket(s, REPEAT_WELL)


# The title bar's buttons the bar has: their place in the titlebar sheet (normal, pressed) and where their face is measured
BUTTONS = (("menu", (0, 1), (0, 10), 0), ("close", (19, 1), (19, 10), -9))


def buttons(s):
    """Main Menu and Close side by side, the pressed ones under them: the title bar's faces, a row taller."""
    b = BAR_BUTTON
    for i, (name, *faces, sample_dx) in enumerate(BUTTONS):
        for row, (fx, fy) in enumerate(faces):
            x, y = b * i, b * row
            s.rect(x, y, b, b, BLACK)
            s.add(f'<g transform="translate({x + 1} {y + 1}) scale(1 {8 / 7:.6f}) translate({-fx} {-fy})">')
            with s.source(ref="titlebar", dx=sample_dx, absolute=True):
                face(s, fx, fy, 8, 7)
            s.add("</g>")
            glyph(s, name, x + 1, y + 1.5)


PICTURES = {"left": (BAR_LEFT, BAR_H, left), "mid": (8, BAR_H, mid), "right": (BAR_RIGHT, BAR_H, right), "buttons": (2 * BAR_BUTTON, 2 * BAR_BUTTON, buttons)}
