from time import sleep

from game_objects import *
from controls import *
from PyQt6.QtWidgets import QMessageBox


class Sokoban:
    TIMEREVENT = pygame.USEREVENT + 1

    def __init__(self, size, background, screen, point_size=1, points_count=10, text_size=30,
                 base_colors=((255, 255, 255), (0, 0, 0)),
                 active_colors=((0, 0, 0), (255, 255, 255))):
        self.size = size
        self.background = background
        self.point_size = point_size
        self.points_count = points_count
        self.cell_len = point_size * points_count
        self.level = None

        self.images = {
            "X": pygame.image.load("data/wall.png"),  # wall
            "@": pygame.image.load("data/hero.png"),  # hero
            " ": pygame.image.load("data/ground.png"),  # void cell
            ".": pygame.image.load("data/place.png"),  # place for box
            "*": pygame.image.load("data/box.png")  # box
        }
        for i in self.images:
            self.images[i] = pygame.transform.scale(self.images[i], (self.cell_len, self.cell_len))
            self.images[i].set_colorkey((255, 255, 255))
        self.hero_image_angles = {
            (-1, 0): self.images["@"],
            (0, 1): pygame.transform.rotate(self.images["@"], 90),
            (1, 0): pygame.transform.rotate(self.images["@"], 180),
            (0, -1): pygame.transform.rotate(self.images["@"], 270),
        }
        for i in self.hero_image_angles.values():
            i.set_colorkey((255, 255, 255))
        self.running = True
        self.screen = screen
        self.screen.fill(background)
        self.all_group = pygame.sprite.Group()
        self.tiles_group = pygame.sprite.Group()
        self.hero_group = pygame.sprite.Group()
        self.walls_group = pygame.sprite.Group()
        self.places_group = pygame.sprite.Group()
        self.boxes_group = pygame.sprite.Group()

        self.controls_group = pygame.sprite.Group()
        self.cursor_group = pygame.sprite.Group()
        self.static_group = pygame.sprite.Group()
        self.buttons_group = pygame.sprite.Group()

        self.cursor = Cursor(self.cursor_group)
        self.info_static = Static(0, 0, self.controls_group, self.static_group, text_size=text_size, colors=base_colors)
        # self.button_back.set_pos(self.size[0] - self.button_back.rect.width, 0)

        last_x_pos = 0
        self.button_restart = Button(
            0, 0,
            self.controls_group, self.buttons_group,
            text="Restart",
            base_colors=base_colors,
            active_colors=active_colors,
            text_size=text_size,
            on_click=lambda _self, parent, event: (
                parent.clear(),
                parent.load_level(parent.level)
            )
        )
        last_x_pos += self.button_restart.rect.width
        self.button_restart.set_pos(self.size[0] - last_x_pos, 0)

        def button_forward(button, game, event):
            if isinstance(game.level, int):
                with open("data/levels/user_level", "r+") as file_level:
                    max_user_level = int(file_level.readline().rstrip("\n"))
                    if self.level < max_user_level:
                        game.clear()
                        game.level += 1
                        game.load_level(game.level)

        self.button_forward = Button(
            0, 0,
            self.controls_group, self.buttons_group,
            text=" ⇛ ",
            base_colors=base_colors,
            active_colors=active_colors,
            text_size=text_size,
            on_click=button_forward
        )
        last_x_pos += self.button_forward.rect.width + 3
        self.button_forward.set_pos(self.size[0] - last_x_pos, 0)

        def button_click_back(button, game: Sokoban, event):
            # print(game.level)
            if isinstance(game.level, int) and game.level > 1:
                game.clear()
                game.level -= 1
                game.load_level(game.level)

        self.button_back = Button(
            0, 0,
            self.controls_group, self.buttons_group,
            text=" ⇚ ",
            base_colors=base_colors,
            active_colors=active_colors,
            text_size=text_size,
            on_click=button_click_back
        )
        last_x_pos += self.button_back.rect.width + 3
        self.button_back.set_pos(self.size[0] - last_x_pos, 0)

        self.button_menu = Button(
            0, 0,
            self.controls_group, self.buttons_group,
            text="Menu",
            base_colors=base_colors,
            active_colors=active_colors,
            text_size=text_size,
            on_click=lambda _self, parent, event: (
                setattr(parent, "running", False)
            )
        )
        last_x_pos += self.button_menu.rect.width + 3
        self.button_menu.set_pos(self.size[0] - last_x_pos, 0)

        self.hero = None
        self.tiles = []
        self.walls = []
        self.places = []
        self.boxes = []

        self.retval = True
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
        self.info_static.set_text(
            f"Level: {self.level if isinstance(self.level, int) else self.level.split("/")[-1].split(".")[0]}" +
            f", Boxes: 0/{len(self.boxes_group)}")

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
        self.controls_group.draw(self.screen)

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

    def key_down_event(self, event):
        if event.scancode in self.move_directions:
            self.timer_direction = self.move_directions[event.scancode]

    def key_up_event(self, event):
        if event.scancode in self.move_directions and self.move_directions[event.scancode] == self.timer_direction:
            self.timer_direction = None

    def timer_event(self, event):
        if self.timer_steps and self.steps_direction:
            direct_x, direct_y = self.steps_direction
            for obj in self.move_objects:
                obj.move(direct_x * self.point_size, direct_y * self.point_size)
            self.timer_steps -= 1
            if not self.timer_steps:
                self.move_objects.clear()
                self.steps_direction = None
                delivered_count = len(pygame.sprite.groupcollide(self.boxes_group, self.places_group, False, False))
                if delivered_count == len(self.boxes_group):
                    if type(self.level).__name__ == "int":
                        self.clear()
                        self.level = self.level + 1
                        self.load_level(self.level)
                        with (open("data/levels/user_level", "r+") as file_level,
                              open("data/levels/max_level") as file_max):
                            max_user_level = int(file_level.readline().rstrip("\n"))
                            max_levels_count = int(file_max.readline().rstrip("\n"))
                            if self.level >= max_levels_count:
                                QMessageBox.about(None, "Sokoban", "Вы прошли игру!")
                                self.running = False
                                return
                            if self.level > max_user_level:
                                file_level.seek(0, 0)
                                file_level.write(f"{self.level}")
                        sleep(0.5)
                    else:
                        self.running = False
                    return
                self.info_static.set_text(
                    f"Level: {self.level if isinstance(self.level, int) else self.level.split("/")[-1].split(".")[0]}" +
                    f", Boxes: {delivered_count}/{len(self.boxes_group)}")
            return
        if self.timer_direction:
            direct_x, direct_y = self.timer_direction
            self.hero.image = self.hero_image_angles[self.timer_direction]
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
            self.timer_steps = self.points_count
            self.steps_direction = self.timer_direction

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
            setattr(_self, "retval", False)
        ),
        pygame.KEYDOWN: key_down_event,
        pygame.KEYUP: key_up_event,
        TIMEREVENT: timer_event,
        pygame.MOUSEMOTION: mouse_motion_event,
        pygame.MOUSEBUTTONDOWN: mouse_down_event
    }

    def mainloop(self, level: int | str = 0):
        self.level = level
        self.load_level(level)
        self.retval = True
        self.running = True
        while self.running:
            for event in pygame.event.get():
                handler = self.game_events.get(event.type, lambda *args, **kwargs: 0)
                handler(self, event)
            self.update()
            pygame.display.flip()
        self.clear()
        return self.retval
