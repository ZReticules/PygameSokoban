import pygame
from controls import *
from PyQt6.QtWidgets import QFileDialog


class Menu:
    def __init__(self, size, background, screen, text_size=30, base_colors=((255, 255, 255), (0, 0, 0)),
                 active_colors=((0, 0, 0), (255, 255, 255))):
        self.size = size
        self.background = background
        self.running = True
        self.screen = screen
        self.screen.fill(background)

        self.controls_group = pygame.sprite.Group()
        self.cursor_group = pygame.sprite.Group()
        # self.static_group = pygame.sprite.Group()
        self.buttons_group = pygame.sprite.Group()

        self.cursor = Cursor(self.cursor_group)

        last_y_pos = 250
        self.button_start = Button(
            0, 0,
            self.controls_group, self.buttons_group,
            text="Play",
            base_colors=base_colors,
            active_colors=active_colors,
            text_size=text_size,
            on_click=lambda _self, parent, event: (
                setattr(parent, "running", False)
            )
        )

        self.button_start.set_pos((self.size[0] - self.button_start.rect.width) // 2, last_y_pos)
        last_y_pos += self.button_start.rect.height

        self.button_load = Button(
            0, 0,
            self.controls_group, self.buttons_group,
            text="Load",
            base_colors=base_colors,
            active_colors=active_colors,
            text_size=text_size,
            on_click=lambda _self, parent, event: (
                _path := QFileDialog.getOpenFileName(None, 'Open File', '', 'All Files (*)')[0],
                (setattr(parent, "running", False), setattr(parent, "retval", _path)) if _path else None
            )
        )

        last_y_pos += 20
        self.button_load.set_pos((self.size[0] - self.button_load.rect.width) // 2, last_y_pos)
        last_y_pos += self.button_load.rect.height

        self.button_close = Button(
            0, 0,
            self.controls_group, self.buttons_group,
            text="Close",
            base_colors=base_colors,
            active_colors=active_colors,
            text_size=text_size,
            on_click=lambda _self, parent, event: (
                setattr(parent, "running", False),
                setattr(parent, "retval", "Quit")
            )
        )

        last_y_pos += 20
        self.button_close.set_pos((self.size[0] - self.button_close.rect.width) // 2, last_y_pos)
        last_y_pos += self.button_close.rect.height

        self.retval = None

    def update(self):
        self.screen.fill(self.background)
        self.controls_group.draw(self.screen)

    def mouse_motion_event(self, event):
        self.cursor.set_pos(*event.pos)
        collided_button = pygame.sprite.spritecollideany(self.cursor, self.buttons_group)
        if self.cursor.last_collided != collided_button:
            if self.cursor.last_collided is not None:
                self.cursor.last_collided.off_cursor()
            self.cursor.last_collided = collided_button
            if self.cursor.last_collided is not None:
                self.cursor.last_collided.on_cursor()

    def mouse_down_event(self, event):
        self.mouse_motion_event(event)
        if self.cursor.last_collided is not None:
            self.cursor.last_collided.click(self.cursor.last_collided, self, event)

    game_events = {
        pygame.QUIT: lambda _self, event: (
            setattr(_self, "running", False),
            setattr(_self, "retval", "Quit")
        ),
        pygame.MOUSEMOTION: mouse_motion_event,
        pygame.MOUSEBUTTONDOWN: mouse_down_event
    }

    def mainloop(self, level: int | str = 0):
        self.retval = level
        self.running = True
        while self.running:
            for event in pygame.event.get():
                handler = self.game_events.get(event.type, lambda *args, **kwargs: 0)
                handler(self, event)
            self.update()
            pygame.display.flip()
        return self.retval
