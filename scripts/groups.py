from settings import *
from support import load_image
from entities import Entity

class AllSprites(pygame.sprite.Group):
    def __init__(self, display):
        super().__init__()
        self.display_surface = display
        self.offset = vector()
        self.shadow_surf = load_image('other/shadow.png')
        self.notice_surf = load_image('ui/notice.png')

    def draw(self, player):
        self.offset.x = -(player.rect.centerx - DISPLAY_WIDTH / 2)
        self.offset.y = -(player.rect.centery - DISPLAY_HEIGHT / 2)

        bg_sprites = [sprite for sprite in self if sprite.z < WORLD_LAYERS['main']]
        main_sprites = sorted([sprite for sprite in self if sprite.z == WORLD_LAYERS['main']], key = lambda sprite: sprite.y_sort)
        fg_sprites = [sprite for sprite in self if sprite.z > WORLD_LAYERS['main']]

        for layer in (bg_sprites, main_sprites, fg_sprites):
            for sprite in layer:
                if isinstance(sprite, Entity):
                    self.display_surface.blit(self.shadow_surf, sprite.rect.topleft + self.offset + vector(40, 110))
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
                if sprite == player and player.noticed:
                    rect = self.notice_surf.get_rect(midbottom = sprite.rect.midtop)
                    self.display_surface.blit(self.notice_surf, rect.topleft + self.offset)

class BattleSprites(pygame.sprite.Group):
    def __init__(self, display):
        super().__init__()
        self.display = display

    def draw(self, current_entity_sprite, side, mode, target_index, player_sprites, opponent_sprites):
        # get available
        sprite_group = opponent_sprites if side == 'opponent' else player_sprites
        sprites = {sprite.pos_index: sprite for sprite in sprite_group}
        entity_sprite = sprites[list(sprites.keys())[target_index]] if sprites else None

        for sprite in sorted(self, key = lambda sprite: sprite.z):
            if sprite.z == BATTLE_LAYERS['outline']:
                if sprite.entity_sprite == current_entity_sprite and not (mode == 'target' and side == 'player') or\
                    sprite.entity_sprite == entity_sprite and mode == 'target':
                    self.display.blit(sprite.image, sprite.rect)
            else:
                self.display.blit(sprite.image, sprite.rect)
