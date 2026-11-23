"""The windows skin.toml lays out itself: the main window's bar view and the media library."""
from art_bar import BAR_BUTTON, BUTTON_INSET, BAR_H, BAR_LEFT, BAR_MIN, BAR_RIGHT, CLOCK, DISPLAY_X, GROOVE_Y, PLAY_MODES_AT
from art_main import PLAY_MODES, REPEAT_SPRITE, SHUFFLE_SPRITE
import art_ml as ml

BAR_WINDOW = f"""
# --- the main window's bar view, from the sheets above ---

[[window]]
key = "main"

[window.bar]
edge = "bottom"
size = [{BAR_MIN}, {BAR_H}]"""

LIBRARY_WINDOW = """
# --- the media library, in the playlist's frame from the sheets above ---

[[window]]
key = "library"
placement = "docked"
empty_press = "nothing"
wheel_scrolls_list = true

[window.normal]
size = [400, 232]
resize_step = [25, 29]
cursor = "pnormal\""""


def element(kind, place, view="bar", **keys):
    """One element of a window's view as TOML; a place with a text in it is `edges`."""
    where = "edges" if any(isinstance(v, str) for v in place) else "rect"
    lines = ["", f"[[window.{view}.element]]", f'type = "{kind}"', f"{where} = {toml(list(place))}"]
    return lines + [f"{k} = {toml(v)}" for k, v in keys.items()]


def toml(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {toml(x)}" for k, x in v.items()) + " }"
    if isinstance(v, list):
        return "[" + ", ".join(toml(x) for x in v) + "]"
    return f'"{v}"' if isinstance(v, str) else str(v)


def area(sheet, x, y, w, h):
    return {"file": f"sheets/{sheet}.svg", "area": [x, y, w, h]}


def bar_area(x, y):
    return {"file": "bar/buttons.svg", "area": [x, y, BAR_BUTTON, BAR_BUTTON]}


def end(x):
    """A place counted from the bar's right end, where the right picture starts at 0."""
    return f"end-{BAR_RIGHT - x}"


def toggle(sheet_box, at, states, flag, click, **more):
    """A two-state button from shufrep: `states` are the y of off, off pressed, on, on pressed."""
    (sx, w, h), (x, y) = sheet_box, at
    pics = dict(zip(("normal", "pressed", "on", "on_pressed"), (area("shufrep", sx + dx, sy, w, h) for dx, sy in states)))
    return element("toggle", (end(x), y, end(x + w), y + h), **pics, flag=flag, click=click, **more)


PLAY_MODE_STATES = ((0, 0), (0, 15), (0, 30), (0, 45))


def play_mode(frame, sprite, flag, click, **more):
    """One button of a shuffle or repeat sprite, from its black frame in: the bar draws the rim round it."""
    (fx, fy, fw, fh), (ox, oy, sx, _) = frame, sprite
    dx, dy = PLAY_MODES_AT
    states = [(x, y + fy - oy) for x, y in PLAY_MODE_STATES]
    return toggle((sx + fx - ox, fw, fh), (fx + dx, fy + dy), states, flag, click, **more)


