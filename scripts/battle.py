from settings import *
from sprites import BattleSprite, BattleArtSprite, BattleNameSprite\
    , BattleEffectSprite, BattleStatsSprite, BattleEnemy, EntityOutlineSprite, AttackSprite, IndicatorSprite
from groups import BattleSprites
from support import draw_bar
from clock import Timer
from data_part import DataCollector
from game_data.attack_data import ATTACK_DATA
from game_data.effects_data import EFFECT_DATA
from random import choice

class Battle:
    def __init__(self, display, player_team, opponent_team,
                 entity_frames, bg_frames, fonts, character,
                 end_battle, menuopen):
        # general
        self.display = display
        self.bg_frames = bg_frames
        self.entity_frames = entity_frames
        self.fonts = fonts
        self.team_data = {
            'player': player_team,
            'opponent': opponent_team
            }
        self.timers = {
            'pre battle': Timer(500, func = lambda: self.update_all_entity('resume')),
            'opponent delay': Timer(600, func = self.opponent_attack)
        }
        self.battle_over = False
        self.character = character

        self.end_battle = end_battle
        
        # groups
        self.battle_sprites = BattleSprites(self.display)
        self.player_sprites = pygame.sprite.Group()
        self.opponent_sprites = pygame.sprite.Group()

        self.data_collector = DataCollector('battle')
        self.battle_result = None
        self.battle_result_open = False

        # controls
        self.detail_box = False
        self.current_entity = None
        self.selection_mode = None
        self.selection_side = 'player'
        self.selected_attack = None
        self.selected_target = None
        self.battle_pause = False
        self.menu_open = menuopen
        self.indexes = {
            'general': 1,
            'entity': 0,
            'skills': 0,
            'switch': 0,
            'target': 0,
        }

        # main rect
        width = self.display.get_width()
        height = self.display.get_height()

        # list
        self.main_surf = pygame.Surface((width, 220), pygame.SRCALPHA)
        self.main_surf.fill((0, 0, 0, 0))
        self.visible_items = 4
        self.item_height = 50

        # in-battle list
        self.list_width = 768
        self.list_height = 434
        self.list_visible_attacks = 4
        self.list_item_height = 96
        self.list_main_rect = pygame.rect.Rect((106, 82), (self.list_width - 20, self.list_height - 20))

        # transition / tint
        self.transition_target = None
        self.tint_surf = pygame.Surface(self.display.get_size())
        self.tint_mode = 'untint'
        self.tint_progress = 0
        self.tint_direction = -1
        self.tint_speed = 600
        self.tint_done = True
        
        self.setup()

        self.update_all_entity('pause')
        self.timers['pre battle'].activate()    

    def setup(self):
        # create entity
        for side, entites in self.team_data.items():
            num = 3 if self.team_data == 'player' else 2
            for index, entity in {k:v for k,v in entites.items() if k <= num}.items():
                self.create_entity(entity, index, index, side)

            # remove opponent data
            for i in range(len(self.opponent_sprites)):
                del self.team_data['opponent'][i]

    def create_entity(self, entity, index, pos_index, team):
        entity.paused = False
        frames = self.entity_frames['characters'][entity.name]
        outline_frames = self.entity_frames['outlines'][entity.name]
        
        if team == 'player':
            pos = list(BATTLE_POSITIONS['left'].values())[pos_index]
            groups = (self.battle_sprites, self.player_sprites)
            frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames] for state, frames in frames.items()}
            outline_frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames] for state, frames in outline_frames.items()}
        else:
            pos = list(BATTLE_POSITIONS['right'].values())[pos_index]
            groups = (self.battle_sprites, self.opponent_sprites)

        battle_sprite = BattleSprite(pos, frames, groups, entity, index, pos_index, team, self.apply_attack, self.create_entity)
        EntityOutlineSprite(battle_sprite, self.battle_sprites, outline_frames)

        # ui
        if team == 'player':
            BattleArtSprite(index, battle_sprite, self.battle_sprites, self.entity_frames['list_art'][entity.name])
            BattleNameSprite(index, battle_sprite, self.battle_sprites, self.fonts['regular'])
            if len(battle_sprite.entity.effects) > 0: BattleEffectSprite(index, battle_sprite, self.battle_sprites, self.entity_frames['effects'])
            BattleStatsSprite(index, battle_sprite, self.battle_sprites, self.fonts['regular'])
        else:
            BattleEnemy(battle_sprite.rect.midbottom + vector(0, 0), battle_sprite, self.battle_sprites, self.fonts['small'])

    def list_box(self):
        self.display.blit(self.bg_frames, (0, 0))
        pygame.draw.rect(self.display, COLORS['pure white'], self.main_surf.get_rect(topleft = (0, 500)), 0, 4)

    def input(self, keys):
        if self.selection_mode and self.current_entity and not self.timers['pre battle'].active:

            match self.selection_mode:
                case 'general': limiter = len(BATTLE_CHOICES['full'])
                case 'skills': limiter = len(self.current_entity.entity.get_abilities()) if\
                      len(self.current_entity.entity.get_abilities()) >= 1 else 1
                case 'target': limiter = len(self.opponent_sprites) if self.selection_side == 'opponent' else len(self.player_sprites)

            if keys[pygame.K_DOWN]:
                self.indexes[self.selection_mode] = (self.indexes[self.selection_mode] + 1) % limiter
            if keys[pygame.K_UP]:
                self.indexes[self.selection_mode] = (self.indexes[self.selection_mode] - 1) % limiter

            if keys[pygame.K_z]:
                if self.selection_mode == 'target':
                    sprite_group = self.opponent_sprites if self.selection_side == 'opponent' else self.player_sprites
                    sprites = {sprite.pos_index: sprite for sprite in sprite_group}
                    entity_sprite = sprites[list(sprites.keys())[self.indexes['target']]]

                    if self.selected_attack:
                        self.current_entity.activate_attack(entity_sprite, self.selected_attack)
                        self.selected_attack = None
                        self.current_entity = None
                        self.selection_mode = None

                if self.selection_mode == 'details':
                    self.update_all_entity('paused')
                    if self.detail_box:
                        self.detail_box = False
                        if self.selection_mode in ('skills', 'target', 'details'):
                            self.selection_mode = 'general'

                if self.selection_mode == 'skills':
                    self.selection_mode = 'target'
                    self.selected_attack = self.current_entity.entity.get_abilities()[self.indexes['skills']]
                    self.selection_side = ATTACK_DATA[self.selected_attack]['target']

                if self.selection_mode == 'general':
                    if self.indexes['general'] == 0:
                        self.selection_mode = 'details'

                    if self.indexes['general'] == 1:
                        self.selection_mode = 'target'
                        self.selected_attack = self.current_entity.entity.get_basic_attack()[0]
                        self.selection_side = ATTACK_DATA[self.selected_attack]['target']

                    if self.indexes['general'] == 2:
                        self.current_entity.activate_attack(self.current_entity, 'block')
                        self.current_entity = None
                        self.selection_mode = None

                    if self.indexes['general'] == 3:
                        self.selection_mode = 'skills'

                self.indexes = {k: 0 for k in self.indexes}
                self.indexes['general'] = 1

            if keys[pygame.K_x]:
                if self.selection_mode in ('skills', 'target', 'details'):
                    self.selection_mode = 'general'

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    # battle system
    def check_active(self):
        for entity_sprite in self.player_sprites.sprites() + self.opponent_sprites.sprites():
            if entity_sprite.entity.initiative >= 100 and not entity_sprite.entity.health < 0:
                self.activate_effects(entity_sprite)
                if not entity_sprite.entity.health < 0 :
                    entity_sprite.entity.defending = False
                    self.update_all_entity('pause')
                    entity_sprite.entity.initiative = 0
                    entity_sprite.set_highlight(True)
                    self.current_entity = entity_sprite
                    if self.player_sprites in entity_sprite.groups():
                        self.selection_mode = 'general'

                    else:
                        self.timers['opponent delay'].activate()

    def update_all_entity(self, option):
        for entity_sprite in self.player_sprites.sprites() + self.opponent_sprites.sprites():
            entity_sprite.entity.paused = True if option == 'pause' else False

    def check_death(self):
        for entity_sprite in self.opponent_sprites.sprites() + self.player_sprites.sprites():
            if entity_sprite.entity.health <= 0:
                entity_sprite.entity.initiative = 0
                if self.player_sprites in entity_sprite.groups():
                    active_entity = [(entity_sprite.index, entity_sprite.entity) for entity_sprite in self.player_sprites.sprites()]
                    avalible_entity = [(index, entity) for index, entity in self.team_data['player'].items() if entity.health > 0 and\
                                       (index, entity) not in active_entity]
                    if avalible_entity:
                        next_entity = [(entity, index, entity_sprite.pos_index, 'player') for index, entity in avalible_entity][0]
                    else:
                        next_entity = None
                else:
                    # replace
                    next_entity = (list(self.team_data['opponent'].values())[0], entity_sprite.index, entity_sprite.pos_index, 'opponent') if\
                    self.team_data['opponent'] else None
                    if self.team_data['opponent']:
                        del self.team_data['opponent'][min(self.team_data['opponent'])]
                    # kill
                entity_sprite.delayed_kill(next_entity)

    def opponent_attack(self):
        if not self.current_entity.entity.health < 0:
            if len(self.current_entity.entity.get_useable_abilities()) == 0:
                ability = choice(self.current_entity.entity.get_basic_attack() + ['block'])
            else:
                ability = choice(self.current_entity.entity.get_useable_abilities() + ['block'])

            side = ATTACK_DATA[ability]['target']
            if side == 'player':
                random_target = choice(self.opponent_sprites.sprites())
            elif side == 'self':
                random_target = self.current_entity
            else:
                random_target = choice(self.player_sprites.sprites())
            self.current_entity.activate_attack(random_target, ability)

    def apply_attack(self, sentity, target_sprite, attack, amount, team):
        AttackSprite(target_sprite.rect.center,
                     self.entity_frames['attacks'][ATTACK_DATA[attack]['animation']],
                     self.battle_sprites)
        
        attack_element = ATTACK_DATA[attack]['element']
        target_element = target_sprite.entity.element
        keyword = ATTACK_DATA[attack]['keyword']

        if ATTACK_DATA[attack]['target'] == 'opponent':
            attack_type = 'attack'
        else:
            attack_type = 'buff'

        attack_dealt = 0
        attack_recieve = 0

        if  attack_element == 'fire' and target_element == 'plant' or\
            attack_element == 'water' and target_element == 'fire' or \
            attack_element == 'plant' and target_element == 'water':
            amount *= 2

        if  attack_element == 'fire' and target_element == 'water' or\
            attack_element == 'water' and target_element == 'plant' or \
            attack_element == 'plant' and target_element == 'fire':
            amount *= 0.5

        target_defense = target_sprite.entity.defense
        
        if keyword == 'block':
            target_sprite.entity.defending = True

        if target_sprite.entity.defending:
            target_defense *= 2
        dealing = int(amount - target_defense)
        if keyword == 'heal':
            dealing = dealing
        else:
            dealing = max(0, min(dealing, amount))

        if team == 'player' and attack_type == 'attack':
            attack_dealt = dealing
        elif team == 'opponent' and attack_type == 'attack':
            attack_recieve = dealing

        # update
        target_sprite.entity.health -= dealing
        IndicatorSprite(target_sprite.rect.center, self.fonts['dialog'],
                        self.battle_sprites, dealing,
                        target_sprite.entity.defending, keyword)
        
        if team == 'player':
            data = {'Entity': sentity.name,
                    'Side': team,
                    'Deal to': target_sprite.entity.name,
                    'Action': attack,
                    'Action-Type': attack_type,
                    'Action-Element': attack_element,
                    'Damage Dealt': attack_dealt,
                    'Damage Recive': attack_recieve,
                    'Current-Health': sentity.health,
                    'Current-Mana': sentity.energy,
                    'Mana Useage': ATTACK_DATA[attack]['cost']}
        
            self.data_collector.collect_data(data)
        
        self.check_death()

        # resume
        self.update_all_entity('resume')

    def check_end_battle(self):
        # opponent
        if len(self.opponent_sprites) == 0 and not self.battle_over:
            self.update_all_entity('pause')
            self.battle_over = True
            self.data_collector.save_data()       
            for entity in self.team_data['player'].values():
                entity.initiative = 0
            if not self.battle_result and self.tint_done:
                self.end_battle(self.character, True)
        # player
        if len(self.player_sprites) == 0 and not self.battle_over:
            self.update_all_entity('pause')
            self.battle_over = True
            self.end_battle(self.character, False)
            for entity in self.team_data['player'].values():
                entity.initiative = 0

    def activate_effects(self, current_entity):
        pass
        # for effect in current_entity.entity.effects:
        #     print(effect)
        #     effect[1] -= 1
        #     if effect[1] <= 0:
        #         current_entity.entity.effects.pop(effect[1])

        # print(current_entity.entity.effects)

    def check_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if event.key == pygame.K_ESCAPE and keys[pygame.K_ESCAPE]:
                
                    self.menu_open = not self.menu_open
                    if self.menu_open:
                        self.update_all_entity('pause')
                    else:
                        self.update_all_entity('resume')

    def exit_result(self):
        self.tint_mode = 'untint'
        self.tint_done = False
        self.battle_result = None

    # ui
    def draw_ui(self):
        if self.current_entity:
            if self.selection_mode == 'details':
                self.draw_detail()
            if self.selection_mode == 'general':
                self.draw_general()
            if self.selection_mode == 'skills':
                self.draw_skills()

    def draw_general(self):
        if self.current_entity.team == 'player':
            for index, (option, data_dict) in enumerate(BATTLE_CHOICES['full'].items()):
                if index == self.indexes['general']:
                    surf = self.entity_frames['ui'][f"{data_dict['icon']}_highlight"]
                else:
                    surf = pygame.transform.grayscale(self.entity_frames['ui'][data_dict['icon']])
                if self.indexes['general'] in [index - 1, index, index + 1]:
                    if self.indexes['general'] == index:
                        offset = vector(0, 0)
                    elif self.indexes['general'] == index - 1:
                        offset = vector(-10, 40)
                    elif self.indexes['general'] == index + 1:
                        offset = vector(-10, -40)
                    rect = surf.get_rect(center = self.current_entity.rect.midright + offset)
                    self.display.blit(surf, rect)

    def draw_detail(self):
        self.detail_box = True
        bg_rect = pygame.rect.Rect((96, 72), (500, 500))
        pygame.draw.rect(self.display, COLORS['gray'], bg_rect, 0, 5)
        # print(self.current_entity.entity.name)

    def draw_skills(self):
        # data
        abilities = self.current_entity.entity.get_abilities()

        # bg
        v_offset = 0 if self.indexes['skills'] < self.list_visible_attacks else -(self.indexes['skills'] - self.list_visible_attacks + 1) * 106

        bg_rect = pygame.rect.Rect((96, 72), (self.list_width, self.list_height))
        pygame.draw.rect(self.display, COLORS['light-gray'], bg_rect, 0, 5)

        # skills
        for index, ability in enumerate(abilities):
            selected = index == self.indexes['skills']

            # text
            bg_color = COLORS['gray'] if selected else COLORS['light-gray']
            text_color = COLORS['white'] if selected else COLORS['black']

            top = self.list_main_rect.top + index * 106 + v_offset
            item_rect = pygame.Rect((self.list_main_rect.topleft[0], top), (self.list_width  - 20, self.list_item_height))
            
            icon_surf = self.entity_frames['skill_art']['temp']
            icon_rect = icon_surf.get_rect(midleft = item_rect.midleft + vector(10, 0))

            ability_text = str(ability).title()
            text_surf = self.fonts['regular'].render(ability_text, False, text_color)
            text_rect = text_surf.get_rect(midleft = icon_rect.midright + vector(15, -20))

            element = ATTACK_DATA[ability]['element']
            element_surf = self.fonts['regular'].render(str(element).title(), False, COLORS[element])
            element_rect = element_surf.get_rect(midleft = text_rect.midright + vector(15, 0))

            mana_use = f"Cost :{str(int(abs(ATTACK_DATA[ability]['cost'])))} MP"
            mana_surf = self.fonts['regular'].render(mana_use, False, text_color)
            mana_rect = mana_surf.get_rect(midleft = element_rect.midright + vector(15, 0))

            desc_text = f"{ATTACK_DATA[ability]['detail1']}" + ' ' +\
                        f"{str(int(abs(ATTACK_DATA[ability]['amount']) * 100))}%" + ' ' +\
                        f"{ATTACK_DATA[ability]['detail2']}"
            desc_surf = self.fonts['regular'].render(desc_text, False, text_color)
            desc_rect = desc_surf.get_rect(midleft = icon_rect.midright + vector(15, 20))

            # draw
            if item_rect.colliderect(self.list_main_rect):
                pygame.draw.rect(self.display, bg_color, item_rect, 0, 5)
            
                for surf, rect in ((icon_surf, icon_rect), (text_surf, text_rect), (element_surf, element_rect),
                                   (mana_surf, mana_rect), (desc_surf, desc_rect)):
                    self.display.blit(surf, rect)

    def draw_switch(self):
        # data
        active_entity = [(entity_sprite.index, entity_sprite.entity) for entity_sprite in self.player_sprites]
        self.avalible_entity = {index: entity for index, entity in self.team_data['player'].items() if\
                            (index, entity) not in active_entity and entity.health > 0}

        # bg
        v_offset = 0 if self.indexes['switch'] < self.list_visible_attacks else -(self.indexes['switch'] - self.list_visible_attacks + 1) * 106

        bg_rect = pygame.rect.Rect((96, 72), (self.list_width, self.list_height))
        pygame.draw.rect(self.display, COLORS['light-gray'], bg_rect, 0, 5)

        # skills
        for index, entity in enumerate(self.avalible_entity.values()):
            selected = index == self.indexes['switch']

            # text
            bg_color = COLORS['gray'] if selected else COLORS['lighter']
            text_color = COLORS['white'] if selected else COLORS['black']

            top = self.list_main_rect.top + index * 106 + v_offset
            item_rect = pygame.Rect((self.list_main_rect.topleft[0], top), (self.list_width  - 20, self.list_item_height))
            
            icon_surf = pygame.transform.scale(self.entity_frames['list_art'][entity.name], (234, 78))
            icon_rect = icon_surf.get_rect(midleft = item_rect.midleft + vector(10, 0))

            text = f"{str(entity.name).title()}   (Level: {str(entity.level)})"
            text_surf = self.fonts['regular'].render(text, False, text_color)
            text_rect = text_surf.get_rect(midleft = icon_rect.midright + vector(15, -20))

            hp_text = f"HP :{str(entity.health)}/{str(entity.get_stat('max_health'))}"
            hp_text_surf = self.fonts['regular'].render(hp_text, False, COLORS['white'])
            hp_text_rect = hp_text_surf.get_rect(topleft = icon_rect.midright + vector(20, -5))

            mp_text = f"MP :{str(entity.energy)}/{str(entity.get_stat('max_energy'))}"
            mp_text_surf = self.fonts['regular'].render(mp_text, False, COLORS['white'])
            mp_text_rect = mp_text_surf.get_rect(topleft = icon_rect.midright + vector(20, 20))

            # draw
            if item_rect.colliderect(self.list_main_rect):
                pygame.draw.rect(self.display, bg_color, item_rect, 0, 5)
                for surf, rect in ((icon_surf, icon_rect), (text_surf, text_rect)):
                    self.display.blit(surf, rect)
                
                hp_rect = pygame.Rect((icon_rect.midright + vector(15, -5)), (200, 20))
                draw_bar(self.display, hp_rect, entity.health, entity.max_health, COLORS['red'], COLORS['black'], 2)
                hp_rect = pygame.Rect((icon_rect.midright + vector(15, 20)), (200, 20))
                draw_bar(self.display, hp_rect, entity.energy, entity.max_energy, COLORS['blue'], COLORS['black'], 2)
                
                for surf, rect in ((hp_text_surf, hp_text_rect), (mp_text_surf, mp_text_rect)):
                    self.display.blit(surf, rect)

    def update(self, dt):
        if not self.battle_pause:
            self.list_box()
            self.update_timers()
            self.check_end_battle()
            self.check_active()
            self.battle_sprites.update(dt)       
            self.battle_sprites.draw(self.current_entity, self.selection_side,
                                    self.selection_mode, self.indexes['target'], self.player_sprites, self.opponent_sprites)
            self.draw_ui()
