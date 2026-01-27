import json

x, y = 3,3

print('+'.join(["h"*8, "g", "j"]))
print(["h"*8, "g"])
print(8**0)


data = {
        "window_background": (10, 10, 10),
        "font": "Game/Assets/Hud/Font/KiwiSoda.ttf",
        "center_position": 0,
        "screen_size": (800, 600)
        }
with open("test.json", "w") as file:
    json.dump(data, file, indent=1)