def bar_window():
    """The bar as TOML: the main window's sprites on the bar's own metal."""
    e = []
    e += element("image", (0, 0, BAR_LEFT, BAR_H), normal="bar/left.svg")
    e += element("image", (BAR_LEFT, 0, end(0), BAR_H), normal="bar/mid.svg", fill="tile")
    e += element("image", (end(0), 0, "end", BAR_H), normal="bar/right.svg")
    b, mid = BAR_BUTTON, (BAR_H - BAR_BUTTON) // 2
    e += element("button", (BUTTON_INSET, mid, b, b), normal=bar_area(0, 0), pressed=bar_area(0, b),
                 menu_press="main", cursor="mainmenu", tip="Main Menu")  # fmt: skip
    transport = (
        (0, 23, "previous", "Previous", {"shift": "back5s", "ctrl": "start-of-list", "menu": "previous"}),
        (23, 23, "play", "Play", {"shift": "open-file", "ctrl": "open-url", "menu": "play"}),
        (46, 23, "pause", "Pause", {"menu": "pause"}),
        (69, 23, "stop", "Stop", {"shift": "stop-fadeout", "ctrl": "stop-after-current", "menu": "stop"}),
        (92, 22, "next", "Next", {"shift": "fwd5s", "ctrl": "end-of-list", "menu": "next"}),
    )
    for sx, w, click, tip, more in transport:
        e += element("button", (18 + sx, 2, w, 18), normal=area("cbuttons", sx, 0, w, 18), pressed=area("cbuttons", sx, 18, w, 18),
                     click=click, **more, tip=tip)  # fmt: skip
    e += element("button", (138, 3, 22, 16), normal=area("cbuttons", 114, 0, 22, 16), pressed=area("cbuttons", 114, 16, 22, 16),
                 click="open-file", shift="open-folder", ctrl="open-url", menu="eject", tip="Open")  # fmt: skip
    for sx, state in ((0, "playing"), (9, "paused"), (18, "stopped")):
        e += element("image", (DISPLAY_X + 4, 6, 9, 9), normal=area("playpaus", sx, 0, 9, 9), show=state)
    e += element("clock", (*CLOCK, 63, 13), hide="stopped")
    e += element("button", (*CLOCK, 63, 13), press="toggle-time-mode", menu="time")
    e += element("vis", (243, 3, 76, 16))
    e += element("button", (243, 3, 76, 16), press="cycle-vis-mode", menu="vis")
    e += element("marquee", (BAR_LEFT + 3, 4, end(-3), 10), double="file-info", cursor="songname",
                 tip="Song Title (right-click for options)", menu="song-title")  # fmt: skip
    # the position thumb without its top and bottom rows, centred on the groove, which it runs the length of
    thumb = {"normal": area("posbar", 248, 1, 29, 8), "pressed": area("posbar", 278, 1, 29, 8)}
    top = GROOVE_Y + 1 - 4
    e += element("slider", (BAR_LEFT, top, end(0), top + 8), value="position", thumb=thumb, thumb_len=29, live=False,
                 show="seekable", cursor="posbar", menu="seek")  # fmt: skip
    track = {"file": "sheets/volume.svg", "first": [0, 0, 68, 13], "step": [0, 15], "count": 28}
    # a row below the track's top, as the main window shows it, so it sits on the groove
    thumb = {k: area("volume", x, 422, 14, 11) | {"offset": [0, 1]} for k, x in (("normal", 15), ("pressed", 0))}
    e += element("slider", (end(9), 4, end(77), 17), value="volume", track=track, thumb=thumb, thumb_len=14, reset=200,
                 wheel_step=8, cursor="volbal", tip="Volume")  # fmt: skip
    # the sprites as the main window shows them, where TOGGLES_AT and PLAY_MODES_AT put its wells
    e += toggle((0, 23, 12), (82, 5), ((0, 61), (46, 61), (0, 73), (46, 73)), "eq-window", "toggle-eq-window")
    e += toggle((23, 23, 12), (105, 5), ((0, 61), (46, 61), (0, 73), (46, 73)), "playlist-window", "toggle-playlist-window")
    *shuffle, repeat = (frame for frame, *_ in PLAY_MODES)
    for frame in shuffle:
        e += play_mode(frame, SHUFFLE_SPRITE, "shuffle", "toggle-shuffle", menu="shuffle")
    e += play_mode(repeat, REPEAT_SPRITE, "repeat", "toggle-repeat", menu="repeat")
    e += element("button", (end(BAR_RIGHT - BUTTON_INSET - b), mid, end(BAR_RIGHT - BUTTON_INSET), mid + b), normal=bar_area(b, 0), pressed=bar_area(b, b),
                 click="exit", tip="Close")  # fmt: skip
    return [BAR_WINDOW, *e]


FRAME = 6  # the window's frame along its sides, in the playlist's pieces


