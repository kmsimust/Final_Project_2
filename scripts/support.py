import pygame
import os
from os.path import join
from pygame.math import Vector2 as vector

from pytmx.util_pygame import load_pygame

BASE_IMG_PATH = 'graphics/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    return img

def load_folder(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

def load_folder_dict(path):
    frames ={}
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        surf = load_image(path + '/' + img_name)
        frames[img_name.split('.')[0]] = surf
    return frames

def load_tilemap(cols, rows, path):
	frames = {}
	surf = load_image(path)
	cell_width, cell_height = surf.get_width() / cols, surf.get_height() / rows
	for col in range(cols):
		for row in range(rows):
			cutout_rect = pygame.Rect(col * cell_width, row * cell_height,cell_width,cell_height)
			cutout_surf = pygame.Surface((cell_width, cell_height))
			cutout_surf.fill('green')
			cutout_surf.set_colorkey('green')
			cutout_surf.blit(surf, (0,0), cutout_rect)
			frames[(col, row)] = cutout_surf
	return frames

def coast_loader(cols, rows, *path):
	frame_dict = load_tilemap(cols, rows, *path)
	new_dict = {}
	terrains = ['grass', 'grass_i', 'sand_i', 'sand', 'rock', 'rock_i', 'ice', 'ice_i']
	sides = {
		'topleft': (0,0), 'top': (1,0), 'topright': (2,0), 
		'left': (0,1), 'right': (2,1), 'bottomleft': (0,2), 
		'bottom': (1,2), 'bottomright': (2,2)}
	for index, terrain in enumerate(terrains):
		new_dict[terrain] = {}
		for key, pos in sides.items():
			new_dict[terrain][key] = [frame_dict[(pos[0] + index * 3, pos[1] + row)] for row in range(0,rows, 3)]
	return new_dict

def character_loader(cols, rows, path):
	frame_dict = load_tilemap(cols, rows, path)
	new_dict = {}
	for row, direction in enumerate(('down', 'left', 'right', 'up')):
		new_dict[direction] = [frame_dict[(col, row)] for col in range(cols)]
		new_dict[f'{direction}_idle'] = [frame_dict[(0, row)]]
	return new_dict

def all_character_loader(path):
	new_dict = {}
	for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
			new_dict[img_name.split('.')[0]] = character_loader(4, 4, path + '/' + img_name)
	return new_dict

def tmx_loader(path):
	tmx_dict = {}
	for file_name in os.listdir(path):
		tmx_dict[file_name.split('.')[0]] = load_pygame(path + '/' + file_name)
	return tmx_dict

def battle_character_loader(cols, rows, path):
	battle_character_dict = {}
	for image in os.listdir(BASE_IMG_PATH + path):
		image_name = image.split('.')[0]
		battle_character_dict[image_name] = {}
		frame_dict = load_tilemap(cols, rows, path + '/' + image)
		for row, key in enumerate(('idle', 'attack')):
			battle_character_dict[image_name][key] = [frame_dict[(col, row)] for col in range(cols)]
	return battle_character_dict

def outline_creator(frame_dict, width):
	outline_frame_dict = {}
	for monster, monster_frames in frame_dict.items():
		outline_frame_dict[monster] = {}
		for state, frames in monster_frames.items():
			outline_frame_dict[monster][state] = []
			for frame in frames:
				new_surf = pygame.Surface(vector(frame.get_size()) + vector(width * 2), pygame.SRCALPHA)
				new_surf.fill((0, 0, 0, 0))
				white_frame = pygame.mask.from_surface(frame).to_surface()
				white_frame.set_colorkey('black')

				new_surf.blit(white_frame, (0, 0))
				new_surf.blit(white_frame, (width, 0))
				new_surf.blit(white_frame, (width * 2, 0))
				new_surf.blit(white_frame, (width * 2, width))
				new_surf.blit(white_frame, (width * 2, width * 2))
				new_surf.blit(white_frame, (width, width * 2))
				new_surf.blit(white_frame, (0, width * 2))
				new_surf.blit(white_frame, (0, width))
				outline_frame_dict[monster][state].append(new_surf)
	return outline_frame_dict

def attack_loader(path):
	attack_dict = {}
	for image in os.listdir(BASE_IMG_PATH + path):
		image_name = image.split('.')[0]
		attack_dict[image_name] = list(load_tilemap(4, 1, path + '/' + image).values())
	return attack_dict

def audio_loader(path):
	files = {}
	for file in os.listdir(path):
		file_name = file.split('.')[0]
		files[file_name] = pygame.mixer.Sound(path + '/' + file)
	return files

# game functions
def check_connections(radius, entity, target, tolerance = 30):
	relation = vector(target.rect.center) - vector(entity.rect.center)
	if relation.length() < radius:
		if entity.facing_direction == 'left' and relation.x < 0 and abs(relation.y) < tolerance or\
		   entity.facing_direction == 'right' and relation.x > 0 and abs(relation.y) < tolerance or\
		   entity.facing_direction == 'up' and relation.y < 0 and abs(relation.x) < tolerance or\
		   entity.facing_direction == 'down' and relation.y > 0 and abs(relation.x) < tolerance:
			return True

def draw_bar(surface, rect, value, max_value, color, bg_color, radius = 1):
	ratio = rect.width / max_value
	bg_rect = rect.copy()
	progess = max(0, min(rect.width, value * ratio))
	progess_rect = pygame.Rect(rect.topleft, (progess, rect.height))
	pygame.draw.rect(surface, bg_color, bg_rect, 0, radius)
	pygame.draw.rect(surface, color, progess_rect, 0, radius)
