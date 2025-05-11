from settings import *
from game_data.attack_data import ATTACK_DATA
from random import uniform
from support import draw_bar
from clock import Timer

# overworld
class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups ,z=WORLD_LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.y_sort = self.rect.centery
        self.hitbox = self.rect.copy()

class BorderSprite(Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy()

class TransitionSprite(Sprite):
    def __init__(self, pos, size, target, groups):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.target = target

class CollidableSprite(Sprite):	
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.inflate(-self.rect.width / 2, -self.rect.height * 0.6)

class MonsterPatchSprite(Sprite):
    def __init__(self, pos, surf, groups, biome):
        super().__init__(pos, surf, groups, z=WORLD_LAYERS['main' if biome != 'sand' else 'bg'])
        self.biome = biome
        self.y_sort -= 40

class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups, z=WORLD_LAYERS['main']):
        self.frame_index = 0
        self.frames = frames
        super().__init__(pos, self.frames[self.frame_index], groups, z)

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, dt):
        self.animate(dt)

# battle
class BattleSprite(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, entity, index, pos_index, team,
                 apply_attack, create_entity):
        # data
        self.index = index
        self.pos_index = pos_index
        self.entity = entity
        self.entity.paused = True
        self.team = team
        self.frame_index = 0
        self.frames = frames
        self.state = 'idle'
        self.animation_speed = ANIMATION_SPEED + uniform(-1, 1)
        self.z = BATTLE_LAYERS['enemy']
        self.highlight = False
        self.target_sprite = None
        self.current_attack = None
        
        self.apply_attack = apply_attack
        self.create_entity = create_entity

        # sprite setup
        super().__init__(groups)
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_rect(midbottom = pos)

        # timers
        self.timers = {
            'remove highlight': Timer(500, func=lambda: self.set_highlight(False)),
            'kill': Timer(600, func=self.destroy)
        }

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.state == 'attack' and self.frame_index >= len(self.frames['attack']):
            self.apply_attack(self.entity, self.target_sprite, self.current_attack, self.entity.get_base_attack(self.current_attack), self.team)
            self.state = 'idle'

        self.adjusted_frame_index = int(self.frame_index)% len(self.frames[self.state])
        self.image = self.frames[self.state][self.adjusted_frame_index]

        if self.highlight:
            white_surf = pygame.mask.from_surface(self.image).to_surface()
            white_surf.set_colorkey('black')
            self.image = white_surf

    def set_highlight(self, value):
        self.highlight = value
        if value:
            self.timers['remove highlight'].activate()

    def activate_attack(self, target_sprite, attack):
        self.state = ATTACK_DATA[attack]['movesets']
        self.frame_index = 0
        self.target_sprite = target_sprite
        self.current_attack = attack
        self.entity.reduce_energy(attack)

    def delayed_kill(self, new):
        if not self.timers['kill'].active:
            self.next_entity_data = new
            self.timers['kill'].activate()

    def destroy(self):
        if self.next_entity_data:
            self.create_entity(*self.next_entity_data)
        self.kill()

    def update(self, dt):
        for timer in self.timers.values():
            timer.update()
        self.animate(dt)
        self.entity.update(dt)

class EntityOutlineSprite(pygame.sprite.Sprite):
    def __init__(self, entity_sprite, groups, frames):
        super().__init__(groups)
        self.z = BATTLE_LAYERS['outline']
        self.entity_sprite = entity_sprite
        self.frames = frames

        self.image = self.frames[self.entity_sprite.state][self.entity_sprite.frame_index]
        self.rect = self.image.get_rect(center = self.entity_sprite.rect.center)

    def update(self, dt):
        self.image = self.frames[self.entity_sprite.state][self.entity_sprite.adjusted_frame_index]

# player
class BattleArtSprite(pygame.sprite.Sprite):
    def __init__(self, index, entity_frames, groups, image):
        super().__init__(groups)
        self.entity_sprite = entity_frames
        self.z = BATTLE_LAYERS['name']
        self.surf = image

        self.image = pygame.transform.scale(self.surf, (120, 40))
        self.rect = self.image.get_rect(topleft = (25, 530 + (45 * index)))

    def update(self, dt):
        if not self.entity_sprite.groups():
            self.image = pygame.transform.scale(pygame.transform.grayscale(self.surf), (120, 40))

class BattleNameSprite(pygame.sprite.Sprite):
    def __init__(self, index, entity_sprite, groups, font):
        super().__init__(groups)
        self.entity_sprite = entity_sprite
        self.z = BATTLE_LAYERS['name']

        text_surf = font.render(entity_sprite.entity.name[:12], True, COLORS['black'])

        self.image = text_surf
        self.rect = self.image.get_rect(midleft = (155, 550 + (45 * index)))

