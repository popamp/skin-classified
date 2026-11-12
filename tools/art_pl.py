"""The playlist editor sheet: whole pieces, each tile one gradient, with its bevel lines and details on top."""
from art_main import backing
from art_parts import BLACK, MINI_TRANSPORT, boxed, face, label, lamp_button, small_button
from art_title import TITLE_COLOR, gold_rule, title

STRIPS = ((0, True), (21, False))  # title strips, focused and not
UPPER_SAMPLE = (27, 2)  # columns whose colours every piece of a title strip takes above the panel...
LOWER_SAMPLE = (60, 40)  # ...and in the five rows below it, so that the pieces join without a seam
BOTTOM_BUTTONS = (("Add", 14, 7), ("Del", 43, 7), ("Sel", 72, 7), ("Misc", 101, 6.2))  # word, x, height of its capitals
# Menu columns: normal, selected; words from the top
MENU = ((0, 23, ("Url", "Dir", "File")), (54, 77, ("All", "Crop", "File")), (104, 127, ("Inv", "No", "All")), (154, 177, ("Sort", "Inf", "Ops")), (204, 227, ("New", "Save", "Load")))
MENU_ROWS = ((114, 15, 126), (130, 18, 143), (149, 13, 159))  # top, rows, baseline of each item
MENU_BLUE = ((117, 11), (134, 11), (150, 11))
BAR_COLUMNS = ((48, 54), (100, 72), (150, 54), (200, 54), (250, 54))


def strip_ground(s, x, y, w):
    """The two gradients of a title strip's piece: above the panel and along its top."""
    s.vfill(x, y, w, 15, *UPPER_SAMPLE)
    s.vfill(x, y + 15, w, 5, *LOWER_SAMPLE)


def top_left(s, y):
    strip_ground(s, 0, y, 25)
    s.hfill(6, y + 16, 19, 3, y + 16, 3)
    gold_rule(s, 7, y + 5, 18)
    for x, top in ((0, 0), (1, 1), (2, 2), (3, 13), (4, 13), (5, 15)):
        s.line(x, y + top, 20 - top)
    s.rect(5, y + 13, 1, 2, s.color(5, y + 13, 1, 2))
    s.rect(6, y + 19, 4, 1, s.color(7, y + 18))


def title_tile(s, y, active):
    strip_ground(s, 26, y, 100)
    s.vfill(26, y + 5, 1, 6, 26)
    title(s, "PLAYLIST EDITOR", 30, 122, y, active)


def top_tile(s, y):
    strip_ground(s, 127, y, 25)
    gold_rule(s, 127, y + 5, 25)


def top_right(s, y):
    strip_ground(s, 153, y, 25)
    s.hfill(153, y + 16, 18, 3, y + 16, 3)
    s.rect(170, y + 19, 1, 1, s.color(170, y + 18))
    s.vfill(153, y + 5, 1, 6, 153)
    for x, top in ((171, 16), (172, 13), (173, 15), (174, 14), (175, 12), (176, 2), (177, 1)):
        s.line(x, y + top, 20 - top)
    s.path(f"M173 {y + 13}h2v1h-1v1h-1z", s.color(173, y + 13))
    boxed(s, 158, y + 4, "dash")
    boxed(s, 167, y + 4, "unshade", sample_dx=-9)


def mini_buttons(s):
    s.rect(52, 42, 19, 9, BLACK)
    small_button(s, 52, 43, 8, 7, "unshade", sample_dx=10)
    small_button(s, 62, 43, 8, 7, "dash")
    s.rect(52, 53, 17, 18, BLACK)
    face(s, 53, 54, 6, 16)
    face(s, 62, 54, 6, 16)


def shade_left(s, y):
    s.vfill(72, y, 25, 14, 85, 8)
    for x in (72, 73, 74):
        s.line(x, y + 1, 12)


def shade_right(s, y):
    s.vfill(99, y, 50, 14, 105, 10)
    s.hfill(120, y + 3, 9, 8, y + 7)
    s.rect(129, y + 2, 20, 11, BLACK)
    small_button(s, 131, y + 4, 8, 7, "dash")
    small_button(s, 140, y + 4, 8, 7, "unshade", sample_dx=-9)


def bottom_panel(s, x, w, holes):
    """The panel of a bottom piece: one gradient along it, which the middle tile continues."""
    s.rect(x, 73, w, 30, s.prof(x, 73, w, 30, "x", 8, holes))


def bottom_bevels(s, outline, sx, sw):
    """The bevels along a bottom piece, one gradient in a stepped outline: each ends where it turns up the side."""
    s.path(outline, s.vgrad(103, 7, sx, sw))


def button_with_word(s, x, text, cap=7):
    fx, fy, fw, fh = lamp_button(s, (x, 81, 22, 15), False)
    label(s, text, fx + fw / 2 - 0.5, 92, cap, "#1b1b1b")


