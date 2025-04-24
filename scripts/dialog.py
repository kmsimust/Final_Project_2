from settings import *
from clock import Timer

class DialogTree:
    def __init__(self, character, character_icon, player, all_sprites, font, end_dialog):
        self.character = character
        self.character_icon = character_icon
        self.player = player
        self.name = character.name
        self.id = character.id
        self.all_sprites = all_sprites
        self.font = font
        self.end_dialog = end_dialog

        self.dialog = character.get_dialog()
        self.dialog_num = len(self.dialog)
        self.dialog_index = 0

        self.current_dialog = DialogSprite(
                                self.dialog[self.dialog_index],
                                self.player,
                                self.character,
                                self.character_icon,
                                self.all_sprites,
                                self.font)
        self.dialog_timer = Timer(100, autostart=True)
        
    def input(self, keys):
        if keys[pygame.K_z] and not self.dialog_timer.active:
            self.current_dialog.kill()
            self.dialog_index += 1
            if self.dialog_index < self.dialog_num:
                self.current_dialog = DialogSprite(
                                        self.dialog[self.dialog_index],
                                        self.player,
                                        self.character,
                                        self.character_icon,
                                        self.all_sprites,
                                        self.font)
                self.dialog_timer.activate()
            else:
                self.end_dialog(self.character)

    def update(self, dt, keys):
        self.dialog_timer.update()
        self.input(keys)
        self.current_dialog.update(dt)

class DialogSprite(pygame.sprite.Sprite):
    def __init__(self, message, player, character, character_icon, groups, font):
        super().__init__(groups)
        self.z = WORLD_LAYERS['top']
        
        self.player = player
        self.message = message
        self.font = font
        self.character = character
        self.character_icon = character_icon

        self.counter = 0
        self.text_surf = self.font.render('', True, COLORS['black'])
        
        # temporary
        self.image = self.text_surf
        self.rect = self.image.get_rect(midtop = self.player.rect.center)

    def update(self, dt):
        speed = 3
        
        if self.counter < speed * len(self.message):
            self.counter += 1  
        
        # text
        self.text_surf = self.font.render(self.message[0:self.counter], True, COLORS['black'])
        height = 240

        # background
        surf = pygame.Surface((DISPLAY_WIDTH, height), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        icon_rect = self.character_icon.get_rect(topleft = (0, 0))
        
        # display text
        pygame.draw.rect(surf, COLORS['pure white'], surf.get_rect(topleft = (0, 0)), 0, 4)
        surf.blit(self.text_surf, surf.get_rect(topleft = (240, 40)))
        surf.blit(self.character_icon, icon_rect.topleft + vector(24, 24))

        # box position
        self.image = surf
        self.rect = self.image.get_rect(midtop = self.player.rect.center + vector(0, 360 - height))
