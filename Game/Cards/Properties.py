''' 
This is where the cards are grouped and defined 
    Cards have 4 rarities: 0 - common, 1 - uncommon, 2 - rare, 3 - legendary
    Rarity Distribution = (common, uncommon, rare, legendary) as a ratio
'''

import json
from temp import Base

class Prop:
    '''
    All the card descriptions are stored in a json doc,
    this class helps read that, although all the actual
    in-game properties are defined here.
    '''
    @classmethod
    def read_card(cls, card:Base):
        ''' Reads the description dict and returns the corresponding class. '''
        category = card.description["group"]
        name = card.description["name"]
        return getattr(getattr(cls, category), name)()
    
    @classmethod
    def read_group(cls, group:str):
        ''' Returns the entire group class for spawning purposes. '''
        return getattr(cls, group)


class Prototype:
    amount = 8
    distribution = ()
    ''' This simply utilizes some of the features in the StatCalc for booster stacking '''
    class Fixed(Base):
        ''' Carries a flat boost, value is determined by stack '''
        def __init__(self):
            super().__init__(
                description={
                    "name": "CardBoost",
                    "group": "Prototype"
                },
                rarity=0,
                limit=10
                )
            
    
    class Multiplier(Base):
        def __init__(self):
            super().__init__(
                description={
                    "name": "CardMultiplier",
                    "group": "Prototype"
                },
                rarity=3,
                limit=1
                )
    
    cards = [
        Fixed,
    ]


class Starter:
    amount = 18
    distribution = ()
    class ValueUp(Base):
        def __init__(self):
            super().__init__(
                description={
                    "name": "ValueUp",
                    "group": "Starter"
                },
                rarity=0,
                limit=1
                )
            