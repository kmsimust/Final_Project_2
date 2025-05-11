import sys
import tkinter as tk
from settings import *
from support import *
from game_data.character_data import CHARACTER_DATA

from sprites import Sprite, AnimatedSprite, MonsterPatchSprite, BorderSprite, CollidableSprite, TransitionSprite
from entities import Player, Character
from groups import AllSprites
from dialog import DialogTree
from data_part import DataTkin
from battle_entity import BattleEntity
from menu import MenuWindow, MainMenuWindow
from inventory import Inventory
from battle import Battle

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Test')

        #pygame settings
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE, 32)
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.resize_display = self.display.copy()
        self.display_pos = DISPLAY_DEFULT_POS

        self.clock = pygame.time.Clock()
        self.timer = {}

        self.player_team = {
            0: BattleEntity('Player', 80),
        }

        self.dummy_team = {
            0: BattleEntity('Plumette', 90),
        }

        # groups
        self.all_sprites = AllSprites(self.display)
        self.collision_sprites = pygame.sprite.Group()
        self.character_sprites = pygame.sprite.Group()
        self.transition_sprites = pygame.sprite.Group()
        self.encounter_sprites = pygame.sprite.Group()

        self.import_menu()
        self.import_assets()
        self.setup(self.tmx_maps['Test1'], 'spawn')

        # transition / tint
        self.transition_target = None
        self.tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint_mode = 'untint'
        self.tint_progress = 0
        self.tint_direction = -1
        self.tint_speed = 600

        # overlays
        self.dialog = None
        self.state = 'menu'
        self.main_menu = MainMenuWindow(self.display, self.font, self.to_the_game, self.menu_frames)
        self.main_menu_open = True #defult: True
        self.menu = MenuWindow(self.display, self.font, self.off_menu, self.to_main_menu)
        self.menu_open = False #defult: False
        self.inventory = Inventory(self.display, self.player_team, self.font, self.battle_frames)
        self.inventory_open = False
        self.battle = None
        self.battle_defeated = False
    
    def import_menu(self):
        self.menu_frames = {
            'menu': load_folder_dict('menu')
        }

    def import_assets(self):
        self.tmx_maps = tmx_loader('data/maps')
        
        self.overworld_frames = {
            'water': load_folder('tilesets/water'),
            'coast': coast_loader(24, 12, 'tilesets/coast.png'),
            'characters': all_character_loader('characters'),
            'characters_icon': load_folder_dict('characters_icon')
        }

        self.battle_frames = {
            'icons': load_folder_dict('icons'),
            'characters': battle_character_loader(4, 2, 'monsters'),
            'ui': load_folder_dict('ui'),
            'list_art': load_folder_dict('battle_list_art'),
            'effects': load_folder_dict('effects'),
            'skill_art': load_folder_dict('skill_art'),
            'attacks': attack_loader('attacks')
        }

        # self.battle_frames['character']['name'] = None
        self.battle_frames['outlines'] = outline_creator(self.battle_frames['characters'], 4)

        self.background_frames = {
            'bg': load_folder_dict('backgrounds')
        }

        self.font = {
            'dialog': pygame.font.Font(join('graphics', 'fonts', 'PixeloidSans.ttf'), 30),
            'regular': pygame.font.Font(join('graphics', 'fonts', 'PixeloidSans.ttf'), 18),
            'small': pygame.font.Font(join('graphics', 'fonts', 'PixeloidSans.ttf'), 14),
            'bold': pygame.font.Font(join('graphics', 'fonts', 'dogicapixelbold.otf'), 20)
        }

        self.audio = audio_loader('audio')

    def setup(self, tmx_map, player_start_point):
        # clear
        for group in (self.all_sprites, self.collision_sprites, self.transition_sprites, self.character_sprites):
            group.empty()
        
        # Terrain
        for layer in ['Terrain', 'Terrain Top']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, WORLD_LAYERS['bg'])

        # Water
        for obj in tmx_map.get_layer_by_name('Water'):
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite((x,y), self.overworld_frames['water'], self.all_sprites, WORLD_LAYERS['water'])

        # Coast
        for obj in tmx_map.get_layer_by_name('Coast'):
            terrain = obj.properties['terrain']
            side = obj.properties['side']
            AnimatedSprite((obj.x, obj.y), self.overworld_frames['coast'][terrain][side], self.all_sprites, WORLD_LAYERS['bg'])

        # Objects
        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'top':
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, WORLD_LAYERS['top'])
            else:
                CollidableSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        # transition objects
        for obj in tmx_map.get_layer_by_name('Transition'):
            TransitionSprite((obj.x, obj.y), (obj.width, obj.height), (obj.properties['target'], obj.properties['pos']), self.transition_sprites)

        # Collision Objects
        for obj in tmx_map.get_layer_by_name('Collisions'):
            BorderSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        # Grass Patches
        for obj in tmx_map.get_layer_by_name('Monsters'):
            MonsterPatchSprite((obj.x, obj.y), obj.image, self.all_sprites , obj.properties['biome'])

        # Entities
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                if obj.properties['pos'] == player_start_point:
                    self.player = Player(
                        pos = (obj.x, obj.y),
                        frames = self.overworld_frames['characters']['player'],
                        groups = self.all_sprites,
                        facing_direction = obj.properties['direction'],
                        collision_sprites = self.collision_sprites)
            else:
                Character(
                        pos = (obj.x, obj.y),
                        name = obj.properties['graphic'],
                        frames = self.overworld_frames['characters'][obj.properties['graphic']],
                        frame_id = obj.properties['graphic'],
                        groups = (self.all_sprites, self.collision_sprites, self.character_sprites),
                        facing_direction = obj.properties['direction'],
                        character_data = CHARACTER_DATA[obj.properties['character_id']],
                        player = self.player,
                        create_dialog = self.create_dialog,
                        collision_sprites = self.collision_sprites,
                        radius = obj.properties['radius'],
                        nurse = obj.properties['character_id'] == 'Nurse')

    # game dialog

    def input(self):
        if not self.dialog and not self.battle:
            for character in self.character_sprites:
                if check_connections(100, self.player, character):
                    self.player.block()
                    character.change_facing_direction(self.player.rect.center)
                    self.create_dialog(character)
                    character.can_rotate = False

    def create_dialog(self, character):
        if not self.dialog:    
            self.dialog = DialogTree(character,
                                     self.overworld_frames['characters_icon'][character.id],
                                     self.player, self.all_sprites,
                                     self.font['dialog'],
                                     self.end_dialog)

    def end_dialog(self, character):
        self.dialog = None

        if character.nurse:
            for entity in self.player_team.values():
                entity.health = entity.max_health
                entity.energy = entity.max_energy
            self.battle_defeated = False
            self.player.unblock()

        elif not character.character_data['defeated'] and not self.battle_defeated:
            self.transition_target = Battle(
                display = self.display,
                player_team = self.player_team,
                opponent_team = character.team,
                entity_frames = self.battle_frames,
                bg_frames = self.background_frames['bg']['forest'],
                fonts = self.font,
                character = character,
                end_battle = self.end_battle,
                menuopen = self.menu_open
                )
            self.tint_mode = 'tint'
        else:
            self.player.unblock()

    # transition system

    def transition_check(self):
        sprites = [sprite for sprite in self.transition_sprites if sprite.rect.colliderect(self.player.hitbox)]
        if sprites:
            self.player.block()
            self.transition_target = sprites[0].target
            self.tint_surf = pygame.Surface((self.display.get_size()))
            self.tint_mode = 'tint'

    def tint_screen(self, dt):
        if self.tint_mode == 'untint':
            self.tint_progress -= self.tint_speed * dt

        if self.tint_mode == 'tint':
            self.tint_progress += self.tint_speed * dt
            
            if self.tint_progress >= 255:
                if type(self.transition_target) == Battle:
                    self.battle = self.transition_target
                elif self.transition_target == 'level':
                    self.battle = None
                elif self.main_menu_open:
                    pass
                else:
                    self.setup(self.tmx_maps[self.transition_target[0]], self.transition_target[1])
                self.tint_mode = 'untint'
                self.transition_target = None

        self.tint_progress = max(0, min(self.tint_progress, 255))
        self.tint_surf.set_alpha(self.tint_progress)
        self.display.blit(self.tint_surf, (0, 0))

    def end_battle(self, character, match):
        app = DataTkin()
        app.mainloop()
        self.transition_target = 'level'
        self.tint_mode = 'tint'
        if character and match:
            character.character_data['defeated'] = True
            self.create_dialog(character)
        else:
            self.battle_defeated = True
            self.player.unblock()

    def check_encounter(self):
        pass

    def encounter_active(self):
        pass

    def set_defeat(self):
        self.battle_defeated = True

    def to_main_menu(self):
        self.main_menu_open = True
        self.off_menu()

    def to_the_game(self):
        self.main_menu_open = False

    def off_menu(self):
        self.menu_open = False
        if self.battle:
            self.battle_defeated = False
        self.player.unblock()

    def resize(self, event):
        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE, 32)
        h_ratio = self.screen.get_height() / 3
        self.resize_display = pygame.Surface((h_ratio * 4, self.screen.get_height()))
        self.display_pos = ((self.screen.get_width() - self.resize_display.get_width()) / 2, 0)
        self.tint_surf = self.resize_display.copy()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.display.fill('black')

            # event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.VIDEORESIZE:
                    self.resize(event)

                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()

                    if self.main_menu_open:
                        self.main_menu.input(keys)

                    else:
                        if event.key == pygame.K_z and keys[pygame.K_z]:
                            self.input()

                        if event.key == pygame.K_v and keys[pygame.K_v]:
                            if not self.dialog and not self.battle:
                                self.inventory_open = not self.inventory_open
                                self.player.blocked = not self.player.blocked

                        if event.key == pygame.K_ESCAPE and keys[pygame.K_ESCAPE]:
                            self.player.blocked = not self.player.blocked
                            self.inventory_open = False
                            if self.battle:
                                self.battle.pause = True

                            self.menu_open = not self.menu_open

                        if self.dialog: self.dialog.input(keys)

                        if self.menu_open: self.menu.input(keys)

                        if self.inventory_open: self.inventory.input(keys)

                        if self.battle: self.battle.input(keys)

            # game logic
            if self.main_menu_open:
                self.main_menu.update(dt)
            else:
                if not self.battle:
                    self.transition_check()
                    self.all_sprites.update(dt)
                    self.all_sprites.draw(self.player) 

                # overlays
                if self.dialog: self.dialog.update(dt) 
                if self.inventory_open: self.inventory.update(dt)
                if self.battle: self.battle.update(dt)
                if self.menu_open: self.menu.update(dt)

            # scale
            self.screen.blit(self.resize_display, self.display_pos)
            self.tint_screen(dt)
            self.resize_display.blit(pygame.transform.scale(self.display, self.resize_display.get_size()), (0, 0))
            pygame.display.update()
            
game = Game()
game.run()
