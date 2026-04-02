# boss.py
import pygame as pg
from demon import Demon
from fire_cross import FireCross
from player import Player

class Boss(Demon):
    def __init__(self, x, y, theme, player, main):
        super().__init__(x, y)

        self.main = main
        self.theme = theme
        self.player = player
        self.max_health = 500
        self.health = self.max_health
        self.damage = 20
        self.xp_reward = 250

        # TODO: add unique sprite animations per sin
        self.wrath_walking = [pg.image.load(f"sprites/boss/wrath/walking/wrath_walking_{i}.png") for i in range(1, 6)]
        self.wrath_screaming = [pg.image.load(f"sprites/boss/wrath/screaming/wrath_screaming_{i}.png") for i in range(1, 6)]
        self.color = (255, 0, 0)

    def get_current_frame(self):
        # TEMP: colored circle visual
        surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color, (40, 40), 40)
        return surf

    def summon_fire_cross(self):
        px = self.player.x
        py = self.player.y

        fire = FireCross(self.player, int(px), int(py), self.main)

        self.main.fire_attacks.append(fire)