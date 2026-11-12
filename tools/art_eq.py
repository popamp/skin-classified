"""The equalizer: window, buttons, slider bars and the shade strip."""
from art_main import backing
from art_parts import (BLACK, PRESSED_INK, RAISED_INK, boxed, face, glyph, label, lamp, lamp_button, resize_grip, ribbed_thumb, small_button, socket,
                       span_label, window_frame)
from art_sliders import groove
from art_title import STRIP_SAMPLE, WINDOW_BUTTONS, gold_rule, strip, title

GROOVES = [25] + [82 + 18 * i for i in range(10)]  # preamp and the ten bands, 7 wide, rows 39..98
FREQUENCIES = ("60", "170", "310", "600", "1K", "3K", "6K", "12K", "14K", "16K")
SCALES = [16, 35] + [73 + 18 * i for i in range(11)]  # the tick columns beside the sliders
LONG_TICKS = (43, 69, 95)
WHITE, YELLOW = "#ffffff", "#f3d357"
PANEL = (7, 16, 261, 93)
PANEL_HOLES = ((14, 18, 60, 14), (80, 15, 125, 23), (217, 18, 46, 14), (16, 36, 250, 72))
PANEL_STOPS = 10
BAR_TOP = 38  # the window row a slider bar sprite starts on
BUTTONS = {"ON": ((14, 19, 23, 11), 10, 18.5), "AUTO": ((40, 19, 32, 11), 10, 28)}
PRESETS_LABEL = (4, 37)


def panel_fit(s):
    """The window's panel: one vertical gradient down it."""
    x, y, w, h = PANEL
    with s.source(absolute=True):
        return s.prof(x, y, w, h, "y", PANEL_STOPS, PANEL_HOLES)


def eq_strip(s, y, h=14, active=True):
    """The EQUALIZER title strip."""
    strip(s, 0, y, h, 3)
    for gx, gl in ((5, 97), (174, 79)):
        gold_rule(s, gx, y + 5, gl)
    title(s, "EQUALIZER", 107, 169, y, active)
    boxed(s, 254, y + 4, "dash")
    boxed(s, 264, y + 4, "unshade", sample_dx=-10)


def graph(s):
    """The graph's cut-out: rim, black ground, the eleven band lines and the zero line."""
    s.ring(82, 16, 121, 21)
    s.rect(83, 17, 119, 19, BLACK)
    green = s.color(88, 22)
    s.path("".join(f"M{88 + 12 * i} 19h1v15h-1z" for i in range(10)), green)
    s.rect(86, 26, 113, 1, s.color(150, 26))


def toggle(s, frame, text, left, right, pressed):
    r = lamp_button(s, frame, pressed)
    lamp(s, frame[0] + 3, frame[1] + 3, 3)
    span_label(s, text, frame[0] + left, frame[0] + right, frame[1] + 8, 5, PRESSED_INK if pressed else RAISED_INK)
    return r


def presets(s, frame, pressed):
    lamp_button(s, frame, pressed)
    span_label(s, "PRESETS", frame[0] + PRESETS_LABEL[0], frame[0] + PRESETS_LABEL[1], frame[1] + 8, 5, PRESSED_INK if pressed else RAISED_INK)


def scales(s):
    """The tick marks beside every slider: one shape for the long ticks, one for the dots."""
    long_ticks = "".join(f"M{x} {y}h5v1h-5z" for x in SCALES for y in LONG_TICKS)
    dots = "".join(f"M{x + 1} {y}h2v1h-2z" for x in SCALES for y in range(45, 95, 2) if y not in LONG_TICKS)
    s.path(dots, s.color(36, 45))
    s.path(long_ticks, WHITE)


def captions(s):
    for text, base in (("+12 db", 42), ("+0 db", 71), ("-12 db", 101)):
        label(s, text, 56, base, 5, YELLOW, "Bold")
    span_label(s, "PREAMP", 17, 41, 108, 4.5, WHITE)
    for i, text in enumerate(FREQUENCIES):
        label(s, text, 85.5 + 18 * i, 108, 5, WHITE, "Bold")


