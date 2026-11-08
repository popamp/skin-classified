"""The playlist editor sheet."""
from art_main import lamp_button

CYAN = "#00c6ff"
BLACK = "#000000"

# Metal pieces of the window frame: (rect, cream buttons in black frames on it)
SURFACES = [
    ((0, 0, 25, 20), []),
    ((26, 0, 100, 20), []),
    ((127, 0, 25, 20), []),
    ((153, 0, 25, 20), []),
    ((0, 21, 25, 20), []),
    ((26, 21, 100, 20), []),
    ((127, 21, 25, 20), []),
    ((153, 21, 25, 20), []),
    ((179, 0, 25, 38), []),
    ((205, 0, 75, 38), []),
    ((0, 42, 25, 29), []),
    ((26, 42, 25, 29), []),
    ((72, 42, 25, 14), []),
    ((72, 57, 25, 14), []),
    ((99, 42, 50, 14), []),
    ((99, 57, 50, 14), []),
    ((0, 72, 125, 38), [(14, 81, 22, 15), (43, 81, 22, 15), (72, 81, 22, 15), (101, 81, 22, 15)]),
    ((126, 72, 150, 38), [(232, 81, 22, 15)]),
]
# Black windows on the metal: left out of the metal's colours, drawn as exact pixels
HOLES = [(131, 80, 92, 10), (130, 93, 57, 9), (189, 94, 34, 8), (11, 42, 14, 29), (26, 42, 10, 29)]


def surface(s, rect, buttons, n=12, tol=22):
    """Metal as one gradient per row; framed cream buttons drawn as such; every other mark as exact pixels.

    In the title strips rows 5..9 are gold rules and lettering, so they take the colours of rows 3..4.
    Black windows are filled black, with what is in them as exact pixels.
    """
    x, y, w, h = rect
    title = h == 20 and y in (0, 21)
    sample = (lambda j: (y + 3, 2) if 5 <= j - y <= 9 else (j, 1)) if title else None
    holes = [r for r in HOLES if r[0] < x + w and r[0] + r[2] > x and r[1] < y + h and r[1] + r[3] > y]
    s.rows(*rect, n, buttons + holes, sample)
    for f in buttons:
        lamp_button(s, f, False)
    s.pix_tiles(*rect, 16, tol, buttons + holes)
    for h in holes:
        s.rect(*h, BLACK)
        s.pix(*h, BLACK, 20)


def pledit(s):
    for rect, buttons in SURFACES:
        surface(s, rect, buttons)
    s.pix(52, 42, 19, 29, CYAN, 0)  # scroll thumbs
    s.pix(150, 42, 9, 9, CYAN, 0)
    s.pix(0, 111, 280, 75, CYAN, 0)  # menu items: flat cream or blue with their words
