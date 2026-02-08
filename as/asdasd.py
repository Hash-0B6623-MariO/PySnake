import json

x, y = 3,3

print('+'.join(["h"*8, "g", "j"]))
print(["h"*8, "g"])
print(8**0)


data = {
        "window_background": (10, 10, 10),
        "font": "Game/Assets/Hud/Font/KiwiSoda.ttf",
        "center_window": 0,
        "screen_size": (800, 600)
        }

import os
print("Python is looking in:", os.getcwd())


with open("as/afas/test.json", "r") as file:
    print(json.load(file))
