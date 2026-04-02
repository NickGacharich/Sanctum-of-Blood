import math
import pygame as pg
from settings import *

class Map:
    def __init__(self):
        self.house_textures = {
            1: pg.image.load("textures/horror_house_wall_1.png").convert(),
            2: pg.image.load("textures/horror_house_door.png").convert(),
            3: pg.image.load("textures/horror_house_bath.png").convert()
        }
        self.outside_house_textures = {
            1: pg.image.load("textures/outside_house_wall.png").convert(),
            2: pg.image.load("textures/outside_house_garage.png").convert(),
            3: pg.image.load("textures/outside_house_front_door.png").convert(),
            4: pg.image.load("textures/outside_house_window_1.png").convert(),
            5: pg.image.load("textures/outside_house_window_2.png").convert(),
            6: pg.image.load("textures/forest_wall_ 1.png").convert(),
            7: pg.image.load("textures/forest_wall_2.png").convert(),
            8: pg.image.load("textures/forest_wall_3.png").convert()
        }
        self.house = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 1],
            [1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 1, 2, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 1],
            [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
            [1, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 1, 0, 2, 1],
            [1, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 2, 2, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1],
        ]
        self.outside_house = [
            [6, 6, 7, 8, 8, 7, 7, 7, 6, 6, 6, 6, 6, 7, 8],
            [8, 0, 0, 0, 0, 0, 5, 5, 0, 0, 0, 0, 0, 0, 8],
            [8, 0, 0, 0, 0, 0, 5, 5, 0, 0, 0, 0, 0, 0, 8],
            [7, 0, 0, 0, 0, 0, 6, 6, 0, 0, 0, 0, 0, 0, 7],
            [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
            [6, 0, 0, 0, 1, 1, 2, 1, 3, 4, 1, 0, 0, 0, 7],
            [6, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 6],
            [6, 0, 0, 0, 1, 0, 0, 0, 0, 0, 5, 0, 0, 0, 6],
            [6, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 6],
            [7, 8, 7, 7, 1, 1, 1, 1, 1, 1, 1, 7, 7, 8, 8],
        ]
        self.current_map = [row[:] for row in self.house]
        self.current_texture = self.house_textures.copy()

    def has_wall_at(self, x, y):
        return self.house[int(y // TILESIZE)][int(x // TILESIZE)]

    def exit_map(self):
        if self.current_map == self.house:
            self.current_map = []
            self.current_texture = {}
            self.current_map = [row[:] for row in self.outside_house]
            self.current_texture = self.outside_house_textures.copy()



    def render(self, screen):
        for i in range(len(self.current_map)):
            for j in range(len(self.current_map[0])):
                tile_x = j * TILESIZE
                tile_y = i * TILESIZE

                if self.current_map[i][j] == 0:
                    pg.draw.rect(screen, (255, 255, 255), (tile_x, tile_y, TILESIZE - 1, TILESIZE - 1))
                elif self.current_map[i][j] == 1:
                    pg.draw.rect(screen, (40, 40, 40), (tile_x, tile_y, TILESIZE -1, TILESIZE - 1))

