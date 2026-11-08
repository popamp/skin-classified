"""Title bars: metal strips with gold lines and the window's name as vector lettering."""
from lettering import title_path

CYAN = "#00c6ff"  # unused parts of a reference sheet
X0 = 27  # left edge of the strips in the titlebar sheet
W = 275
NAME_W = 42  # ink width of POPAMP
TITLE_COLOR = {True: "#ffffff", False: "#a8a8ad"}  # focused window, unfocused window
TITLE_SHADOW = ' transform="translate(0.6 0.8)" opacity="0.45"'


def title(s, text, left, right, y, active=True):
    """`text` with its ink from `left` to `right`, on rows 4..10 of the strip at `y`, over a soft shadow."""
    d = title_path(text, left, right, y + 11)
    s.path(d, "#000000", TITLE_SHADOW)
    s.path(d, TITLE_COLOR[active])


def name(s, cx, y, active=True):
    """POPAMP centred on `cx`."""
    title(s, "POPAMP", cx - NAME_W / 2, cx + NAME_W / 2, y, active)


def gold_lines(s, x, y, length):
    """The double gold rule: rows 0..4 from `y`, flat along its length, exact end columns."""
    for r in range(5):
        s.rect(x + 1, y + r, length - 2, 1, s.lin(x + 1, y + r, length - 2, 1, "x"))
    s.pix(x, y, 1, 5, "all")
    s.pix(x + length - 1, y, 1, 5, "all")


def strip_frame(s, y, skip, h=14, x0=X0):
    """The strip's metal: exact edge columns and one gradient per row in between.

    Rows 5..9 are almost all covered by gold and lettering, so they take the colours of rows 3..4.
    """
    s.cols(x0, y, 2, h)
    s.cols(x0 + W - 3, y, 3, h)
    skip = [(x0 + sx, y + sy, sw, sh) for sx, sy, sw, sh in skip]
    s.rows(x0 + 2, y, W - 5, h, 12, skip, lambda j: (y + 3, 2) if y + 5 <= j <= y + 9 else (j, 1))


def main_strip(s, y, active, h=14, x0=X0):
    gold = [(19, 93), (163, 80)]
    strip_frame(s, y, [(5, 3, 10, 9), (110, 4, 56, 7), (243, 3, 31, 9)] + [(gx, 5, gl, 5) for gx, gl in gold], h, x0)
    for gx, gl in gold:
        gold_lines(s, x0 + gx, y + 5, gl)
    s.pix(x0 + 5, y + 3, 10, 9, "all")  # menu button
    s.pix(x0 + 243, y + 3, 30, 9, "all")  # minimize, shade, close
    name(s, x0 + 137, y, active)


def shade_strip(s, y, active):
    strip_frame(s, y, [(5, 2, 10, 10), (20, 3, 52, 9), (77, 1, 84, 13), (161, 1, 112, 12)])
    s.pix(X0 + 5, y + 2, 10, 10, "all")  # menu button
    s.pix(X0 + 77, y + 1, 84, 13, f"col:{X0 + 75}", 12)  # song title display
    s.pix(X0 + 161, y + 1, 111, 12, f"col:{X0 + 160}", 12)  # mini buttons, position bar, window buttons
    name(s, X0 + 44.5, y, active)


def titlebar(s):
    s.pix(0, 0, X0, 44, CYAN, 0)  # loose buttons
    main_strip(s, 0, True, h=15)  # the reference has a spare row under the first strip
    main_strip(s, 15, False)
    shade_strip(s, 29, True)
    shade_strip(s, 42, False)
    # The reference's easter-egg strips carried a slogan; here they repeat the normal title.
    with s.source(dy=-57):
        main_strip(s, 57, True)
    with s.source(dy=-57):
        main_strip(s, 72, False)
    s.cols(X0 + W, 0, 1, 87)  # a spare column right of the strips
    s.pix(X0 + W + 1, 0, 344 - X0 - W - 1, 87, CYAN, 0)  # clutterbar