def library_window(title_width):
    """The media library as TOML: the playlist's frame with a title of its own, the display with the visualizer
    under the title, the position bar over the bottom and the transport in the bottom's middle."""
    pl = lambda x, y, w, h: area("pledit", x, y, w, h)
    ml_area = lambda name, x, y, w, h: {"file": f"ml/{name}.svg", "area": [x, y, w, h]}
    rows = ml.TITLE_ROWS
    focus = lambda x: {"normal": pl(x, 0, 25, rows), "inactive": pl(x, 21, 25, rows)}
    v, top, bottom = "normal", ml.LIST_TOP, f"end-{38 + ml.SEEK_H}"
    e = [LIBRARY_WINDOW]
    e += element("image", (0, 0, 25, rows), v, **focus(0))
    e += element("image", (25, 0, "end-25", rows), v, **focus(127), fill="tile")
    e += element("image", ("end-25", 0, "end", rows), v, normal=ml_area("title-right", 0, 0, 25, rows),
                 inactive=ml_area("title-right", 0, 21, 25, rows))  # fmt: skip
    half = title_width // 2
    title = {"file": "ml/title.svg"}
    e += element("image", (f"center-{half}", 0, f"center+{title_width - half}", rows), v,
                 normal=title | {"area": [0, 0, title_width, rows]}, inactive=title | {"area": [0, 21, title_width, rows]})  # fmt: skip
    e += three("strip", ml.STRIP_TOP, ml.STRIP_H, v)
    e += element("image", (0, top, 12, bottom), v, normal=pl(0, 42, 12, 29), fill="tile")
    # the side's dark band between the frame and the list in the display's metal, so the left margin runs on
    # from the display down to the position bar in one colour
    e += element("image", (FRAME, top, ml.WELL_X, bottom), v, normal=ml_area("strip-left", FRAME, 0, ml.WELL_X - FRAME, 2), fill="tile")
    e += element("image", ("end-20", top, "end", bottom), v, normal=pl(31, 42, 20, 29), fill="tile")
    e += three("seek", bottom, ml.SEEK_H, v)
    # the bottom: the playlist's tile between two corners of the library's own, the right one with the resize grip
    e += element("image", (0, "end-38", FRAME, "end"), v, normal="ml/bottom-left.svg")
    e += element("image", (FRAME, "end-38", "end-20", "end"), v, normal=pl(179, 0, 25, 38), fill="tile")
    e += element("image", ("end-20", "end-38", "end", "end"), v, normal="ml/bottom-right.svg")
    # The sides from the title to the bottom's bevel: one picture each, the outer columns of the list's sides,
    # so the frame runs on along the display and the position bar as it does along the list
    e += element("image", (0, ml.STRIP_TOP, FRAME, "end-7"), v, normal=pl(0, 42, FRAME, 29), fill="tile")
    e += element("image", (f"end-{FRAME}", ml.STRIP_TOP, "end", "end-7"), v, normal=pl(51 - FRAME, 42, FRAME, 29), fill="tile")
    e += element("drag", (0, 0, "end-22", ml.STRIP_TOP + ml.WELL_TOP), v, double="toggle-library-maximize", cursor="ptbar")
    e += element("button", ("end-20", 3, "end-11", 12), v, pressed=ml_area("max-pressed", 1, 0, 9, 9),
                 click="toggle-library-maximize", tip="Maximize")  # fmt: skip
    e += element("button", ("end-11", 3, "end-2", 12), v, pressed=pl(52, 42, 9, 9), click="toggle-library-window",
                 cursor="pclose", tip="Close")  # fmt: skip
    e += display(v)
    thumb = {"normal": pl(52, 53, 8, 18), "pressed": pl(61, 53, 8, 18)}
    e += element("library", (12, top, "end-7", bottom), v, menu="library", thumb=thumb)
    e += seek_bar(v)
    e += bottom_controls(v)
    e += element("resize", ("end-20", "end-20", "end", "end"), v, cursor="psize")
    return e


def three(name, top, h, v):
    """A row of the library's pieces `h` high: `name`-left, `name`-mid tiled and `name`-right."""
    at = lambda part: {"normal": f"ml/{name}-{part}.svg"}
    bottom = top + h if isinstance(top, int) else f"end-{int(top[4:]) - h}"
    left = (0, top, ml.STRIP_LEFT, h) if isinstance(top, int) else (0, top, ml.STRIP_LEFT, bottom)
    e = element("image", left, v, **at("left"))
    e += element("image", (ml.STRIP_LEFT, top, f"end-{ml.STRIP_RIGHT}", bottom), v, **at("mid"), fill="tile")
    e += element("image", (f"end-{ml.STRIP_RIGHT}", top, "end", bottom), v, **at("right"))
    return e


def display(v):
    """The display's song block and its visualizer."""
    cx, cy = ml.CLOCK
    e = []
    for sx, state in ((0, "playing"), (9, "paused"), (18, "stopped")):
        e += element("image", (*ml.STATE, 9, 9), v, normal=area("playpaus", sx, 0, 9, 9), show=state)
    e += element("clock", (cx, cy, 63, 13), v, hide="stopped")
    e += element("button", (cx, cy, 63, 13), v, press="toggle-time-mode", menu="time")
    e += element("marquee", (ml.STATE[0], ml.TITLE_ROW, ml.VIS_X - ml.STATE[0] - 8, 10), v, double="file-info", cursor="songname",
                 tip="Song Title (right-click for options)", menu="song-title")  # fmt: skip
    for x, text in ((ml.KBPS_X, "kbps"), (ml.KHZ_X, "khz")):
        e += element("text", (x, ml.RATE_ROW, 15, 6), v, text=text)
    top, bottom = ml.STRIP_TOP + ml.WELL_TOP + 3, ml.STRIP_TOP + ml.WELL_TOP + ml.WELL_H - 3
    vis = (ml.VIS_X, top, f"end-{ml.WELL_END + 3}", bottom)
    e += element("vis", vis, v)
    e += element("button", vis, v, press="cycle-vis-mode", menu="vis")
    return e


