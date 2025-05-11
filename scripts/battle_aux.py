from settings import *
from game_data.effects_data import EFFECT_DATA

class StatusEffect:
    def __init__(self, name):
        self.name = EFFECT_DATA(name)
