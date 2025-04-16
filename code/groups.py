from settings import *
from support import import_image
from entities import Entity

class AllSprites(pygame.sprite.Group):
    def __init__(self, display):
        super().__init__()
        self.display_surface = display
        self.offset = vector()
        self.shadow_surf = import_image('graphics', 'other', 'shadow')

    def draw(self, player_center):
        self.offset.x = -(player_center[0] - DISPLAY_WIDTH / 2)
        self.offset.y = -(player_center[1] - DISPLAY_HEIGHT / 2)

        bg_sprites = [sprite for sprite in self if sprite.z < WORLD_LAYERS['main']]
        main_sprites = sorted([sprite for sprite in self if sprite.z == WORLD_LAYERS['main']], key = lambda sprite: sprite.y_sort)
        fg_sprites = [sprite for sprite in self if sprite.z > WORLD_LAYERS['main']]

        for layer in (bg_sprites, main_sprites, fg_sprites):
            for sprite in layer:
                if isinstance(sprite, Entity):
                    self.display_surface.blit(self.shadow_surf, sprite.rect.topleft + self.offset + vector(40,110))
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
