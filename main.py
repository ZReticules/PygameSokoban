import pygame
import json
import sys

from PyQt6.QtWidgets import QApplication
from sokoban import Sokoban
from menu import Menu

app = QApplication(sys.argv)
with open("config.json") as fconfig:
    config = json.load(fconfig)
pygame.init()
pygame.display.set_caption("Сокобан")
mainScreen = pygame.display.set_mode((config["width"], config["height"]))
pygame.time.set_timer(Sokoban.TIMEREVENT, config["ticks"])
menu = Menu((config["width"], config["height"]), tuple(config["background"]), mainScreen,
            text_size=config["menu_text_size"],
            active_colors=tuple(map(tuple, config["active_colors"])),
            base_colors=tuple(map(tuple, config["base_colors"])))
game = Sokoban((config["width"], config["height"]), tuple(config["background"]), mainScreen,
               point_size=config["point_size"], points_count=config["points_count"], text_size=config["game_text_size"],
               active_colors=tuple(map(tuple, config["active_colors"])),
               base_colors=tuple(map(tuple, config["base_colors"])))
while True:
    with open("data/levels/user_level") as file_level:
        last_user_level = int(file_level.readline().rstrip("\n"))
    if (menu_level := menu.mainloop(level=last_user_level)) == "Quit":
        break
    if not game.mainloop(level=menu_level):
        break
