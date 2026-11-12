"""Title bars: one gradient strip, gold rules, the window's name in vector lettering and whole little buttons."""
from art_parts import BLACK, MINI_TRANSPORT, boxed, face, glyph, label, ribbed_thumb, small_button
from lettering import spanned

CYAN = "#00c6ff"  # unused parts of a reference sheet
X0 = 27  # left edge of the strips in the titlebar sheet
W = 275
NAME_W = 42  # ink width of POPAMP
TITLE_COLOR = {True: "#ffffff", False: "#a8a8ad"}  # focused window, unfocused window
TITLE_SHADOW = ' transform="translate(0.6 0.8)" opacity="0.45"'
WINDOW_BUTTONS = ((245, "shade", 7, 0), (255, "min", 7, 0), (265, "close", 8, -10))  # x, glyph, width, where to measure the face
STRIP_SAMPLE = 17  # a column free of rules and lettering


def title(s, text, left, right, y, active=True):
    """`text` with its ink from `left` to `right`, on rows 4..10 of the strip at `y`, over a soft shadow."""
    d = spanned(text, left, right, y + 11)
    s.path(d, BLACK, TITLE_SHADOW)
    s.path(d, TITLE_COLOR[active])


def name(s, cx, y, active=True):
    """POPAMP centred on `cx`."""
    title(s, "POPAMP", cx - NAME_W / 2, cx + NAME_W / 2, y, active)


def gold_rule(s, x, y, length):
    """The double gold rule with the shadow under it: one rectangle, one gradient."""
    s.vfill(x, y, length, 6, x + length // 2, 8)


def strip(s, x0, y, h, sample=STRIP_SAMPLE):
    """The strip's metal in one gradient, with the three bevel lines at each end drawn over it."""
    s.vfill(x0, y, W, h, x0 + sample, 2)
    for d in range(3):
        s.line(x0 + d, y + d, h - d)
        s.line(x0 + W - 1 - d, y + d, h - d)


def window_buttons(s, x0, y):
    for x, glyph_name, w, sample_dx in WINDOW_BUTTONS:
        boxed(s, x0 + x, y + 4, glyph_name, w, sample_dx=sample_dx)


def main_strip(s, y, active, h=14, x0=X0):
    strip(s, x0, y, h)
    for gx, gl in ((19, 93), (163, 80)):
        gold_rule(s, x0 + gx, y + 5, gl)
    boxed(s, x0 + 6, y + 4, "menu")
    window_buttons(s, x0, y)
    name(s, x0 + 137, y, active)


def shade_strip(s, y, active):
    strip(s, X0, y, 13 if y == 29 else 14)
    boxed(s, X0 + 6, y + 4, "menu")
    name(s, X0 + 44.5, y, active)
    s.ring(X0 + 78, y + 2, 82, 11)  # song title display
    s.rect(X0 + 79, y + 3, 80, 9, BLACK)
    s.path(f"M{X0 + 144} {y + 6}h2v1h-2zM{X0 + 144} {y + 8}h2v1h-2z", "#ffffff")  # the clock's colon
    s.rect(X0 + 166, y + 3, 72, 9, BLACK)  # the mini transport's bay
    for i, glyph_name in enumerate(MINI_TRANSPORT):
        small_button(s, X0 + 168 + 9 * i, y + 4, 8, 7, glyph_name)
    small_button(s, X0 + 215, y + 4, 9, 7, "eject")
    s.ring(X0 + 225, y + 3, 19, 9)  # position bar slot
    s.rect(X0 + 226, y + 4, 17, 7, s.lin(X0 + 226, y + 4, 17, 7))
    window_buttons(s, X0, y)


def loose_buttons(s):
    """The separate button sprites at the sheet's left: normal row and pressed row."""
    s.rect(0, 0, X0, 44, BLACK)
    for y in (1, 10):
        small_button(s, 0, y, 8, 7, "menu")
        small_button(s, 10, y, 7, 7, "shade")
        small_button(s, 19, y, 8, 7, "close", sample_dx=-9)
    for y in (19, 28):
        small_button(s, 1, y, 7, 7, "min")
        small_button(s, 10, y, 7, 7, "min")
    s.rect(0, 36, 17, 7, s.lin(0, 36, 17, 7))
    ribbed_thumb(s, 17, 36, 9, 7, (2, 5, 8), 5, s.color(19, 39))


CLUTTER = ((1, "O", 9), (9, "A", 17), (17, "I", 25), (25, "D", 33), (32, "V", 40))


def clutter_column(s, x, lit):
    """One column of the clutterbar's letters on black: grey, the `lit` one green."""
    for i, (_, letter, base) in enumerate(CLUTTER):
        ink = s.color(309, 47) if i == lit else s.color(309, 3)
        label(s, letter, x + 5.5, base + 44 if lit is not None else base, 6, ink, "Bold")


def clutterbar(s):
    s.rect(304, 0, 40, 87, BLACK)
    s.rect(304, 0, 1, 87, s.color(304, 20))
    clutter_column(s, 304, None)
    for k in range(5):
        clutter_column(s, 304 + 8 * k, k)


def titlebar(s):
    loose_buttons(s)
    main_strip(s, 0, True, h=15)  # the reference has a spare row under the first strip
    main_strip(s, 15, False)
    shade_strip(s, 29, True)
    shade_strip(s, 42, False)
    # The reference's easter-egg strips carried a slogan; here they repeat the normal title.
    with s.source(dy=-57):
        main_strip(s, 57, True)
    with s.source(dy=-57):
        main_strip(s, 72, False)
    clutterbar(s)
