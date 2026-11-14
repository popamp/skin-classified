"""The media library's own pictures: its name on the title bar and its menu button, drawn as the playlist's are."""
from art_pl import STRIPS, TITLE_SPAN, TITLE_TEXT, button_with_word, title_tile
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
