from settings import *
from game_data.bchar_data import BATTLE_CHARACTER_DATA
from game_data.attack_data import ATTACK_DATA
from support import draw_bar

class Inventory:
    def __init__(self, display, entity, fonts, entity_frames):
        self.display = display
        self.fonts = fonts
        self.entity = entity
        self.frame_index = 0

        width = self.display.get_width()
        height = self.display.get_height()

        # frames
        self.icon_frames = entity_frames['icons']
        self.characters_frames = entity_frames['characters']
        self.ui_frames = entity_frames['ui']

        # tint
        self.tint_surf = pygame.Surface((pygame.display.get_window_size()))
        self.tint_surf.set_alpha(200)

        # dimensions
        self.main_rect = pygame.rect.Rect(width * 0.05, height * 0.05, width * 0.9, height * 0.9)

        # list
        self.visible_items = 6
        self.list_width = self.main_rect.width * 0.3
        self.item_height = self.main_rect.height / self.visible_items
        self.index = 0
        self.selected_index = None

        # max values
        self.max_stats = {}
        for data in BATTLE_CHARACTER_DATA.values():
            for stat, value in data['stats'].items():
                if stat != 'element':
                    if stat not in self.max_stats:
                        self.max_stats[stat] = value
                    else:
                        self.max_stats[stat] = value if value > self.max_stats[stat] else self.max_stats[stat]
        self.max_stats['health'] = self.max_stats.pop('max_health')
        self.max_stats['energy'] = self.max_stats.pop('max_energy')

    def input(self, keys):
        if keys[pygame.K_UP]:
            self.index -= 1
        if keys[pygame.K_DOWN]:
            self.index += 1
        if keys[pygame.K_z]:
            if self.selected_index != None:
                selected_monster = self.entity[self.selected_index]
                current_monster = self.entity[self.index]
                self.entity[self.index] = selected_monster
                self.entity[self.selected_index] = current_monster
                self.selected_index = None               
            else:
                self.selected_index = self.index

        self.index = self.index % len(self.entity)

    def display_list(self):
        pygame.draw.rect(self.display, COLORS['gray'], self.main_rect, 0, 12)
        v_offset = 0 if self.index < self.visible_items else -(self.index - self.visible_items + 1) * self.item_height

        for index, entity in self.entity.items():
            # color
            bg_color = COLORS['gray'] if self.index != index else COLORS['lighter']
            text_color = COLORS['white'] if self.selected_index != index else COLORS['gold']

            top = self.main_rect.top + index * self.item_height + v_offset
            item_rect = pygame.Rect(self.main_rect.left, top, self.list_width, self.item_height)
            
            text_surf = self.fonts['regular'].render(entity.name, False, text_color)
            text_rect = text_surf.get_rect(midleft = item_rect.midleft + vector(90 + 10, 0))

            icon_surf = self.icon_frames[entity.name]
            icon_rect = icon_surf.get_rect(center = item_rect.midleft + vector(45, 0))
            
            if item_rect.colliderect(self.main_rect):
                # check corner
                if item_rect.collidepoint(self.main_rect.topleft):
                    pygame.draw.rect(self.display, bg_color, item_rect, 0, 0, 12)
                elif item_rect.collidepoint(self.main_rect.bottomleft + vector(1, -1)):
                    pygame.draw.rect(self.display, bg_color, item_rect, 0, 0, 0, 0, 12, 0)
                else: 
                    # only this for sharp corner 
                    pygame.draw.rect(self.display, bg_color, item_rect)

                self.display.blit(text_surf, text_rect)
                self.display.blit(icon_surf, icon_rect)

            # lines
        for i in range(1, min(self.visible_items, len(self.entity))):
            y = self.main_rect.top + self.item_height * i
            left = self.main_rect.left
            right = self.main_rect.left + self.list_width - 5
            pygame.draw.line(self.display, COLORS['light-gray'], (left, y), (right, y))

        # shadow
        shadow_surf = pygame.Surface((4, self.main_rect.height))
        shadow_surf.set_alpha(100)
        self.display.blit(shadow_surf, (self.main_rect.left + self.list_width - 4, self.main_rect.top))

    def display_main(self, dt):
        # data
        entity = self.entity[self.index]

        # main rect
        rect = pygame.Rect(self.main_rect.left + self.list_width, self.main_rect.top, self.main_rect.width - self.list_width, self.main_rect.height)
        pygame.draw.rect(self.display, COLORS['darker'], rect, 0, 12, 0, 12, 0)

        # monster display
        top_rect = pygame.Rect(rect.topleft, (rect.width, rect.height * 0.4))
        pygame.draw.rect(self.display, COLORS[entity.element], top_rect, 0, 0, 0, 12)

        # monster animation
        self.frame_index += ANIMATION_SPEED * dt
        characters_surf = self.characters_frames[entity.name]['idle'][int(self.frame_index) % len(self.characters_frames[entity.name]['idle'])]
        characters_rect = characters_surf.get_rect(center = top_rect.center)
        self.display.blit(characters_surf, characters_rect)

        # name
        name_surf = self.fonts['bold'].render(entity.name, False, COLORS['white'])
        name_rect = name_surf.get_rect(topleft = top_rect.topleft + vector(10, 10))
        self.display.blit(name_surf, name_rect)

        # level
        level_surf = self.fonts['regular'].render(f'Lvl : {entity.level}', False, COLORS['white'])
        level_rect = level_surf.get_rect(bottomleft = top_rect.bottomleft + vector(10, -10))
        self.display.blit(level_surf, level_rect)

        # exp bar
        draw_bar(surface = self.display,
                 rect = pygame.Rect(level_rect.bottomleft, (100, 4)),
                 value = entity.xp,
                 max_value = entity.level_up,
                 color = COLORS['white'],
                 bg_color = COLORS['darker'])

        # element
        element_surf = self.fonts['regular'].render(entity.element, False, COLORS['white'])
        element_rect = element_surf.get_rect(bottomright = top_rect.bottomright + vector(-10, -10))
        self.display.blit(element_surf, element_rect)

        # health/energy
        bar_data = {
            'width': rect.width * 0.4,
            'height': 30,
            'top': top_rect.bottom + rect.width * 0.03,
            'left_side': rect.left + rect.width / 4 - 120,
            'right_side': rect.left + rect.width * 0.7 - 120
        }

        healthbar_rect = pygame.Rect((bar_data['left_side'], bar_data['top']), (bar_data['width'], bar_data['height']))
        draw_bar(surface = self.display,
                 rect = healthbar_rect,
                 value = entity.health,
                 max_value = entity.max_health,
                 color = COLORS['red'],
                 bg_color = COLORS['black'],
                 radius = 2)
        hp_text = self.fonts['regular'].render(f'HP: {int(entity.health)}/{int(entity.max_health)}',False ,COLORS['white'])
        hp_rect = hp_text.get_rect(midleft = healthbar_rect.midleft + vector(10, 0))
        self.display.blit(hp_text, hp_rect)

        manabar_rect = pygame.Rect((bar_data['right_side'], bar_data['top']), (bar_data['width'], bar_data['height']))
        draw_bar(surface = self.display,
                 rect = manabar_rect,
                 value = entity.energy,
                 max_value = entity.max_energy,
                 color = COLORS['blue'],
                 bg_color = COLORS['black'],
                 radius = 2)
        mana_text = self.fonts['regular'].render(f'MP: {int(entity.energy)}/{int(entity.max_energy)}',False ,COLORS['white'])
        mana_rect = mana_text.get_rect(midleft = manabar_rect.midleft + vector(10, 0))
        self.display.blit(mana_text, mana_rect)

        # info
        sides = {
            'left': healthbar_rect.left,
            'right': manabar_rect.left
        }
        info_height = rect.bottom - healthbar_rect.bottom

        # stats
        stats_rect = pygame.Rect(sides['left'], healthbar_rect.bottom, healthbar_rect.width, info_height).inflate(0, -75)
        stats_text_surf = self.fonts['regular'].render('Stats', False, COLORS['white'])
        stats_text_rect = stats_text_surf.get_rect(bottomleft = stats_rect.topleft)
        self.display.blit(stats_text_surf, stats_text_rect)

        entity_stats = entity.get_stats()
        stat_height = stats_rect.height / len(entity_stats)

        for index, (stat, value) in enumerate(entity_stats.items()):
            single_stat_rect = pygame.Rect(stats_rect.left, stats_rect.top + index * stat_height, stats_rect.width, stat_height)

            # icon
            icon_surf = self.ui_frames[stat]
            icon_rect = icon_surf.get_rect(midleft = single_stat_rect.midleft + vector(5, 0))
            self.display.blit(icon_surf, icon_rect)

            # text
            text_surf = self.fonts['regular'].render((f"{(str(stat).capitalize())} :"), False, COLORS['white'])
            text_rect = text_surf.get_rect(topleft = icon_rect.topleft + vector(20, -7))
            self.display.blit(text_surf, text_rect)

            # stats
            stat_surf = self.fonts['regular'].render(str(int(value)), False, COLORS['white'])
            stat_rect = text_surf.get_rect(topleft = text_rect.topright + vector(5, 0))
            self.display.blit(stat_surf, stat_rect)

            # bar
            bar_rect = pygame.Rect((text_rect.left, text_rect.bottom + 2), (single_stat_rect.width - (text_rect.left - single_stat_rect.left), 4))
            draw_bar(surface = self.display,
                 rect = bar_rect,
                 value = value,
                 max_value = self.max_stats[stat],
                 color = COLORS['white'],
                 bg_color = COLORS['black'])
            
        # abilities
        ability_rect = pygame.Rect(sides['right'], healthbar_rect.bottom, healthbar_rect.width, info_height).inflate(0, -75)
        ability_text_surf = self.fonts['regular'].render('Ability', False, COLORS['white'])
        ability_text_rect = ability_text_surf.get_rect(bottomleft = ability_rect.topleft)
        self.display.blit(ability_text_surf, ability_text_rect)

        for index, ability in enumerate(entity.get_abilities()):
            element = ATTACK_DATA[ability]['element']

            text_surf = self.fonts['regular'].render(ability, False, COLORS['black'])
            x = ability_rect.left + (index % 2) * ability_rect.width / 2
            y = 20 + ability_rect.top + int(index / 2) * (text_surf.get_height() + 20)
            rect = text_surf.get_rect(topleft = (x, y))
            pygame.draw.rect(self.display, COLORS[element], rect.inflate(10, 10), 0, 4)
            self.display.blit(text_surf, rect)

    def update(self, dt):
        self.display.blit(self.tint_surf, (0, 0))
        # pygame.draw.rect(self.display, 'white', self.main_rect)
        self.display_list()
        self.display_main(dt)