def seek_bar(v):
    """The position bar along the band: the main window's groove, its ends and a tiled middle, and its thumb."""
    y0 = 38 + ml.SEEK_H - ml.GROOVE_TOP
    y1 = y0 - 8
    left, right = ml.WELL_X, ml.WELL_END
    e = element("image", (left, f"end-{y0}", left + 6, f"end-{y1}"), v, normal=area("posbar", 0, 1, 6, 8))
    e += element("image", (left + 6, f"end-{y0}", f"end-{right + 6}", f"end-{y1}"), v, normal=area("posbar", 100, 1, 8, 8), fill="tile")
    e += element("image", (f"end-{right + 6}", f"end-{y0}", f"end-{right}", f"end-{y1}"), v, normal=area("posbar", 242, 1, 6, 8))
    thumb = {"normal": area("posbar", 248, 1, 29, 8), "pressed": area("posbar", 278, 1, 29, 8)}
    e += element("slider", (left, f"end-{y0}", f"end-{right}", f"end-{y1}"), v, value="position", thumb=thumb, thumb_len=29,
                 live=False, show="seekable", cursor="posbar", menu="seek")  # fmt: skip
    return e


def centre(dx):
    """A place `dx` from the window's middle."""
    return f"center+{dx}" if dx >= 0 else f"center-{-dx}"


def bottom_controls(v):
    """In the bottom: the status in the playlist's well, the transport in the main window's wells in the middle
    (its Play plays the track picked in the library), the volume and the menu button."""
    e = element("image", (11, "end-31", 105, "end-19"), v, normal=area("pledit", 130, 79, 94, 12))
    e += element("text", (14, "end-28", 102, "end-22"), v, text="library-status")
    (tw, th), half = ml.TRANSPORT_SIZE, ml.TRANSPORT_SIZE[0] // 2
    row = 34  # the transport picture's top, from the window's bottom
    e += element("image", (centre(-half), f"end-{row}", centre(tw - half), f"end-{row - th}"), v, normal="ml/transport.svg")
    fx, fy = ml.TRANSPORT_FROM
    transport = (
        (0, 23, "previous", "Previous", {"shift": "back5s", "ctrl": "start-of-list", "menu": "previous"}),
        (23, 23, "library-play", "Play the picked track", {"shift": "open-file", "ctrl": "open-url", "menu": "play"}),
        (46, 23, "pause", "Pause", {"menu": "pause"}),
        (69, 23, "stop", "Stop", {"shift": "stop-fadeout", "ctrl": "stop-after-current", "menu": "stop"}),
        (92, 22, "next", "Next", {"shift": "fwd5s", "ctrl": "end-of-list", "menu": "next"}),
    )
    x0, y0 = 16 - fx - half, row - (88 - fy)  # the main window has the buttons at 16, 88
    for sx, w, click, tip, more in transport:
        e += element("button", (centre(x0 + sx), f"end-{y0}", centre(x0 + sx + w), f"end-{y0 - 18}"), v,
                     normal=area("cbuttons", sx, 0, w, 18), pressed=area("cbuttons", sx, 18, w, 18), click=click, **more, tip=tip)  # fmt: skip
    ox, oy = 136 - fx - half, row - (89 - fy)  # and Open at 136, 89
    e += element("button", (centre(ox), f"end-{oy}", centre(ox + 22), f"end-{oy - 16}"), v, normal=area("cbuttons", 114, 0, 22, 16),
                 pressed=area("cbuttons", 114, 16, 22, 16), click="open-file", shift="open-folder", ctrl="open-url", menu="eject",
                 tip="Open")  # fmt: skip
    track = {"file": "sheets/volume.svg", "first": [0, 0, 68, 13], "step": [0, 15], "count": 28}
    thumb = {k: area("volume", x, 422, 14, 11) | {"offset": [0, 1]} for k, x in (("normal", 15), ("pressed", 0))}
    e += element("slider", ("end-120", "end-28", "end-52", "end-15"), v, value="volume", track=track, thumb=thumb, thumb_len=14,
                 reset=200, wheel_step=8, cursor="volbal", tip="Volume")  # fmt: skip
    # the List button, labelled for the library
    e += element("image", ("end-44", "end-29", "end-22", "end-14"), v, normal="ml/menu.svg")
    e += element("button", ("end-44", "end-29", "end-22", "end-14"), v, menu_release="library", tip="Library Menu")
    return e
