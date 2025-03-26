import pygame
from typing import Any, Callable


class Cursor(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = pygame.Rect(0, 0, 1, 1)
        self.last_collided = None

    def set_pos(self, x, y):
        self.rect = pygame.Rect(x, y, 1, 1)


class Static(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups, text="", colors=((0, 0, 0), (255, 255, 255)), text_size=30):
        super().__init__(*groups)
        self.text = text
        self.text_size = text_size
        self.tx_color, self.bg_color = colors
        self.image = pygame.font.Font("data/segoe-ui-symbol.ttf", self.text_size).render(text, True,
                                                                                         self.tx_color, self.bg_color)
        self.rect = self.image.get_rect().move(x, y)

    def set_text(self, text):
        x, y, *_ = self.rect
        self.text = text
        self.image = pygame.font.Font("data/segoe-ui-symbol.ttf", self.text_size).render(text, True,
                                                                                         self.tx_color, self.bg_color)
        self.rect = self.image.get_rect().move(x, y)

    def set_colors(self, colors):
        self.tx_color, self.bg_color = colors
        self.image = pygame.font.Font("data/segoe-ui-symbol.ttf", self.text_size).render(self.text, True, *colors)

    def set_bg_color(self, color):
        self.bg_color = color
        self.image = pygame.font.Font("data/segoe-ui-symbol.ttf", self.text_size).render(self.text, True,
                                                                                         self.tx_color, self.bg_color)

    def set_tx_color(self, color):
        self.tx_color = color
        self.image = pygame.font.Font("data/segoe-ui-symbol.ttf", self.text_size).render(self.text, True,
                                                                                         self.tx_color, self.bg_color)

    def set_pos(self, x, y):
        self.rect = pygame.Rect(x, y, self.rect.width, self.rect.height)


class Button(Static):

    def on_cursor(self):
        # print((self.tx_color, self.bg_color) != self.active_colors)
        if (self.tx_color, self.bg_color) != self.active_colors:
            self.set_colors(self.active_colors)

    def off_cursor(self):
        if (self.tx_color, self.bg_color) != self.base_colors:
            self.set_colors(self.base_colors)

    def __init__(self, x, y, *groups,
                 text="",
                 base_colors=((0, 0, 0), (255, 255, 255)),
                 on_click: Callable[[Any, Any, Any], Any] = lambda _self, parent, event: None,
                 active_colors=((255, 255, 255), (0, 0, 0)),
                 text_size=30
                 ):
        self.click = on_click
        super().__init__(x, y, *groups, text=text, colors=base_colors, text_size=text_size)
        self.base_colors = base_colors
        self.active_colors = active_colors
