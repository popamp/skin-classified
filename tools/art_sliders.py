"""Sliders (volume, balance, position) and the bitmap-font sheets."""
from art_parts import BLACK, ribbed_thumb

CYAN = "#00c6ff"
FRAMES, FRAME_H = 28, 15  # volume and balance: 28 frames, 14 rows each and a spare row
THUMB_RIBS = (4, 6, 8)
MAIN_PANEL = (7, 17, 261, 92)
MAIN_HOLES = ((10, 20, 256, 48), (100, 53, 170, 16), (14, 71, 252, 11), (14, 86, 118, 22), (134, 87, 25, 20), (161, 89, 107, 20))
PANEL_STOPS = 10


def panel_fit(s):
    """The main window's panel: one horizontal gradient across it."""
    x, y, w, h = MAIN_PANEL
    with s.source(ref="main", absolute=True):
        return s.prof(x, y, w, h, "x", PANEL_STOPS, MAIN_HOLES)


def panel_paint(s, shift):
    """The panel's gradient, with main window column `shift` moved to column 0."""
    fit = panel_fit(s)
    x1, _, x2, _ = fit["lin"]
    return {"lin": [x1 - shift, 0, x2 - shift, 0], "stops": fit["stops"]}


def exact(s):
    """The original's bitmap fonts and lamps: flat colours, one outlined shape per colour."""
    s.outlined(0, 0, s.w, s.h, CYAN)


def groove(s, x, y, w, h, vertical=False):
    """A sunken rounded slot: a light rim along its bottom and right, a dark shaded inside."""
    r = (w if vertical else h) / 2
    s.rrect(x + 1, y + 1, w, h, r, s.color(x + w // 2, y + h, 1, 1) if not vertical else s.color(x + w, y + h // 2, 1, 1))
    k = int(r) + 1
    if vertical:
        inside = s.prof(x, y + k, w, h - 2 * k, "x", w)
    else:
        inside = s.prof(x + k, y, w - 2 * k, h, "y", h)
    s.rrect(x, y, w, h, r, inside)


def slider_frames(s, x, w, gx, gw, on_main):
    """28 identical frames of the volume or balance slot (at `gx`, `gw` wide): the first, repeated.

    The metal is the main window's own panel gradient, moved to where the sprite sits (`on_main`: its x there).
    """
    with s.group("frame"):
        s.rect(x, 0, w, 14, panel_paint(s, on_main))
        groove(s, gx, 3, gw, 7)
    for i in range(1, FRAMES):
        s.use("frame", 0, FRAME_H * i)
    for fx, ink_col in ((0, 5), (15, 20)):  # thumbs: pressed, normal
        s.rect(fx, 422, 14, 11, BLACK)
        ribbed_thumb(s, fx + 1, 423, 12, 9, THUMB_RIBS, 5, BLACK)


def volume(s):
    slider_frames(s, 0, 68, 0, 64, 107)


def balance(s):
    slider_frames(s, 8, 39, 9, 37, 168)


def slot(s, x, y):
    """The position bar's flat slot, 248 wide: one gradient down it, the shaded floor, its dark and light ends."""
    s.vfill(x, y, 248, 10, x + 100)
    s.rect(x + 1, y + 3, 245, 4, s.prof(x + 1, y + 3, 245, 4, "x", 8))
    s.rect(x, y + 1, 1, 7, s.color(x, y + 3, 1, 4))
    s.rect(x + 246, y + 3, 1, 5, s.color(x + 246, y + 3, 1, 4))
    s.rect(x + 247, y + 2, 1, 7, s.color(x + 247, y + 3, 1, 4))


def posbar(s):
    slot(s, 0, 0)
    for x in (248, 278):  # thumbs: a frame and a recessed bar, in one gradient, with their end columns over it
        s.vfill(x, 0, 29, 10, x + 10, 8)
        s.hfill(x, 0, 4, 10, 4)
        s.hfill(x + 25, 0, 4, 10, 4)
