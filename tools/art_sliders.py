"""Sliders (volume, balance, position) and the small pixel-font sheets."""

CYAN = "#00c6ff"
FRAMES, FRAME_H = 28, 15  # volume and balance: 28 frames, 14 rows each and a spare row


def exact(s):
    """Pixel fonts and lamps: every pixel as it is (they are drawn on whole pixels at any size)."""
    s.pix(0, 0, s.w, s.h, CYAN, 0)


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


def metal(s, x, y, w, h, skip=(), n=10):
    s.rows(x, y, w, h, n, skip)


def slider_frames(s, x, w, gx, gw):
    """28 identical frames of the volume or balance slot (at `gx`, `gw` wide): the first, repeated."""
    with s.group("frame"):
        metal(s, x, 0, w, 14, [(gx, 3, gw + 1, 8)])
        groove(s, gx, 3, gw, 7)
    for i in range(1, FRAMES):
        s.use("frame", 0, FRAME_H * i)
    s.pix(0, 422, 29, 11, CYAN, 0)  # thumbs: pressed, normal


def volume(s):
    slider_frames(s, 0, 68, 0, 64)


def balance(s):
    slider_frames(s, 8, 39, 9, 37)


def posbar(s):
    """The position bar's flat slot (exact end columns, one gradient per row) and its two thumbs."""
    s.cols(0, 0, 2, 10)
    s.rows(2, 0, 243, 10, 16)
    s.cols(245, 0, 3, 10)
    s.pix(248, 0, 59, 10, CYAN, 0)
