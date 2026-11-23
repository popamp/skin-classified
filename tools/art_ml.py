"""The media library's own pictures: its name on the title bar and its menu button, drawn as the playlist's are."""
from art_bar import COLON, colours, moved
from art_main import TRANSPORT_WELLS, wells
from art_parts import BLACK, small_button, span_label
from art_pl import STRIPS, TITLE_SPAN, TITLE_TEXT, button_with_word, grip, title_tile, top_right
from lettering import fitted_cap, spaced_like

TITLE = "MEDIA LIBRARY"
# The List button's place in the playlist sheet; the library's menu button is that button with another word
MENU_AT, MENU_WORD = (232, 81, 22, 15), "Menu"
TITLE_AT = (26, 0, 100, 41)  # the playlist's name plate, focused and (21 rows down) not


def title(s):
    """MEDIA LIBRARY on the plate, spaced as PLAYLIST EDITOR is."""
    span = spaced_like(TITLE, TITLE_TEXT, *TITLE_SPAN)
    for y, active in STRIPS:
        title_tile(s, y, active, TITLE, span)


def menu(s):
    x, _, w, _ = MENU_AT
    # as wide as Misc, the widest word the playlist's buttons have
    button_with_word(s, x, MENU_WORD, fitted_cap(MENU_WORD, w - 4, 7))


# name: (the drawing's place in the playlist sheet, how it is drawn)
PICTURES = {"title": (TITLE_AT, title), "menu": (MENU_AT, menu)}


# --- the display under the title and the band with the position bar over the bottom pieces ------------------
# Drawn on the main sheet with the bar view's colours.

# The title's rows above the playlist's top bevel: the library's display, not its list, comes under them
TITLE_ROWS = 15
STRIP_TOP, STRIP_H = TITLE_ROWS, 48
LIST_TOP = STRIP_TOP + STRIP_H
WELL_TOP, WELL_H = 3, 42  # the display's well in the strip, rims included
STRIP_LEFT, STRIP_RIGHT, TILE = 220, 20, 8
# The well from the window's left, and its right end this far from the window's end: right inside the frame at
# both sides, as the list is, so the frame is the same at the left and the right of the display and the list
FRAME = 6  # the window's frame along its sides, in the playlist's pieces
WELL_X, WELL_END = FRAME, 6
SEEK_H = 14  # the band over the bottom pieces
GROOVE_TOP = 3  # the position groove in the band, 8 high
# In the window: the play state, the clock (its colon from it), the song title's row, the rates' row
CLOCK = (30, STRIP_TOP + WELL_TOP + 5)
STATE = (16, CLOCK[1] + 2)
TITLE_ROW = STRIP_TOP + WELL_TOP + 22
RATE_ROW = STRIP_TOP + WELL_TOP + 33
KBPS_X, KHZ_X = 16, 66
VIS_X = STRIP_LEFT - 8  # the visualizer from here to the well's right, a line before it

def ground(s, w, h):
    """The bar's panel; the window's sides over it are the playlist's, laid by the skin."""
    _, panel, _ = colours(s)
    s.rect(0, 0, w, h, panel)


def well(s, x0, x1, left=False, right=False):
    """The display's well from `x0` to `x1`, rimmed as the bar's display: dark at the top and left, light at the
    bottom and right; the list's top rim under it."""
    _, _, rims = colours(s)
    y, h = WELL_TOP, WELL_H
    s.rect(x0, y, x1 - x0, h, rims["bottom"])
    s.rect(x0, y, x1 - x0, 1, rims["top"])
    if left:
        s.rect(x0, y, 1, h - 1, rims["left"])
    if right:
        s.rect(x1 - 1, y + 1, 1, h - 2, rims["right"])
    s.rect(x0 + left, y + 1, x1 - x0 - left - right, h - 2, BLACK)
    s.rect(x0, STRIP_H - 1, x1 - x0, 1, rims["top"])


