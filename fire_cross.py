import pygame
from player import Player


class FireTile:
    def __init__(self, player, x, y, main):
        self.main = main
        self.player = player
        self.x = x
        self.y = y
        self.timer = 180  # lasts 3 seconds at 60fps
        self.damage = 10

    def update(self):
        self.timer -= 1

        # damage player if touching
        px = self.player.x
        py = self.player.y

        if int(px) == self.x and int(py) == self.y:
            self.player.health -= self.damage

    def draw(self):
        screen_x = self.x * 64
        screen_y = self.y * 64

        pygame.draw.rect(self.main.screen, (255, 80, 0),
                         (screen_x, screen_y, 64, 64))

class FireCross:
    def __init__(self, player, center_x, center_y, main):
        self.main = main
        self.player = player
        self.tiles = []

        positions = [
            (0,0),
            (1,0),(-1,0),
            (2,0),(-2,0),
            (0,1),(0,-1),
            (0,2),(0,-2)
        ]

        for dx, dy in positions:
            x = center_x + dx
            y = center_y + dy
            self.tiles.append(FireTile(player, x, y, main))

    def update(self):
        for tile in self.tiles:
            tile.update()

    def draw(self):
        for tile in self.tiles:
            tile.draw()

    def is_finished(self):
        return self.tiles[0].timer <= 0