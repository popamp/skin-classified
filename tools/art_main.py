"""The main window and its button sheets."""
from art_parts import (BLACK, LOOP, LOOP_STROKE, PRESS_SHIFT, RAISED_INK, PRESSED_INK, TRANSPORT, cream_button, cream_button_down, lamp, lamp_button, label,
                       resize_grip, socket, span_label, transport_icon, transport_inks, window_frame)
from art_sliders import MAIN_PANEL, groove, panel_fit
from art_title import main_strip

# The bolt of Popamp's logo, as an outline around its centre (118.8 units high)
BOLT = ((-10.43, -59.4), (23.46, -59.4), (0, -19.92), (30.91, -19.92), (-19.74, 59.4), (-3.72, 3.54), (-30.91, 3.54))
LOGO_CX, LOGO_CY = 253.5, 94
DISPLAY = "M11 21H265V53H107A7 7 0 0 0 100 60V67H11Z"
TAB_EDGE = "M265 53.5H107A6.5 6.5 0 0 0 100.5 60V67"
# The shuffle icons' bars in a 22 x 11 button, where EQ and PL have their letters
BARS_MIXED = ((9, 5, 2, 3), (12, 3, 2, 5), (15, 6, 2, 2), (18, 4, 2, 4))
BARS_RISING = ((9, 6, 2, 2), (12, 5, 2, 3), (15, 4, 2, 4), (18, 3, 2, 5))
ICON_LABEL = {"eq": ("EQ", 9.5, 18), "pl": ("PL", 10, 17.5)}
WORD_CAP = 5.5


def cbuttons(s):
    inks_up, inks_down = transport_inks(s, 69, 0), transport_inks(s, 69, 18, PRESS_SHIFT)
    for i, name in enumerate(TRANSPORT):
        if name == "eject":
            continue
        x = 23 * i
        s.rect(x + 22, 0, 1, 36, BLACK)
        cream_button(s, x, 0, 22, 18)
        transport_icon(s, name, x, 0, inks_up)
        cream_button_down(s, x, 18, 22, 18)
        transport_icon(s, name, x, 18, inks_down, PRESS_SHIFT)
    cream_button(s, 114, 0, 22, 16)
    transport_icon(s, "eject", 114, 0, inks_up)
    cream_button_down(s, 114, 16, 21, 16, top=2)
    transport_icon(s, "eject", 114, 16, inks_down, PRESS_SHIFT)


def bars(s, frame, table, pressed):
    fx, fy = frame[:2]
    d = "".join(f"M{fx + x} {fy + y}h{w}v{h}h{-w}z" for x, y, w, h in table)
    s.path(d, PRESSED_INK if pressed else RAISED_INK)


def lamp_toggle(s, frame, pressed):
    """A toggle like EQ and PL: the cream button in its black frame, its lamp at the left."""
    lamp_button(s, frame, pressed)
    lamp(s, frame[0] + 3, frame[1] + 3, 3)


def bars_button(s, frame, table, pressed):
    lamp_toggle(s, frame, pressed)
    bars(s, frame, table, pressed)


def loop_button(s, frame, pressed):
    lamp_toggle(s, frame, pressed)
    for d in LOOP:
        s.stroke(d, PRESSED_INK if pressed else RAISED_INK, LOOP_STROKE, f' transform="translate({frame[0]} {frame[1]})"')


def word_button(s, frame, which, pressed):
    """The EQ or PL toggle: lamp and two letters."""
    lamp_toggle(s, frame, pressed)
    text, left, right = ICON_LABEL[which]
    span_label(s, text, frame[0] + left, frame[0] + right, frame[1] + 8, WORD_CAP, PRESSED_INK if pressed else RAISED_INK)


