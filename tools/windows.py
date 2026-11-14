"""The windows skin.toml lays out itself: the main window's bar view and the media library."""
from art_bar import BAR_BUTTON, BAR_H, BAR_LEFT, BAR_MIN, BAR_RIGHT, CLOCK, DISPLAY_X, GROOVE_Y

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
size = [275, 116]
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


def bar_window():
    """The bar as TOML: the main window's sprites on the bar's own metal."""
    e = []
    e += element("image", (0, 0, BAR_LEFT, BAR_H), normal="bar/left.svg")
    e += element("image", (BAR_LEFT, 0, end(0), BAR_H), normal="bar/mid.svg", fill="tile")
    e += element("image", (end(0), 0, "end", BAR_H), normal="bar/right.svg")
    b, mid = BAR_BUTTON, (BAR_H - BAR_BUTTON) // 2
    e += element("button", (4, mid, b, b), normal=bar_area(0, 0), pressed=bar_area(0, b),
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
    thumb = {"normal": area("volume", 15, 422, 14, 11), "pressed": area("volume", 0, 422, 14, 11)}
    e += element("slider", (end(9), 4, end(77), 17), value="volume", track=track, thumb=thumb, thumb_len=14, reset=200,
                 wheel_step=8, cursor="volbal", tip="Volume")  # fmt: skip
    # the sprites as the main window shows them, where TOGGLES_AT and PLAY_MODES_AT put its wells
    e += toggle((0, 23, 12), (82, 5), ((0, 61), (46, 61), (0, 73), (46, 73)), "eq-window", "toggle-eq-window")
    e += toggle((23, 23, 12), (105, 5), ((0, 61), (46, 61), (0, 73), (46, 73)), "playlist-window", "toggle-playlist-window")
    e += toggle((28, 47, 15), (133, 3), ((0, 0), (0, 15), (0, 30), (0, 45)), "shuffle", "toggle-shuffle", menu="shuffle")
    e += toggle((0, 28, 15), (179, 3), ((0, 0), (0, 15), (0, 30), (0, 45)), "repeat", "toggle-repeat", menu="repeat")
    e += element("button", (end(213), mid, end(213 + b), mid + b), normal=bar_area(b, 0), pressed=bar_area(b, b),
                 click="exit", tip="Close")  # fmt: skip
    return [BAR_WINDOW, *e]


def library_window(title_width):
    """The media library as TOML: the playlist's frame, with a title and a menu button of its own."""
    pl = lambda x, y, w, h: area("pledit", x, y, w, h)
    focus = lambda x: {"normal": pl(x, 0, 25, 20), "inactive": pl(x, 21, 25, 20)}
    v = "normal"
    e = [LIBRARY_WINDOW]
    e += element("image", (0, 0, 25, 20), v, **focus(0))
    e += element("image", (25, 0, "end-25", 20), v, **focus(127), fill="tile")
    e += element("image", ("end-25", 0, "end", 20), v, **focus(153))
    half = title_width // 2
    title = {"file": "ml/title.svg"}
    e += element("image", (f"center-{half}", 0, f"center+{title_width - half}", 20), v,
                 normal=title | {"area": [0, 0, title_width, 20]}, inactive=title | {"area": [0, 21, title_width, 20]})  # fmt: skip
    e += element("image", (0, 20, 12, "end-38"), v, normal=pl(0, 42, 12, 29), fill="tile")
    e += element("image", ("end-20", 20, "end", "end-38"), v, normal=pl(31, 42, 20, 29), fill="tile")
    e += element("image", (12, "end-38", "end-150", "end"), v, normal=pl(179, 0, 25, 38), fill="tile")
    # the bottom's left end without the Add, Del, Sel and Misc buttons
    e += element("image", (0, "end-38", 12, "end"), v, normal=pl(0, 72, 12, 38))
    e += element("image", ("end-150", "end-38", "end", "end"), v, normal=pl(126, 72, 150, 38))
    # the List button, labelled for the library
    e += element("image", ("end-44", "end-29", "end-22", "end-14"), v, normal="ml/menu.svg")
    e += element("drag", (0, 0, "end", 20), v, cursor="ptbar")
    e += element("button", ("end-11", 3, "end-2", 12), v, pressed=pl(52, 42, 9, 9), click="toggle-library-window",
                 cursor="pclose", tip="Close")  # fmt: skip
    thumb = {"normal": pl(52, 53, 8, 18), "pressed": pl(61, 53, 8, 18)}
    e += element("library", (12, 20, "end-7", "end-38"), v, menu="library", thumb=thumb)
    e += element("text", ("end-143", "end-28", "end-58", "end-22"), v, text="library-status")
    e += element("text", ("end-82", "end-14", "end-52", "end-8"), v, text="playlist-clock", hide="stopped")
    mini = ((5, 8, "previous"), (14, 8, "play"), (23, 8, "pause"), (32, 8, "stop"), (41, 8, "next"), (50, 9, "open-file"))
    for x, w, click in mini:
        e += element("button", (f"end-{150 - x}", "end-16", f"end-{150 - x - w}", "end-9"), v, click=click)
    e += element("button", ("end-44", "end-29", "end-22", "end-14"), v, menu_release="library", tip="Library Menu")
    e += element("resize", ("end-20", "end-20", "end", "end"), v, cursor="psize")
    return e