def bottom_left(s):
    s.rect(6, 72, 5, 1, s.color(7, 72))
    s.rect(11, 72, 114, 1, s.lin(11, 72, 114, 1, "x"))
    bottom_panel(s, 6, 119, [(x, 81, 22, 15) for _, x, _ in BOTTOM_BUTTONS])
    s.hfill(0, 72, 6, 38, 85, 4)
    bottom_bevels(s, "M125 103H6V104H5V106H4V107H3V108H1V109H0V110H125Z", 60, 40)
    for text, x, cap in BOTTOM_BUTTONS:
        button_with_word(s, x, text, cap)


def mini_transport(s, x, y):
    s.rect(x, y, 57, 9, BLACK)
    for i, name in enumerate(MINI_TRANSPORT):
        small_button(s, x + 1 + 9 * i, y + 1, 8, 7, name)
    small_button(s, x + 46, y + 1, 8, 7, "eject")


def seek_arrows(s):
    """The two arrows at the corner of the playlist's bottom right: one dark outline, two light triangles."""
    s.path("M264.5 73L269 77.5V80.5L264.5 85L260 80.5V77.5Z", s.color(266, 78))
    s.path("M264.5 74L268.5 78H260.5ZM264.5 84L260.5 80H268.5Z", s.color(265, 77))


def bottom_right(s):
    s.hfill(265, 72, 11, 38, 88, 4)
    s.rect(126, 72, 143, 1, s.lin(126, 72, 143, 1, "x"))
    bottom_panel(s, 126, 143, [(130, 79, 94, 24), (232, 81, 22, 15), (258, 73, 11, 30)])
    bottom_bevels(s, "M126 103H271V105H272V106H273V107H274V108H276V110H126Z", 200, 40)
    s.ring(130, 79, 94, 12)
    s.rect(131, 80, 92, 10, BLACK)
    mini_transport(s, 130, 93)
    s.ring(189, 93, 35, 10)
    s.rect(190, 94, 33, 8, BLACK)
    s.rect(211, 96, 2, 1, "#ffffff")
    s.rect(211, 99, 2, 1, "#ffffff")
    button_with_word(s, 232, "List")
    seek_arrows(s)
    light, dark = s.color(267, 94), s.color(266, 96)
    for x0, y0, x1, y1 in ((268, 94, 260.5, 101.5), (268, 97.5, 264, 101.5)):
        s.stroke(f"M{x0 + 1} {y0}L{x1 + 1} {y1}", dark)
        s.stroke(f"M{x0} {y0}L{x1} {y1}", light)


def menu_item(s, x, y, rows, base, word, selected, blue_y, blue_h):
    if selected:
        s.rect(x, blue_y, 19, blue_h, "#000080")
    label(s, word, x + 10.5, base, 7, "#ffffff" if selected else "#000000")


def menu_ground(s, x, height):
    """The cream column behind a menu's items: a black cap, the ground, a white top line and a grey right one."""
    s.rect(x, 111, 22, height, BLACK)
    s.rect(x, 114, 21, height - 5, s.color(x + 4, 116))
    s.rect(x, 115, 20, 1, s.color(x + 4, 115))
    s.rect(x + 20, 115, 1, height - 6, s.color(x + 20, 120))


def menus(s):
    for normal, selected, words in MENU:
        for x, chosen in ((normal, False), (selected, True)):
            menu_ground(s, x, 54)
            for (top, rows, base), (blue_y, blue_h), word in zip(MENU_ROWS, MENU_BLUE, words):
                menu_item(s, x, top, rows, base, word, chosen, blue_y, blue_h)
    for x, chosen in ((54, False), (77, True)):  # the fourth item of the second column
        s.rect(x, 168, 22, 18, BLACK)
        s.rect(x, 171, 21, 14, s.color(x + 4, 174))
        if chosen:
            s.rect(x, 174, 20, 10, "#000080")
        label(s, "Misc", x + 10.5, 183, 7, "#ffffff" if chosen else "#000000")
    for x, height in BAR_COLUMNS:
        s.rect(x, 111, 3, height, BLACK)
        s.hfill(x, 114, 3, height - 7, 120)


def pledit(s):
    for y, active in STRIPS:
        top_left(s, y)
        title_tile(s, y, active)
        top_tile(s, y)
        top_right(s, y)
    s.vfill(179, 0, 25, 38, 185, 10)
    s.vfill(205, 0, 75, 38, 215, 30)
    s.hfill(0, 42, 25, 29, 45, 2)
    s.hfill(26, 42, 25, 29, 45, 2)
    mini_buttons(s)
    shade_left(s, 42)
    shade_left(s, 57)
    shade_right(s, 42)
    shade_right(s, 57)
    bottom_left(s)
    bottom_right(s)
    menus(s)