def backing(s, x, y, w, h, rows=()):
    """The metal round a sprite's frames: one gradient across it (the walls), and the `rows` (y, height) over it."""
    s.hfill(x, y, w, h, y + h - 4)  # a row below the lamps
    for ry, rh in rows:
        s.vfill(x, y + ry, w, rh, x + w // 2, 2)


def shufrep(s):
    """Each row of the shuffle and repeat sprites is the main window's own play-mode area in that row's state."""
    for i in range(len(EQ_STATES)):
        for mx, my, sx, w in (SHUFFLE_SPRITE, REPEAT_SPRITE):
            clip = f"playmodes{i}-{sx}"
            s.defs.append(f'<clipPath id="{clip}"><rect x="{sx}" y="{15 * i}" width="{w}" height="15"/></clipPath>')
            s.add(f'<g clip-path="url(#{clip})"><g transform="translate({sx - mx} {15 * i - my})">')
            play_modes(s, i)
            s.add("</g></g>")
    for y in (61, 73):
        backing(s, 0, y, 92, 12, ((11, 1),))
        word_button(s, (0, y, 22, 11), "eq", False)
        word_button(s, (25, y, 21, 11), "pl", False)
        word_button(s, (46, y, 22, 11), "eq", False)
        word_button(s, (71, y, 21, 11), "pl", y == 73)


def popamp_bolt(s, cx, cy, height):
    """The bolt of Popamp's logo, sunk into the metal: dark rim on top, light lip below, lit from the top left."""
    k = height / 118.8
    outline = " ".join(f"{cx + px * k:.2f},{cy + py * k:.2f}" for px, py in BOLT)
    s.defs.append(
        '<linearGradient id="boltfill" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#8a4a08"/><stop offset="0.45" stop-color="#ee9414"/>'
        '<stop offset="1" stop-color="#ffd23f"/></linearGradient>'
    )
    miter = 'stroke-linejoin="miter" stroke-miterlimit="4"'
    s.add(f'<polygon points="{outline}" transform="translate(0.9 0.9)" fill="#d4d4e2" stroke="#d4d4e2" stroke-width="0.8" {miter}/>')
    s.add(f'<polygon points="{outline}" fill="#000000" stroke="#000000" stroke-width="1.4" {miter}/>')
    s.add(f'<polygon points="{outline}" fill="url(#boltfill)"/>')
    # the shadow the upper edges cast on the sunken face: everything but the bolt moved down and right, clipped to the bolt
    s.defs.append(f'<clipPath id="boltclip"><polygon points="{outline}"/></clipPath>')
    x0, y0, w, h = 241, 82, 26, 25
    moved = "L".join(f"{cx + px * k + 1.1:.2f} {cy + py * k + 1.1:.2f}" for px, py in BOLT)
    s.add(f'<path d="M{x0} {y0}h{w}v{h}h{-w}ZM{moved}Z" fill="#000000" fill-rule="evenodd" opacity="0.55" clip-path="url(#boltclip)"/>')


def display(s):
    """The song display: one cut-out with a dark rim top-left, a light one bottom-right and a raised tab in its corner."""
    s.rect(10, 20, 256, 1, s.color(150, 20))
    s.rect(10, 21, 1, 47, s.color(10, 40))
    s.rect(265, 21, 1, 32, s.color(265, 30))
    s.rect(11, 67, 89, 1, s.color(50, 67))
    s.path(DISPLAY, BLACK)
    s.stroke(TAB_EDGE, s.color(180, 53), 1)
    s.rect(72, 30, 3, 1, "#ffffff")  # the clock's colon
    s.rect(72, 33, 3, 1, "#ffffff")
    span_label(s, "KBPS", 126.5, 146, 49, 6, "#ffffff")
    span_label(s, "KHZ", 167, 182, 49, 6, "#ffffff")


def position_slot(s):
    """The position bar's slot in the bare window (the sliding bar is drawn over it from its own sheet)."""
    from art_sliders import slot

    s.rect(15, 73, 1, 8, s.color(15, 75))
    with s.source(ref="posbar", dx=-16, dy=-72):
        slot(s, 16, 72)


TRANSPORT_WELLS = ((15, 87, 116, 20), (135, 88, 24, 18))  # the transport's and Open's black frames
TOGGLE_WELLS = (((219, 58, 22, 11), "eq"), ((244, 58, 21, 11), "pl"))
# The shuffle sprite's two buttons and the repeat sprite's one: the black frame in the main window, as large as EQ's,
# and the bars (none for repeat)
PLAY_MODES = (((164, 91, 22, 11), BARS_MIXED), ((189, 91, 22, 11), BARS_RISING), ((214, 91, 22, 11), None))
# The EQ button in the reference's shufrep sheet in each of the sprites' four rows (off, off pressed, on, on pressed):
# the play-mode buttons take its colours, state by state
EQ_STATES = ((0, 61), (46, 61), (0, 73), (46, 73))
# The play-mode area of the main window, and where the player shows the sprites in it: (x, y, sheet x, width)
PLAY_MODE_AREA = (163, 89, 75, 15)
SHUFFLE_SPRITE, REPEAT_SPRITE = (164, 89, 28, 47), (210, 89, 0, 28)


def wells(s, frames):
    """Black frames sunk into the metal."""
    for f in frames:
        socket(s, f)
        s.rect(*f, BLACK)


def play_mode_socket(s, frame):
    """A play-mode button's rim: the EQ well's, which is as large, wherever the button is shown."""
    (ex, ey, _, _), _ = TOGGLE_WELLS[0]
    with s.source(ref="main", dx=ex - frame[0], dy=ey - frame[1], absolute=True):
        socket(s, frame)


def play_modes(s, row=0):
    """The play-mode area in main window coordinates: the panel's metal, the rims and the buttons as EQ is in sprite row `row`."""
    s.rect(*PLAY_MODE_AREA, panel_fit(s))
    ex, ey = EQ_STATES[row]
    for frame, table in PLAY_MODES:
        play_mode_socket(s, frame)
        x, y = frame[:2]
        with s.source(ref="shufrep", dx=ex - x, dy=ey - y, absolute=True):
            if table:
                bars_button(s, frame, table, False)
            else:
                loop_button(s, frame, False)


def transport(s):
    wells(s, TRANSPORT_WELLS)
    with s.source(ref="cbuttons", dx=-16, dy=-88):
        inks = transport_inks(s, 16 + 69, 88)
        for i, name in enumerate(n for n in TRANSPORT if n != "eject"):
            cream_button(s, 16 + 23 * i, 88, 22, 18)
            transport_icon(s, name, 16 + 23 * i, 88, inks)
    with s.source(ref="cbuttons", dx=114 - 136, dy=-89):
        cream_button(s, 136, 89, 22, 16)
    with s.source(ref="cbuttons", dx=-16, dy=-88):
        transport_icon(s, "eject", 136, 89, inks)


def main(s):
    window_frame(s, 17)
    s.rect(*MAIN_PANEL, panel_fit(s))
    main_strip(s, 0, True, x0=0)
    display(s)
    groove(s, 107, 60, 64, 7)
    position_slot(s)
    transport(s)
    for frame, which in TOGGLE_WELLS:
        socket(s, frame)
        word_button(s, frame, which, False)
    play_modes(s)
    popamp_bolt(s, LOGO_CX, LOGO_CY, 22)
    resize_grip(s)
