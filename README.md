Pysnake

This is snake, but rebuilt in python.

However, the file currently has modules for easier UI building, and game modding. 
These are separated by a line of '=':
Mapping/Tiles - mapping/object data
BoardRules - contains the bulk of the game logic
GameHUD - handles drawing using the UI templates and mouse interaction

The rest at the bottom are supposed to be modules and json files, compacted in one file for submission:
GameData - Jason files for config and settings, also player data and perks
FileHandler - module for handling game data and generally the Jason files
UIComponents - templates for building ui surfaces faster, with functions and drawing handled









Currently the project only has the skeleton implementations for a few features that I would like to add, however they can also be viewed in the project under Mods:
Cards - modifies game scoring
Packs - allows for pseudo-random drawing of cards
StatCalc - utility class for function operators, used with Cards