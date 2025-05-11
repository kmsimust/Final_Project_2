from settings import *

class MenuWindow:
    def __init__(self, display, fonts, close, to_mainmenu):
        self.display = display
        self.fonts = fonts
        self.choice = {
            0: 'resume',
            1: 'return menu',
            2: 'quit game'
            }
        self.close = close
        self.mainmenu = to_mainmenu

        width = self.display.get_width()
        height = self.display.get_height()

        self.tint_surf = pygame.Surface((pygame.display.get_window_size()))
        self.tint_surf.set_alpha(200)

        # dimensions
        self.main_rect = pygame.rect.Rect(width * 0.05, height * 0.05, width * 0.9, height * 0.9)

        # list
        self.visible_items = 6
        self.list_width = 844
        self.item_height = 578 / self.visible_items
        self.index = 0
        self.selected_index = None

    def input(self, keys):
        if keys[pygame.K_UP]:
            self.index -= 1
        if keys[pygame.K_DOWN]:
            self.index += 1
        
        if keys[pygame.K_z]:
            if self.index == 0:
                self.close()
                self.index = 0
            if self.index == 1:
                self.mainmenu()
                self.index = 0
            if self.index == 2:
                pygame.quit()
                exit()

        self.index = self.index % len(self.choice)

    def display_list(self):
        pygame.draw.rect(self.display, COLORS['gray'], self.main_rect, 0, 12)
        v_offset = 0 if self.index < self.visible_items else -(self.index - self.visible_items + 1) * (self.item_height + 10)

        for index, choice in self.choice.items():
            bg_color = COLORS['gray'] if self.index != index else COLORS['lighter']
            text_color = COLORS['white'] if self.index != index else COLORS['black']

            top = self.main_rect.top + 10 + index * self.item_height + v_offset
            item_rect = pygame.Rect(self.main_rect.left + 10, top, self.list_width, self.item_height)
            
            text_surf = self.fonts['dialog'].render(str(choice).title(), False, text_color)
            text_rect = text_surf.get_rect(center = item_rect.center)

            if item_rect.colliderect(self.main_rect):
                pygame.draw.rect(self.display, bg_color, item_rect, 0, 5)

            self.display.blit(text_surf, text_rect)

    def update(self, dt):
        self.display.blit(self.tint_surf, (0, 0))
        # pygame.draw.rect(self.display, 'white', self.main_rect)
        self.display_list()

class MainMenuWindow:
    def __init__(self, display, fonts, to_game, image):
        self.display = display
        self.fonts = fonts
        self.choice = {
            0: 'start',
            1: 'controls',
            2: 'quit game'
            }
        self.to_game = to_game
        self.image = image

        width = self.display.get_width()
        height = self.display.get_height()

        self.tint_surf = pygame.Surface((pygame.display.get_window_size()))
        self.tint_surf.fill('white')

        self.tutorial_surf = self.image['menu']['tutorial1']
        self.tutorial_rect = self.tutorial_surf.get_rect()

        # dimensions
        self.main_rect = pygame.rect.Rect((690, 230), (220, 450))
        self.show_controls = False

        # list
        self.visible_items = 4
        self.list_width = 200
        self.item_height = 100
        self.index = 0
        self.selected_index = None

        # control rect

    def input(self, keys):
        if keys[pygame.K_UP]:
            self.index -= 1
        if keys[pygame.K_DOWN]:
            self.index += 1
        
        if keys[pygame.K_z]:
            if self.index == 0:
                if self.show_controls:
                    self.show_controls = False
                else:
                    self.to_game()
                    self.index = 0

            if self.index == 1:
                self.show_controls = True
                self.index = 0

            if self.index == 2:
                pygame.quit()
                exit()

        if keys[pygame.K_x]:
            if self.show_controls:
                self.show_controls = False

        self.index = self.index % len(self.choice)

    def display_list(self):
        pygame.draw.rect(self.display, COLORS['gray'], self.main_rect, 0, 12)
        v_offset = 0 if self.index < self.visible_items else -(self.index - self.visible_items + 1) * (self.item_height + 10)

        for index, choice in self.choice.items():
            bg_color = COLORS['gray'] if self.index != index else COLORS['lighter']
            text_color = COLORS['white'] if self.index != index else COLORS['black']

            top = self.main_rect.top + 10 + index * self.item_height + v_offset
            item_rect = pygame.Rect(self.main_rect.left + 10, top, self.list_width, self.item_height)
            
            text_surf = self.fonts['dialog'].render(str(choice).title(), False, text_color)
            text_rect = text_surf.get_rect(center = item_rect.center)

            if item_rect.colliderect(self.main_rect):
                pygame.draw.rect(self.display, bg_color, item_rect, 0, 5)

            self.display.blit(text_surf, text_rect)

    def display_controls(self):
        self.display.blit(self.tutorial_surf, self.tutorial_rect)

    def update(self, dt):
        if self.show_controls:
            self.display_controls()
        else:
            self.display.blit(self.tint_surf, (0, 0))
            self.display_list()
