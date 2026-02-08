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
        """ Loads keybinds from a JSON file and returns a structured dict. """
        config = cls.get_config()
        keybinds = {}
        for level, group in config["keybinds"].items():
            current_group = {} 
            print(group)
            for tag, mapping in group.items():
                current_group[tag] = {getattr(pygame, key): action for key, action in mapping.items()}
            keybinds[level] = current_group
        return keybinds
    
    @classmethod
    def get_config(cls):
        return cls.read_json(cls.path_config)
    
    @classmethod
    def get_settings(cls, settings="/default"):
        path = cls.path_settings + settings + ".json"
        return cls.read_json(path)



class KeyHandler:
    ''' Handles game runtime inputs '''
    def __init__(self, keybinds: dict, action_map: dict):
        self._key_mapping = keybinds 
        self._action_mapping = action_map     # References the functions to string counterparts
        self.action_queue = {key: [] for key in self._action_mapping.keys()}  # Map of key to list of actions

        # Strategy Dispatch Table: Map tags to internal logic methods
        self._evaluation_strategies = {
            "movement": self._eval_movement,
            "action": self._eval_standard
        }

    def getActionMap(self):
        return self._action_mapping

    def setKeyMapping(self, keybinds: dict):
        self._key_mapping = keybinds 

    def evaluate_queue(self):
        """ Entry point for the recursive evaluation loop. """
        # TODO: It does evaluate every tick, but might be negligible
        for tag, queue in self.action_queue.items():
            if queue:
                self._evaluation_strategies[tag](list(reversed(queue)))
                queue.clear()

    def find_key(self, key):
        """Utility to find the tag and action for a given key."""
        for tag, mapping in self._key_mapping.items():
            if key in mapping.keys():
                return {"tag":tag,"action":mapping[key]}
        return False

    def handle_keydown(self, key):
        """ Buffers the key. """
        if key in self._key_mapping["user"].keys():
            self._action_mapping[key]()
        else:
            input = self.find_key(key)
            if input:
                self.action_queue[input["tag"]].append(input["action"])

    # --- Strategy Implementations ---
    def _eval_movement(self, queue):
        """Movement rule: Only execute the latest movement found in the tick."""
        try:
            check = queue.pop(0)()  # Check if the action is valid (e.g., not a 180 turn)
            return check if check else self._eval_movement(queue)  # Execute the action
        except IndexError:
            return False  # No valid movement found

    # Placeholder
    def _eval_standard(self, action, tag, processed_tags):
        """Standard actions: Allow multiple, but perhaps only once per tag per tick."""
        action()
    


