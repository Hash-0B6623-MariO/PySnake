class Base:
    ''' Acts as the base class for all cards. '''
    def __init__(self, description:dict, rarity:int, limit:int) -> None:
        self.description = description  # name, pack(refered to as group in the code)
        self.limit = limit
        self._stack = 0  # Affects how many times a card procs
        self.rarity = rarity  # Affects how often a card appears

    def stack(self):
        ''' Increases the stack count by 1, up to the limit. '''
        if self._stack < self.limit:
            self._stack += 1
            return True
        else:
            return False
        