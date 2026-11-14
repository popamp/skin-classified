"""The parts every window is built from: frames, cream buttons, lamps, icons and small labels."""
from lettering import centred, spanned

BLACK = "#000000"
RAISED_INK, PRESSED_INK = "#0e0e0e", "#101010"

# Icons of the transport buttons, engraved, as seen in a 22 x 18 button: closed outlines (corner points), each
# drawn whole in the light ink, its top and left sides over it in the dark one
def box(x0, y0, x1, y1):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


TRANSPORT = {
    "prev": (box(6.5, 4.5, 8.5, 13.5), ((10.5, 8.5), (14.5, 4.5), (15.5, 4.5), (15.5, 13.5), (14.5, 13.5), (10.5, 9.5))),
    "play": (((6.5, 4.5), (7.5, 4.5), (15.5, 8.5), (15.5, 9.5), (7.5, 13.5), (6.5, 13.5)),),
    "pause": (box(5.5, 4.5, 8.5, 13.5), box(12.5, 4.5, 15.5, 13.5)),
    "stop": (box(6.5, 4.5, 15.5, 13.5),),
    "next": (((6.5, 4.5), (7.5, 4.5), (11.5, 8.5), (11.5, 9.5), (7.5, 13.5), (6.5, 13.5)), box(13.5, 4.5, 15.5, 13.5)),
    "eject": (((5.5, 8.5), (10.5, 3.5), (15.5, 8.5)), box(5.5, 10.5, 15.5, 12.5)),
}
STOP_DARK, STOP_LIGHT = (6, 8), (15, 8)  # where the stop button's icon shows its two inks
PRESS_SHIFT = 1  # a pressed icon sits this much lower and to the right

# Glyphs of the small buttons, on an 8 x 7 face: path data, drawn filled ("f") or as a line ("s")
GLYPHS = {
    "menu": ("f", "M1 2.5L2.5 1L4 2.5ZM1 3h6v1H1zM4 4.5L5.5 6L7 4.5Z"),
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

# The repeat icon in its 23 x 11 frame: a circle open at the bottom left, and the arrowhead its end points into
LOOP = ("M11 5A2.5 2.5 0 1 1 13.5 7.5", "M13 6.5L12 7.5L13 8.5")
# A line a little wider than a pixel, so the curve keeps the bars' black where it crosses pixels
LOOP_STROKE = 1.4


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
    at = f' transform="translate({x + shift} {y + shift})"'
    shapes = TRANSPORT[name]
    s.stroke("".join(outline(p) for p in shapes), inks[1], 1, at)
    s.stroke("".join(lit_from_above(p) for p in shapes), inks[0], 1, at)


def outline(points):
    return "M" + "L".join(f"{x:g} {y:g}" for x, y in points) + "Z"


def lit_from_above(points):
    """The sides of an outline facing up or left, as lines a half pixel short at their open ends, so the light ink shows the corners."""
    return "".join(run_path(points, r) for r in runs(facing_up(points)))


def facing_up(points):
    """For each side of an outline (from a point to the next), whether it faces up, or left when it stands upright."""
    n = len(points)
    sides = [(points[i], points[(i + 1) % n]) for i in range(n)]
    turn = 1 if sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in sides) > 0 else -1
    normals = [(turn * (y1 - y0), turn * (x0 - x1)) for (x0, y0), (x1, y1) in sides]
    return [ny < 0 or (ny == 0 and nx < 0) for nx, ny in normals]


def runs(flags):
    """The runs of set flags round a closed outline, each a list of indices."""
    n = len(flags)
    start = next(i for i in range(n) if flags[i] and not flags[i - 1])
    found, run = [], []
    for i in ((start + k) % n for k in range(n)):
        if flags[i]:
            run.append(i)
        elif run:
            found, run = found + [run], []
    return found + ([run] if run else [])


def run_path(points, run):
    n = len(points)
    line = [points[i] for i in run] + [points[(run[-1] + 1) % n]]
    line[0], line[-1] = toward(line[0], line[1]), toward(line[-1], line[-2])
    return "M" + "L".join(f"{x:g} {y:g}" for x, y in line)


def toward(a, b, d=0.5):
    (ax, ay), (bx, by) = a, b
    length = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
    return round(ax + (bx - ax) * d / length, 3), round(ay + (by - ay) * d / length, 3)


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
