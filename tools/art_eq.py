"""The equalizer: window, buttons, slider bars and the shade strip."""
from art_main import lamp_button, socket
from art_sliders import groove
from art_title import gold_lines, strip_frame

CYAN = "#00c6ff"
GROOVES = [25] + [82 + 18 * i for i in range(10)]  # preamp and the ten bands, 7 wide, rows 39..98


def eq_strip(s, y, h=14):
    """The EQUALIZER title strip (its lettering kept as exact pixels)."""
    gold = [(5, 97), (174, 79)]
    strip_frame(s, y, [(102, 3, 72, 9), (254, 3, 19, 9)] + [(gx, 5, gl, 5) for gx, gl in gold], h, 0)
    for gx, gl in gold:
        gold_lines(s, gx, y + 5, gl)
    s.pix(102, y + 3, 72, 9, f"col:{103}", 14)
    s.pix(254, y + 3, 19, 9, "all")  # shade, close


def eq_sample_row(j):
    """Rows where scale marks or labels cover much of the metal take a clean neighbour's colours."""
    if j in (43, 69, 95):
        return j - 1, 1
    if 100 <= j <= 108:
        return 99, 1
    return j, 1


def window(s):
    eq_strip(s, 0)
    buttons = [((14, 19, 23, 11), False), ((40, 19, 32, 11), False), ((219, 19, 41, 11), False)]
    grooves = [(gx, 39, 8, 61) for gx in GROOVES]
    graph = (82, 16, 121, 21)
    skip = [(x - 1, y - 1, w + 2, h + 2) for (x, y, w, h), _ in buttons] + [graph] + grooves
    s.cols(0, 14, 10, 102)
    s.rows(10, 14, 255, 102, 16, skip, eq_sample_row)
    s.cols(265, 14, 10, 102)
    s.pix_tiles(10, 36, 255, 74, 24, 26, grooves)  # scales, dB and frequency labels, resize grip
    for f, pressed in buttons:
        socket(s, f)
        lamp_button(s, f, pressed)
    s.pix(*graph, "all")
    for gx in GROOVES:
        groove(s, gx, 39, 7, 60, vertical=True)


def slider_bar(s, x, y):
    """One slider bar sprite (14 x 64): metal round a vertical slot."""
    s.rows(x, y, 14, 64, 6, [(x + 3, y + 1, 8, 61)])
    groove(s, x + 3, y + 1, 7, 60, vertical=True)


def eqmain(s):
    window(s)
    # ON and AUTO in all states, close and shade buttons
    frames = [(10, 120), (36, 120), (69, 120), (95, 120), (128, 120), (154, 120), (187, 120), (213, 120)]
    frames = [(x, y, 23 if i % 2 == 0 else 32, 11) for i, (x, y) in enumerate(frames)]
    for i, f in enumerate(frames):
        lamp_button(s, f, i >= 4)
    s.pix(0, 116, 275, 18, CYAN, 0, frames)
    eq_strip(s, 134, 15)
    eq_strip(s, 149, 15)
    with s.group("bar"):
        slider_bar(s, 13, 164)
    for row_y in (164, 229):
        for k in range(14):
            if (k, row_y) != (0, 164):
                s.use("bar", 15 * k, row_y - 164)
    s.pix(0, 164, 13, 130, CYAN, 0)  # slider thumbs
    for f, pressed in [((226, 165, 41, 11), False), ((226, 177, 41, 11), True)]:  # presets
        lamp_button(s, f, pressed)
    s.pix(224, 164, 51, 26, CYAN, 0, [(226, 165, 41, 11), (226, 177, 41, 11)])
    s.pix(0, 294, 275, 21, CYAN, 0)  # graph background and its line colours


def eq_shade_strip(s, y):
    """The shaded equalizer: metal, gold rules, two slots for the little volume and balance bars."""
    gold = [(6, 53), (209, 44)]
    slots = [(61, 4, 98, 7), (164, 4, 43, 7)]
    skip = [(gx, 5, gl, 5) for gx, gl in gold] + [(x, sy, w, h + 1) for x, sy, w, h in slots] + [(253, 2, 21, 10)]
    strip_frame(s, y, skip, 14, 0)
    for gx, gl in gold:
        gold_lines(s, gx, y + 5, gl)
    for x, sy, w, h in slots:
        s.rect(x, y + sy + h, w, 1, s.lin(x, y + sy + h, w, 1, "x"))  # light lower lip
        fx, fy, fw, fh = s.ring(x, y + sy, w, h)
        s.rect(fx, fy, fw, fh, s.prof(fx + 4, fy, fw - 8, fh, "y", fh))
    s.pix(253, y + 2, 21, 10, "all")  # shade, close


def eq_ex(s):
    eq_shade_strip(s, 0)
    eq_shade_strip(s, 15)
    s.pix(0, 29, s.w, s.h - 29, CYAN, 0)  # small slider thumbs and the strip's buttons
