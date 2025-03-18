import pygame


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, map_size):
        self.dx = 0
        self.dy = 0
        self.map_size = map_size

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - self.map_size[0] // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - self.map_size[1] // 2)


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect().move(x, y)


class Place(pygame.sprite.Sprite):
    def __init__(self, x, y, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect().move(x, y)


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect().move(x, y)


class Box(pygame.sprite.Sprite):
    def __init__(self, x, y, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect().move(x, y)

    def move(self, step_x, step_y):
        self.rect = self.rect.move(step_x, step_y)


class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect().move(x, y)
        self.camera = None

    def update_camera(self):
        self.camera.update(self)

    def apply_camera(self, group):
        for sprite in group:
            self.camera.apply(sprite)

    def move(self, step_x, step_y):
        self.rect = self.rect.move(step_x, step_y)