class BattleEffectSprite(pygame.sprite.Sprite):
    def __init__(self, index, entity_frames, groups, effects_image):
        super().__init__(groups)
        self.entity_sprite = entity_frames
        self.z = BATTLE_LAYERS['name']
        self.effects: list = entity_frames.entity.effects

        surf = pygame.Surface((100, 40), pygame.SRCALPHA)

        for num, (effect, count) in enumerate(self.effects):  
            offset = num * 38 if len(self.effects) <= 2 else num * (100//len(self.effects))
            surf.blit(effects_image[str(effect)], (0 + offset, 0))

            if len(self.effects) >= 3:
                surf.blit(effects_image['Right_Edge'], (60, 0))

        self.image = surf        
        self.rect = self.image.get_rect(topleft = (300, 530 + (45 * index)))

    def update(self, dt):
        if not self.entity_sprite.groups():
            self.kill()

class BattleStatsSprite(pygame.sprite.Sprite):
    def __init__(self, index, entity_frames, groups, font):
        super().__init__(groups)
        self.entity_sprite = entity_frames
        self.z = BATTLE_LAYERS['name']
        self.index = index
        self.font = font

        self.image = pygame.Surface((525, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft = (415, 530 + (45 * index)))

    def update(self, dt):
        self.image.fill('white')
        for num, (head, value, max_value) in enumerate(self.entity_sprite.entity.get_info()):
            color = (COLORS['red'], COLORS['blue'], COLORS['green'])[num]
            if num < 2:
                text_surf = self.font.render(f'{head} :{int(value)}/{max_value}', False, COLORS['black'])
                text_rect = text_surf.get_rect(topleft = (0 + (175 * num), 0))
                bar_rect = pygame.Rect(text_rect.bottomleft + vector(0, -1), (160, 40))

            else:
                text_surf = self.font.render(f'{head} :{str(int(value))[:3]}%', False, COLORS['black'])
                text_rect = text_surf.get_rect(topleft = (0 + (175 * num), 0))
                bar_rect = pygame.Rect(text_rect.bottomleft + vector(0, -1), (160, 40))

            self.image.blit(text_surf, text_rect)
            draw_bar(self.image, bar_rect, value, max_value, color, COLORS['gray'], 2)

class BattleLevelSprite(pygame.sprite.Sprite):
    def __init__(self, team, pos, entity_sprite, groups, font):
        super().__init__(groups)
        self.entity_sprite = entity_sprite
        self.font = font
        self.z = BATTLE_LAYERS['name']

        self.image = pygame.Surface((60, 26))
        self.rect = self.image.get_rect(topleft = pos) if team == 'player' else self.image.get_rect(topright = pos)
        self.xp_rect = pygame.Rect(0, self.rect.height - 2, self.rect.width, 2)

    def update(self, dt):
        self.image.fill(COLORS['white'])

        text_surf = self.font.render(f'Lvl {self.entity_sprite.entity.level}', False, COLORS['black'])
        text_rect = text_surf.get_rect(center = (self.rect.width / 2, self.rect.height / 2))
        self.image.blit(text_surf, text_rect)

        draw_bar(self.image, self.xp_rect, self.entity_sprite.entity.xp, self.entity_sprite.entity.level_up, COLORS['black'], COLORS['white'], 0)

        if not self.entity_sprite.groups():
            self.kill()

# enemy
class BattleEnemy(pygame.sprite.Sprite):
    def __init__(self, pos, entity_frames, groups, font):
        super().__init__(groups)
        self.entity_sprite = entity_frames
        self.z = BATTLE_LAYERS['name']
        self.font = font

        self.image = pygame.Surface((120, 45), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midtop = pos)

    def update(self, dt):
        self.image.fill('white')

        for num, (head, value, max_value) in enumerate(self.entity_sprite.entity.get_hpap()):
            color = (COLORS['red'], COLORS['green'])[num]
            if num == 0:
                text_surf = self.font.render(f'{head} :', False, COLORS['black'])
                text_rect = text_surf.get_rect(topleft = (10, 5))
                bar_rect = pygame.Rect(text_rect.topleft + vector(0, 0), (100, 15))

            if num == 1:
                text_surf = self.font.render(f'{head} :{str(int(value))[:3]}%', False, COLORS['black'])
                text_rect = text_surf.get_rect(topleft = (10, 25))
                bar_rect = pygame.Rect(text_rect.topleft + vector(0, 0), (100, 15))

            # self.image.blit(text_surf, text_rect)
            draw_bar(self.image, bar_rect, value, max_value, color, COLORS['gray'], 2)

        if not self.entity_sprite.groups():
            self.kill()

# 
class AttackSprite(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups, z=BATTLE_LAYERS['overlay'])
        self.rect.center = pos
        
    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

    def update(self, dt):
        self.animate(dt)

class IndicatorSprite(pygame.sprite.Sprite):
    def __init__(self, pos, font, groups, amount, block, keyword):
        super().__init__(groups)
        self.z = BATTLE_LAYERS['overlay']
        self.font = font
        self.counter = 0
        self.text = abs(amount)
        self.block = block

        if keyword == 'block':
            color = COLORS['block']
            self.text = 'Blocking'
        elif self.block:
            color = COLORS['block']
        else:
            color = COLORS['heal'] if keyword == 'heal' else COLORS['black']

        text_surf = font.render(str(self.text), True, color)
        self.image = text_surf
        self.rect = self.image.get_rect(center = pos + vector(0, -50))
        
    def animate(self, dt):
        self.counter += 1 * dt
        self.rect.center += vector(0, -1)
        if self.counter >= 1:
            self.kill()

    def update(self, dt):
        self.animate(dt)
