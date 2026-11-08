"""Sheets of the main window: transport buttons."""

BLACK = "#000000"
# The bolt of Popamp's logo, as an outline around its centre (118.8 units high)
BOLT = ((-10.43, -59.4), (23.46, -59.4), (0, -19.92), (30.91, -19.92), (-19.74, 59.4), (-3.72, 3.54), (-30.91, 3.54))
LOGO_CX, LOGO_CY = 253.5, 94
LOGO_AREA = (241, 82, 26, 25)  # where the reference's logo was: plain metal now


def cream_face(s, x, y, w, h, icon_tol=10):
    """A cream face: a fitted gradient with the engraved icon on it as exact pixels."""
    s.rect(x, y, w, h, s.lin(x, y, w, h))
    s.pix(x, y, w, h, "lin", icon_tol)


def cream_button(s, x, y, w, h):
    """A raised cream button: an outer top-left edge, two bevel rings and a sunken face."""
    r = s.edge(x, y, w, h)
    r = s.ring(*r)
    r = s.ring(*r)
    cream_face(s, *r)


def cream_button_down(s, x, y, w, h, top=1):
    """The pressed button: black top-left (`top` rows), two dark rings and a darker face."""
    s.rect(x, y, w, h, BLACK)
    r = s.ring(x + 1, y + top, w - 1, h - top)
    r = s.ring(*r)
    cream_face(s, *r)


def cbuttons(s):
    for i in range(4):  # previous, play, pause, stop: 22 wide and a black column
        x = 23 * i
        s.rect(x + 22, 0, 1, 18, BLACK)
        cream_button(s, x, 0, 22, 18)
        s.rect(x + 22, 18, 1, 18, s.color(x + 22, 20, 1, 10))
        cream_button_down(s, x, 18, 22, 18)
    cream_button(s, 92, 0, 22, 18)
    cream_button_down(s, 92, 18, 22, 18)
    cream_button(s, 114, 0, 22, 16)  # eject
    s.rect(135, 16, 1, 16, s.color(135, 16, 1, 16))
    cream_button_down(s, 114, 16, 21, 16, top=2)


def exact_around(s, outer, inner, bg="#00c6ff"):
    """The exact pixels of `outer` outside `inner` (thin margins next to a drawn shape)."""
    ox, oy, ow, oh = outer
    ix, iy, iw, ih = inner
    for x, y, w, h in ((ox, oy, ow, iy - oy), (ox, iy + ih, ow, oy + oh - iy - ih), (ox, iy, ix - ox, ih), (ix + iw, iy, ox + ow - ix - iw, ih)):
        if w > 0 and h > 0:
            s.pix(x, y, w, h, bg, 0)


def lamp_button(s, frame, pressed):
    """A cream toggle in a black frame: one cream bevel (two darker ones when pressed) and a face with lamp and label."""
    r = s.ring(*frame)
    r = s.ring(*r)
    if pressed:
        r = s.ring(*r)
    cream_face(s, *r)


def lamp_sprite(s, sprite, frames, pressed):
    """`pressed`: one flag per frame (the reference mixes pressed and raised halves in one sprite)."""
    if isinstance(pressed, bool):
        pressed = [pressed] * len(frames)
    for f, p in zip(frames, pressed):
        lamp_button(s, f, p)
    if len(frames) == 1:
        exact_around(s, sprite, frames[0])
    else:  # two buttons side by side: margins around their common box, the gap between them
        a, b = frames
        box = (a[0], min(a[1], b[1]), b[0] + b[2] - a[0], max(a[3], b[3]))
        exact_around(s, sprite, box)
        s.pix(a[0] + a[2], box[1], b[0] - a[0] - a[2], box[3], "#00c6ff", 0)


