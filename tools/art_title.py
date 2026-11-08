"""Title bars: metal strips with gold lines and the name POPAMP where the reference had its own name."""

CYAN = "#00c6ff"  # unused parts of a reference sheet
X0 = 27  # left edge of the strips in the titlebar sheet
W = 275

# Letters for POPAMP, taken from the reference's title lettering (rows 4..10 of a strip):
# (sheet, x of the first column, width) for the active strip; the inactive one is `INACTIVE_DY` lower.
GLYPHS = {
    "P": ("titlebar", 180, 7),
    "A": ("titlebar", 165, 6),
    "M": ("titlebar", 171, 9),
    "O": ("eqmain", 114, 7),  # the Q of EQUALIZER without its tail
}
GLYPH_BG = {"titlebar": 141, "eqmain": 104}  # a column of plain background beside the lettering
INACTIVE_Y = {"titlebar": 15, "eqmain": 149}
NAME = "POPAMP"


def name_width():
    return sum(GLYPHS[c][2] for c in NAME)


def name(s, cx, y, active=True):
    """POPAMP centred on `cx`, its letters' rows 4..10 drawn from `y + 4`."""
    x = round(cx - name_width() / 2)
    for c in NAME:
        sheet, gx, gw = GLYPHS[c]
        gy = 0 if active else INACTIVE_Y[sheet]
        with s.source(ref=sheet, dx=gx - x, dy=gy - y, absolute=True):
            rects = s.pix_mask(x, y + 4, gw, 7, f"col:{GLYPH_BG[sheet] - (gx - x)}", 14)
        s.add_pixels(rects)
        x += gw


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
