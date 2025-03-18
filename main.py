from time import sleep

import pygame
from game_objects import *

TIMEREVENT = pygame.USEREVENT + 1


class Sokoban:
    def __init__(self, size, background, cell_len, level=1, steps_count=10):
        self.size = size
        self.background = background
        self.cell_len = cell_len
        self.mills = steps_count
        self.level = level

        self.images = {
            "X": pygame.image.load("data/wall.png"),  # wall
            "@": pygame.image.load("data/hero.png"),  # hero
            " ": pygame.image.load("data/ground.png"),  # void cell
            ".": pygame.image.load("data/place.png"),  # place for box
            "*": pygame.image.load("data/box.png")  # box
        }
        for i in self.images:
            self.images[i] = pygame.transform.scale(self.images[i], (cell_len, cell_len))
            self.images[i].set_colorkey((255, 255, 255))
        self.running = True
        self.screen = pygame.display.set_mode(size)
        self.screen.fill(background)
        self.all_group = pygame.sprite.Group()
        self.tiles_group = pygame.sprite.Group()
        self.hero_group = pygame.sprite.Group()
        self.walls_group = pygame.sprite.Group()
        self.places_group = pygame.sprite.Group()
        self.boxes_group = pygame.sprite.Group()

        self.hero = None
        self.tiles = []
        self.walls = []
        self.places = []
        self.boxes = []
        self.load_level(level)

        self.__retval = True
        self.timer_direction = None
        self.move_objects = []
        self.timer_steps = 0
        self.steps_direction = None

    items_dict = {
        " ": lambda _self, *args: _self.tiles.append(Tile(*args, _self.tiles_group)),
        "X": lambda _self, *args: _self.tiles.append(Wall(*args, _self.walls_group)),
        ".": lambda _self, *args: _self.tiles.append(Place(*args, _self.places_group)),
        "*": lambda _self, *args: (_self.tiles.append(Box(*args, _self.boxes_group))),
        "@": lambda _self, *args: (
            setattr(_self, "hero", Hero(*args, _self.hero_group)),
            setattr(getattr(_self, "hero"), "camera", Camera(getattr(_self, "size")))
        )
    }

    def load_level(self, level: str | int):
        if isinstance(level, int):
            fname = f"data/levels/level{level}.txt"
        else:
            fname = level
        with open(fname) as level_file:
            items_dict = {"X": [], " ": [], ".": [], "*": [], "@": []}
            lines_file = list(map(str.rstrip, level_file.readlines()))
            max_len = max(map(len, lines_file))
            for i, line in enumerate(lines_file):
                for j, smb in enumerate(line.rstrip("\n") + " " * (max_len - len(line))):
                    items_dict[smb].append((j * self.cell_len, i * self.cell_len))
                    if smb != "X" and smb != ".":
                        items_dict[" "].append((j * self.cell_len, i * self.cell_len))
            for key, value in items_dict.items():
                for x, y in value:
                    handler = self.items_dict.get(key, lambda *args: None)
                    handler(self, x, y, self.images[key], self.all_group)

    def clear(self):
        self.all_group.empty()
        self.tiles_group.empty()
        self.walls_group.empty()
        self.boxes_group.empty()
        self.places_group.empty()
        self.hero_group.empty()
        self.hero = None
        self.tiles.clear()
        self.walls.clear()
        self.places.clear()
        self.boxes.clear()

    def update(self):
        self.screen.fill(self.background)
        self.hero.update_camera()
        self.hero.apply_camera(self.all_group)
        self.all_group.draw(self.screen)

    move_directions = {
        82: (0, -1), 26: (0, -1),
        79: (1, 0), 7: (1, 0),
        80: (-1, 0), 4: (-1, 0),
        81: (0, 1), 22: (0, 1)
    }

    image_angles = {
        (-1, 0): 0,
        (0, -1): 90,
        (1, 0): 180,
        (0, 1): 270
    }

    def kdown_event(self, event):
        if event.scancode in self.move_directions:
            self.timer_direction = self.move_directions[event.scancode]

    def kup_event(self, event):
        if self.move_directions[event.scancode] == self.timer_direction:
            self.timer_direction = None

    def timer_event(self, event):
        if self.timer_steps and self.steps_direction:
            direct_x, direct_y = self.steps_direction
            for obj in self.move_objects:
                obj.move(direct_x * (self.cell_len / self.mills), direct_y * (self.cell_len / self.mills))
            self.timer_steps -= 1
            if not self.timer_steps:
                self.move_objects.clear()
                self.steps_direction = None
                delivered_count = len(pygame.sprite.groupcollide(self.boxes_group, self.places_group, False, False))
                if delivered_count == len(self.boxes_group):
                    self.clear()
                    # sleep(1)
                    self.level = self.level + 1
                    self.load_level(self.level)
            return
        if self.timer_direction:
            direct_x, direct_y = self.timer_direction
            self.hero.move(direct_x * self.cell_len, direct_y * self.cell_len)
            if pygame.sprite.spritecollideany(self.hero, self.walls_group):
                self.hero.move(-direct_x * self.cell_len, -direct_y * self.cell_len)
                return
            if box_collided := pygame.sprite.spritecollideany(self.hero, self.boxes_group):
                box_collided.move(direct_x * self.cell_len, direct_y * self.cell_len)
                if pygame.sprite.spritecollideany(box_collided, self.walls_group) or \
                        len(pygame.sprite.spritecollide(box_collided, self.boxes_group, False)) > 1:
                    self.hero.move(-direct_x * self.cell_len, -direct_y * self.cell_len)
                    box_collided.move(-direct_x * self.cell_len, -direct_y * self.cell_len)
                    return
                box_collided.move(-direct_x * self.cell_len, -direct_y * self.cell_len)
                self.move_objects += [box_collided]
            self.hero.move(-direct_x * self.cell_len, -direct_y * self.cell_len)
            self.move_objects += [self.hero]
            self.timer_steps = self.mills
            self.steps_direction = self.timer_direction
            self.hero.image = pygame.transform.rotate(self.images["@"], self.image_angles[self.timer_direction])
            self.hero.image.set_colorkey((255, 255, 255))

    def mouse_motion_event(self, event):
        print(event)

    game_events = {
        pygame.QUIT: lambda _self, event: (
            setattr(_self, "running", False),
            setattr(_self, "__retval", False)
        ),
        pygame.KEYDOWN: kdown_event,
        pygame.KEYUP: kup_event,
        TIMEREVENT: timer_event,
        pygame.MOUSEMOTION: mouse_motion_event
        # pygame.MOUSEBUTTONDOWN: button_down
    }

    def mainloop(self):
        self.__retval = True
        while self.running:
            for event in pygame.event.get():
                handler = self.game_events.get(event.type, lambda *args, **kwargs: 0)
                handler(self, event)
            self.update()
            pygame.display.flip()
        return self.__retval


pygame.init()
pygame.display.set_caption("Сокобан")
pygame.time.set_timer(TIMEREVENT, 10)
Game = Sokoban((800, 800), (0, 0, 0), cell_len=30, steps_count=15, level=0)
Game.mainloop()
