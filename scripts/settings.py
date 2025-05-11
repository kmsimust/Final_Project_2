import pygame
from pygame.math import Vector2 as vector 
from sys import exit


WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
DISPLAY_WIDTH, DISPLAY_HEIGHT = 960, 720
DISPLAY_RATIO = (4, 3)
DISPLAY_DEFULT_POS = ((WINDOW_WIDTH - DISPLAY_WIDTH) / 2, 0)

TILE_SIZE = 64 
ANIMATION_SPEED = 6
BATTLE_OUTLINE_WIDTH = 4
FPS = 60

COLORS = {
	'white': '#f4fefa', 
	'pure white': '#ffffff',
	'gray': '#3a373b',
	'gold': '#ffd700',
	'light-gray': '#4b484d',
    'lighter': '#c8c8c8',
    'darker': '#2b292c',
	'black': '#000000', 
	'red': '#f03131',
	'blue': '#66d7ee',
    'green': '#64a990',
    
	'normal': '#f4fefa',
	'fire':'#f8a060',
	'water':'#50b0d8',
	'plant': '#64a990',
    'dark': '#2b292c',
	'light': '#fff085',
    
	'block': '#0000cd',
	'heal': '#00ff00',
    'burn': 'ff4500',
    'poison': '9400d3',
    'frost': '00ffff',
}

WORLD_LAYERS = {
	'water': 0,
	'bg': 1,
	'shadow': 2,
	'main': 3,
	'top': 4
}

BATTLE_POSITIONS = {
	'left': {'vanguard': (380, 406), 'midtop': (250, 356), 'midbot': (250, 456), 'rear': (100, 406)},
    'left_rear': {'rear': (100, 456)},
	'right': {'vanguard': (580, 406), 'mid': (710, 356), 'rear': (860, 406)},
    'right_rear': {'rear': (860, 456)},
}

BATTLE_LAYERS =  {
	'outline': 0,
	'name': 1,
	'enemy': 2,
	'effects': 3,
	'overlay': 4
}

BATTLE_CHOICES = {
	'full': {
        'detail':  {'icon': 'hand'},
		'attack':  {'icon': 'sword'},
		'defend': {'icon': 'shield'},
        'skills':  {'icon': 'skills'}
		},
	
	'limited': {
		'fight':  {'pos' : vector(30, -40), 'icon': 'sword'},
		'defend': {'pos' : vector(40, 0), 'icon': 'shield'},
		'switch': {'pos' : vector(30, 40), 'icon': 'arrows'}}
}
