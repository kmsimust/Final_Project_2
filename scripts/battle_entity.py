from game_data.attack_data import ATTACK_DATA
from game_data.bchar_data import BATTLE_CHARACTER_DATA
from random import randint

class BattleEntity:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.paused = False

        # stats
        self.base_stats = BATTLE_CHARACTER_DATA[name]['stats']

        self.stats = BATTLE_CHARACTER_DATA[name]['stats']

        self.max_health = self.base_stats['max_health'] + (200 * (self.level - 1))
        self.max_energy = self.base_stats['max_energy'] + (50 * (self.level - 1))

        self.element = self.base_stats['element']
        self.health = self.max_health
        self.energy = self.max_energy
        self.attack = self.base_stats['attack'] + (10 * (self.level - 1))
        self.defense = self.base_stats['defense'] + (2 * (self.level - 1))
        self.speed = self.base_stats['speed'] + (1 * (self.level - 1))
        self.recovery = self.base_stats['recovery'] + (10 * (self.level - 1))
        
        self.initiative = 0
        self.defending = False

        self.basic_attack = BATTLE_CHARACTER_DATA[name]['attack']
        self.abilities = BATTLE_CHARACTER_DATA[name]['abilities']

        self.effects = []

        # experience
        self.xp = 0
        self.level_up = self.level * 150
    
    def get_basic_attack(self):
        return [ability for lvl, ability in self.basic_attack.items()]
    
    def get_abilities(self):
        return [ability for lvl, ability in self.abilities.items()]
    
    def get_useable_abilities(self):
        return [ability for lvl, ability in self.abilities.items() if self.level >= lvl and\
                ATTACK_DATA[ability]['cost'] < self.energy]
        
    def get_info(self):
        return(
            ('HP', self.health, self.max_health),
            ('MP', self.energy, self.max_energy),
            ('AP', self.initiative, 100)
        )
    
    def get_stats(self):
        return {
            'health': self.max_health,
            'energy': self.max_energy,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'recovery': self.recovery
        }
    
    def get_hpap(self):
        return(
            ('HP', self.health, self.max_health),
            ('AP',self.initiative, 100)
        )
    
    def get_base_attack(self, attack):
        return self.attack * ATTACK_DATA[attack]['amount']
    
    def reduce_energy(self, attack):
        self.energy -= ATTACK_DATA[attack]['cost']

    def stats_limiter(self):
        self.health = max(0, min(self.health, self.max_health))
        self.energy = max(0, min(self.energy, self.max_energy))

    def update(self, dt):
        self.stats_limiter()
        if not self.paused:
            self.initiative += self.speed * dt * 2