def strip_left(s):
    ground(s, STRIP_LEFT, STRIP_H)
    well(s, WELL_X, STRIP_LEFT, left=True)
    cx, cy = CLOCK
    dx, *rows = COLON
    for y in rows:
        s.rect(cx + dx, cy - STRIP_TOP + y, 3, 1, "#ffffff")
    row = RATE_ROW - STRIP_TOP + 6
    span_label(s, "KBPS", KBPS_X + 18, KBPS_X + 36, row, 5, "#ffffff")
    span_label(s, "KHZ", KHZ_X + 18, KHZ_X + 31, row, 5, "#ffffff")
    _, _, rims = colours(s)
    s.rect(VIS_X - 3, WELL_TOP + 4, 1, WELL_H - 8, rims["bottom"])


def strip_mid(s):
    ground(s, TILE, STRIP_H)
    well(s, 0, TILE)


def strip_right(s):
    ground(s, STRIP_RIGHT, STRIP_H)
    well(s, 0, STRIP_RIGHT - WELL_END, right=True)


def seek_band(s, w, left=False, right=False):
    """The band's metal, the list's lower rim along its top."""
    ground(s, w, SEEK_H)
    _, _, rims = colours(s)
    x0, x1 = (WELL_X if left else 0), (w - WELL_END if right else w)
    s.rect(x0, 0, x1 - x0, 1, rims["bottom"])


# The transport's and Open's wells as the main window has them, `TRANSPORT_FROM` its top left
TRANSPORT_FROM = (13, 85)
TRANSPORT_SIZE = (148, 24)


def transport(s):
    with moved(s, -TRANSPORT_FROM[0], -TRANSPORT_FROM[1]):
        wells(s, TRANSPORT_WELLS)


def max_pressed(s):
    """Maximize held down, as the playlist's pressed title buttons are."""
    s.rect(61, 42, 10, 9, BLACK)
    small_button(s, 62, 43, 8, 7, "max")


def bottom_tile(s):
    """The playlist's middle tile's gradient, which the bottom's corners continue so their bevels join it."""
    return s.vgrad(72, 38, 185, 10, sy=0)


def bottom_left(s):
    """The bottom's left corner for the library: the side's frame and the bottom's bevel turning up it."""
    s.hfill(0, 72, 6, 38, 85, 4)
    s.path("M6 103V110H0V109H1V108H3V107H4V106H5V103Z", bottom_tile(s))


def bottom_right(s):
    """The bottom's right corner for the library: the middle tile with its bevel turning up the side and the
    resize grip, without the playlist's arrows."""
    s.hfill(265, 72, 11, 38, 88, 4)
    s.path("M256 72H270V103H271V105H272V106H273V107H274V108H276V110H256Z", bottom_tile(s))
    grip(s)


def title_right(s):
    for y, _ in STRIPS:
        top_right(s, y, "max")


# name: (width, height, how it is drawn), on the main sheet
STRIP_PICTURES = {
    "strip-left": (STRIP_LEFT, STRIP_H, strip_left),
    "strip-mid": (TILE, STRIP_H, strip_mid),
    "strip-right": (STRIP_RIGHT, STRIP_H, strip_right),
    "seek-left": (STRIP_LEFT, SEEK_H, lambda s: seek_band(s, STRIP_LEFT, left=True)),
    "seek-mid": (TILE, SEEK_H, lambda s: seek_band(s, TILE)),
    "seek-right": (STRIP_RIGHT, SEEK_H, lambda s: seek_band(s, STRIP_RIGHT, right=True)),
    "transport": (*TRANSPORT_SIZE, transport),
}
PICTURES |= {"title-right": ((153, 0, 25, 41), title_right), "bottom-left": ((0, 72, 6, 38), bottom_left), "bottom-right": ((256, 72, 20, 38), bottom_right), "max-pressed": ((61, 42, 10, 9), max_pressed)}
