import json
import pygame


# Process goes: 
#   Input -> Buffered -> onTick: Evaluate buffered inputs
#       Check: if in key_map[A],... -> 
#           Check: has an event in key_map[A] already activated? if not ->
#               Invoke function in action_map
class FileHandler:
    """ Encapsulates most of the data handling functions. """
    path_config:str = "PlayerData/Config.json"   # Type hinted because it causes an error when using string operations
    path_settings:str = "PlayerData/GameSettings"    # Mapping

    @classmethod
    def read_json(cls, path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"Error reading config file: {e}")
            return {}
    
    @classmethod
    def write_json(cls, data, path):
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error writing config file: {e}")

    @classmethod
    def load_keybinds(cls):
        """ Loads keybinds from config. """
        return cls.get_config()["keybinds"]

    @classmethod
    def get_config(cls):
        return cls.read_json(cls.path_config)
    
    @classmethod
    def getBoardDefault(cls, settings="/default"):
        path = cls.path_settings + settings + ".json"
        return cls.read_json(path)["board"]

    @classmethod
    def getGameDefault(cls, settings="/default"):
        path = cls.path_settings + settings + ".json"
        return cls.read_json(path)["settings"]



# Note: Messy but structure for mapping is 
# level ("user", "game", etc.) -> tag ("movement", "action", etc.) -> key-action mapping
#   * Tag is mainly used for the game input groupings
# Note that this project does not use multithreading, which explains delays
class KeyHandler:
    ''' Handles game runtime inputs '''
    def __init__(self, action_map: dict):
        self.setKeyMapping(FileHandler.load_keybinds(), action_map)   # Maps tags to key-action mappings
        self._action_mapping = action_map     # References the functions to string counterparts
        self.action_queue = {tag: [] for tag in self._key_mapping["game"].keys()}  # Action queue for game inputs

        # Strategy Dispatch Table: Map tags to internal logic methods
        self._evaluation_strategies = {
            "movement": self._eval_movement,
            "action": self._eval_standard
        }

    def setKeyMapping(self, keybinds: dict, action_map: dict):
        """ Takes that raw keybind structure and produces a mapping of tags to key-action mappings. """
        keymap = {}
        # Game
        for level, group in keybinds.items():
            current_group = {}
            for tag, mapping in group.items():
                current_group[tag] = {pygame.key.key_code(key): action_map[action] for key, action in mapping.items()}
            keymap[level] = current_group
        self._key_mapping = keymap

    def getActionMap(self):
        """ Returns the action map for use, atm mainly on the GameHUD callbacks. """
        return self._action_mapping

    def evaluate_queue(self):
        """ Entry point for the recursive evaluation loop. """
        # TODO: It does evaluate every tick, but might be negligible
        for tag, queue in self.action_queue.items():
            if queue:
                self._evaluation_strategies[tag](list(reversed(queue)))
                queue.clear()

    def find_key(self, key):
        """ Utility to find the tag and action for a given key for the game inputs."""
        for tag, mapping in self._key_mapping["game"].items():
            if key in mapping.keys():
                return {"tag":tag,"action":mapping[key]}
        return False

    def handle_keydown(self, key):
        """ Buffers the key. """
        if key in self._key_mapping["user"].keys():
            self._key_mapping["user"][key]()
        else:
            # This branch handles game inputs
            input = self.find_key(key)
            if input:
                self.action_queue[input["tag"]].append(input["action"])

    # --- Strategy Implementations ---
    def _eval_movement(self, queue):
        """Movement rule: Only execute the latest movement found in the tick."""
        # Would like to allow for double queuing, something like a 100ms wait, where the 2nd input is queued but not executed until the next tick.
        try:
            check = queue.pop(0)()  # Check if the action is valid (e.g., not a 180 turn)
            return check if check else self._eval_movement(queue)  # Execute the action
        except IndexError:
            return False  # No valid movement found

    # Placeholder
    def _eval_standard(self, action, tag, processed_tags):
        """Standard actions: Allow multiple, but perhaps only once per tag per tick."""
        action()
    