def shufrep(s):
    shuffle_pressed = [(False, False), (True, False), (False, False), (False, True)]
    for i in range(4):
        y = 15 * i
        lamp_sprite(s, (0, y, 28, 15), [(3, y + 2, 23, 11)], i % 2 == 1)
        lamp_sprite(s, (28, y, 47, 15), [(28, y + 2, 21, 11), (52, y + 2, 22, 11)], shuffle_pressed[i])
    s.pix(0, 60, 92, 1, "#00c6ff", 0)
    for y in (61, 73):
        lamp_sprite(s, (0, y, 23, 12), [(0, y, 22, 11)], False)
        lamp_sprite(s, (23, y, 23, 12), [(25, y, 21, 11)], False)
        lamp_sprite(s, (46, y, 23, 12), [(46, y, 22, 11)], False)
        lamp_sprite(s, (69, y, 23, 12), [(71, y, 21, 11)], y == 73)


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
    x, y, w, h = LOGO_AREA
    moved = "L".join(f"{cx + px * k + 1.1:.2f} {cy + py * k + 1.1:.2f}" for px, py in BOLT)
    s.add(f'<path d="M{x} {y}h{w}v{h}h{-w}ZM{moved}Z" fill="#000000" fill-rule="evenodd" opacity="0.55" clip-path="url(#boltclip)"/>')


def socket(s, frame):
    """The sunken rim round a framed button."""
    x, y, w, h = frame
    s.ring(x - 1, y - 1, w + 2, h + 2)


DISPLAY = "M11 21H265V53H107A7 7 0 0 0 100 60V67H11Z"
TAB_EDGE = "M265 53.5H107A6.5 6.5 0 0 0 100.5 60V67"


def main(s):
    import art_title

    art_title.main_strip(s, 0, True, x0=0)
    skip = [(10, 20, 256, 34), (10, 53, 92, 15), (14, 86, 118, 22), (134, 87, 25, 20), (161, 89, 79, 15), (217, 56, 49, 15), (106, 59, 67, 10), (12, 72, 6, 10), (259, 72, 8, 10)] + [LOGO_AREA]
    s.cols(0, 14, 7, 102)
    s.rows(7, 14, 261, 102, 16, skip)
    s.cols(268, 14, 7, 102)
    s.pix(12, 72, 6, 10, "all")  # ends of the position bar's slot
    s.pix(259, 72, 8, 10, "all")
    # song display: dark rim top-left, light bottom-right, a raised tab cut into its lower right
    s.rect(10, 20, 256, 1, s.color(150, 20))  # dark top
    s.rect(10, 21, 1, 47, s.color(10, 40))  # dark left
    s.rect(265, 21, 1, 32, s.color(265, 30))  # light right, down to the tab
    s.rect(11, 67, 89, 1, s.color(50, 67))  # light bottom, left of the tab
    s.path(DISPLAY, "#000000")
    s.stroke(TAB_EDGE, s.color(180, 53), 1)
    s.pix(11, 21, 254, 32, "#000000", 40)  # colon, KBPS, KHZ
    from art_sliders import groove

    groove(s, 107, 60, 64, 7)
    for f in [(219, 58, 22, 11), (244, 58, 21, 11), (163, 91, 23, 11), (189, 91, 23, 11), (215, 91, 23, 11)]:
        socket(s, f)
        lamp_button(s, f, False)
    # transport buttons and eject, as on their own sheet
    for f in [(15, 87, 116, 20), (135, 88, 23, 18)]:
        socket(s, f)
        s.rect(*f, "#000000")
    with s.source(ref="cbuttons", dx=-16, dy=-88):
        for i in range(4):
            cream_button(s, 16 + 23 * i, 88, 22, 18)
        cream_button(s, 108, 88, 22, 18)
    with s.source(ref="cbuttons", dx=114 - 136, dy=-89):
        cream_button(s, 136, 89, 22, 16)
    s.rect(*LOGO_AREA, s.frame(*LOGO_AREA))
    popamp_bolt(s, LOGO_CX, LOGO_CY, 22)
    resize_grip(s)


def resize_grip(s):
    """Two light diagonal grooves with dark shadows in the bottom-right corner."""
    light, dark = s.color(266, 100), s.color(266, 101)
    for x0, y0, x1, y1 in [(267, 99.5, 258.5, 108), (267, 103.5, 262.5, 108)]:
        s.stroke(f"M{x0 + 1} {y0}L{x1 + 1} {y1}", dark)
        s.stroke(f"M{x0} {y0}L{x1} {y1}", light)