def window(s):
    window_frame(s, 16)
    s.rect(*PANEL, panel_fit(s))
    eq_strip(s, 0)
    for text, (frame, left, right) in BUTTONS.items():
        socket(s, frame)
        toggle(s, frame, text, left, right, False)
    socket(s, (219, 19, 41, 11))
    presets(s, (219, 19, 41, 11), False)
    graph(s)
    for gx in GROOVES:
        groove(s, gx, 39, 7, 60, vertical=True)
    scales(s)
    captions(s)
    resize_grip(s)


def slider_bar(s, x, y):
    """One slider bar sprite (14 x 64): the window's own panel gradient round a vertical slot."""
    fit = panel_fit(s)
    _, y1, _, y2 = fit["lin"]
    s.rect(x, y, 14, 64, {"lin": [0, y1 + y - BAR_TOP, 0, y2 + y - BAR_TOP], "stops": fit["stops"]})
    groove(s, x + 3, y + 1, 7, 60, vertical=True)


def state_buttons(s):
    """ON and AUTO in all states, the little close and shade buttons."""
    backing(s, 10, 120, 240, 11)
    frames = [(10, 120), (36, 120), (69, 120), (95, 120), (128, 120), (154, 120), (187, 120), (213, 120)]
    for i, (x, y) in enumerate(frames):
        text, left, right = ("ON", 10, 18.5) if i % 2 == 0 else ("AUTO", 11, 28)
        toggle(s, (x, y, 23 if i % 2 == 0 else 32, 11), text, left, right, i >= 4)
    s.rect(0, 116, 9, 18, BLACK)
    small_button(s, 0, 117, 8, 7, "unshade", sample_dx=0)
    small_button(s, 0, 126, 8, 7, "dash")


def graph_sheet(s):
    """The graph's ground and its column of line colours."""
    s.rect(0, 294, 113, 19, BLACK)
    s.path("".join(f"M{2 + 12 * i} 294h1v19h-1z" for i in range(10)), s.color(2, 300))
    s.vfill(115, 294, 1, 19, 115)


def eqmain(s):
    window(s)
    state_buttons(s)
    eq_strip(s, 134, 15)
    eq_strip(s, 149, 15, active=False)
    with s.group("bar"):
        slider_bar(s, 13, 164)
    for row_y in (164, 229):
        for k in range(14):
            if (k, row_y) != (0, 164):
                s.use("bar", 15 * k, row_y - 164)
    for y in (164, 176):
        s.rect(0, y, 11, 11, BLACK)
        ribbed_thumb(s, 1, y + 1, 9, 9, (), 0, BLACK)
        s.path(f"M3 {y + 4}h5v1h-5zM3 {y + 6}h5v1h-5z", BLACK)
    backing(s, 224, 164, 44, 25)
    presets(s, (226, 165, 41, 11), False)
    presets(s, (226, 177, 41, 11), True)
    graph_sheet(s)


def eq_shade_strip(s, y):
    """The shaded equalizer: metal, gold rules, two slots for the little volume and balance bars."""
    strip(s, 0, y, 14, 3)
    for gx, gl in ((6, 53), (209, 44)):
        gold_rule(s, gx, y + 5, gl)
    for x, sy, w, h in ((61, 4, 98, 7), (164, 4, 43, 7)):
        s.rect(x, y + sy + h, w, 1, s.lin(x, y + sy + h, w, 1, "x"))  # light lower lip
        fx, fy, fw, fh = s.ring(x, y + sy, w, h)
        s.vfill(fx, fy, fw, fh, fx + 4, fw - 8)
    boxed(s, 254, y + 3, "dash")
    boxed(s, 264, y + 3, "unshade", sample_dx=-10)


def eq_ex(s):
    eq_shade_strip(s, 0)
    eq_shade_strip(s, 15)
    s.rect(0, 29, 24, 28, BLACK)
    ink = s.color(2, 33)
    for x in (1, 11):
        ribbed_thumb(s, x, 30, 9, 7, (1, 4, 7), 5, ink)
    for y in (39, 48):
        small_button(s, 2, y, 8, 7, "dash")
        small_button(s, 11, y, 8, 7, "unshade", sample_dx=-9)
