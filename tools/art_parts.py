"""The parts every window is built from: frames, cream buttons, lamps, icons and small labels."""
from lettering import centred, spanned

BLACK = "#000000"
RAISED_INK, PRESSED_INK = "#0e0e0e", "#101010"

# Icons of the transport buttons, engraved: (dark lines, light lines), as seen in a 22 x 18 button
TRANSPORT = {
    "prev": ("M6.5 13V4.5H8.5M15.5 4.5H14.5L10.5 8.5", "M6.5 13.5H8.5V5M10.5 9.5L14.5 13.5H15.5V5"),
    "play": ("M6.5 13V4.5H7.5L15.5 8.5", "M6.5 13.5H7.5L15.5 9.5"),
    "pause": ("M5.5 13V4.5H8.5M12.5 13V4.5H15.5", "M5.5 13.5H8.5V5M12.5 13.5H15.5V5"),
    "stop": ("M6.5 13V4.5H15.5", "M6.5 13.5H15.5V5"),
    "next": ("M6.5 13V4.5H7.5L11.5 8.5M13.5 13V4.5H15.5", "M6.5 13.5H7.5L11.5 9.5M13.5 13.5H15.5V5"),
    "eject": ("M6.5 7.5L10.5 3.5L14.5 7.5M5.5 12V10.5H15.5", "M5.5 8.5H15.5M5.5 12.5H15.5V11"),
}
STOP_DARK, STOP_LIGHT = (6, 8), (15, 8)  # where the stop button's icon shows its two inks
PRESS_SHIFT = 1  # a pressed icon sits this much lower and to the right

# Glyphs of the small buttons, on an 8 x 7 face: path data, drawn filled ("f") or as a line ("s")
GLYPHS = {
    "menu": ("s", "M1.5 2.5L2.5 1.5L3.5 2.5M1 3.5H7M4.5 4.5L5.5 5.5L6.5 4.5"),
    "shade": ("f", "M1 2H6L3.5 5Z"),
    "min": ("f", "M2 3h3v1H2z"),
    "close": ("s", "M1.4 1.4L5.6 5.6M5.6 1.4L1.4 5.6"),
    "dash": ("f", "M2 3h4v1H2z"),
    "unshade": ("f", "M1 1h5v2H2v2h5v1H1zM4 3h3v2H4z"),
    "prev": ("f", "M2 1h1v5H2zM6 1v5L3 3.5Z"),
    "play": ("f", "M3 1v5L6 3.5Z"),
    "pause": ("f", "M3 2h1v3H3zM5 2h1v3H5z"),
    "stop": ("f", "M3 2h3v3H3z"),
    "next": ("f", "M5 1h1v5H5zM2 1v5L5 3.5Z"),
    "eject": ("f", "M1 3.9L3.5 1L6 3.9ZM1 5h5v1H1z"),
}
GLYPH_STROKE = 1.2
MINI_TRANSPORT = ("prev", "play", "pause", "stop", "next")

LOOP = "M14.5 6.5V5.5L15.5 4.5H17.5L19.5 6.5V7.5L18.5 8.5M17.5 9.5H15M13 7.5H15.5M13.5 8V9.5"


def face(s, x, y, w, h):
    """A button's face: one gradient, fitted to the area's pixels (markings on it do not count)."""
    s.rect(x, y, w, h, s.lin(x, y, w, h))


def cream_button(s, x, y, w, h):
    """A raised cream button: an outer top-left edge, two bevel rings and the face."""
    face(s, *s.ring(*s.ring(*s.edge(x, y, w, h))))


def cream_button_down(s, x, y, w, h, top=1):
    """The pressed button: black top-left (`top` rows), two dark rings and a darker face."""
    s.rect(x, y, w, h, BLACK)
    face(s, *s.ring(*s.ring(x + 1, y + top, w - 1, h - top)))


def lamp_button(s, frame, pressed):
    """A cream toggle in a black frame: two cream bevels (three when pressed) and the face. Returns the face."""
    r = s.ring(*s.ring(*frame))
    if pressed:
        r = s.ring(*r)
    face(s, *r)
    return r


def socket(s, frame):
    """The sunken rim round a framed button."""
    x, y, w, h = frame
    s.ring(x - 1, y - 1, w + 2, h + 2)


def lamp(s, x, y, width):
    """An inset indicator: dark top-left, light bottom-right, its light `width` wide."""
    s.rect(x, y, width + 2, 4, s.color(x + width + 1, y + 1))
    s.rect(x, y, width + 1, 3, s.color(x, y))
    s.rect(x + 1, y + 1, width, 2, s.color(x + 1, y + 1, width, 2))


def transport_icon(s, name, x, y, inks, shift=0):
    dark, light = TRANSPORT[name]
    at = f' transform="translate({x + shift} {y + shift})"'
    s.stroke(dark, inks[0], 1, at)
    s.stroke(light, inks[1], 1, at)


def transport_inks(s, stop_x, y, shift=0):
    """The two inks of the icons in a row of buttons, read off its stop button (`shift`: where a pressed icon moved)."""
    return s.color(stop_x + STOP_DARK[0] + shift, y + STOP_DARK[1] + shift), s.color(stop_x + STOP_LIGHT[0] + shift, y + STOP_LIGHT[1] + shift)


def glyph(s, name, x, y, ink=BLACK):
    kind, d = GLYPHS[name]
    at = f' transform="translate({x} {y})"'
    if kind == "f":
        s.path(d, ink, at)
    else:
        s.stroke(d, ink, GLYPH_STROKE, at)


def small_button(s, x, y, w, h, name, ink=BLACK, sample_dx=0):
    """A little window button: a face and its glyph.

    A big glyph leaves too little face to fit: `sample_dx` measures the face on the neighbouring button instead.
    """
    with s.source(dx=sample_dx):
        face(s, x, y, w, h)
    glyph(s, name, x, y, ink)


def boxed(s, x, y, name, w=8, ink=BLACK, sample_dx=0):
    """A little button in the black box it sits in on a strip."""
    s.rect(x - 1, y - 1, w + 2, 9, BLACK)
    small_button(s, x, y, w, 7, name, ink, sample_dx)


def label(s, text, cx, baseline, cap, ink=BLACK, weight="Regular"):
    s.path(centred(text, cx, baseline, cap, weight), ink)


def span_label(s, text, left, right, baseline, cap, ink=BLACK, weight="Bold"):
    s.path(spanned(text, left, right, baseline, cap, weight), ink)


def ribbed_thumb(s, x, y, w, h, ribs, rib_h, ink):
    """A slider thumb: a face and vertical ribs at the columns `ribs`, centred on its height."""
    face(s, x, y, w, h)
    top = y + (h - rib_h) // 2
    for r in ribs:
        s.rect(x + r, top, 1, rib_h, ink)


def window_frame(s, top):
    """The window's edge: seven concentric bevel rings, as many whole rectangles; the upper four start below the title."""
    for d in range(7):
        y = d if d < 3 else top - 7 + d
        s.ring(d, y, 275 - 2 * d, 116 - d - y)


def resize_grip(s):
    """Two light diagonal grooves with dark shadows in the bottom-right corner."""
    light, dark = s.color(266, 100), s.color(266, 101)
    for x0, y0, x1, y1 in [(267, 99.5, 258.5, 108), (267, 103.5, 262.5, 108)]:
        s.stroke(f"M{x0 + 1} {y0}L{x1 + 1} {y1}", dark)
        s.stroke(f"M{x0} {y0}L{x1} {y1}", light)
