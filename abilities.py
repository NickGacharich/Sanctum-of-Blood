import math
import pygame

import pygame
import math
from settings import *


class Ability:
    def __init__(self, name, mana_cost, cooldown):
        self.name = name
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.cooldown_timer = 0

    def can_use(self, player):
        return player.mana >= self.mana_cost and self.cooldown_timer <= 0

    def use(self, player, game):
        pass

    def update(self, dt, player, demon_manager):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

class FireCross:
    def __init__(self, x, y, angle, image):
        self.x = x
        self.y = y
        self.angle = angle
        self.image = image
        self.damage = 15
        self.alive = False

        self.active = False
        self.speed = 6

    def launch(self):
        self.active = True

    def update(self, player, demon_manager):
        if not self.active or not self.alive:
            return

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # collision with demons
        for demon in demon_manager.demons:
            if demon.dead:
                continue

            dx = self.x - demon.x
            dy = self.y - demon.y
            distance = math.hypot(dx, dy)

            if distance < 20:
                demon.take_damage(self.damage)
                self.alive = False
                break

    def check_collision(self, demon):
        dx = self.x - demon.x
        dy = self.y - demon.y
        distance = math.hypot(dx, dy)

        return distance < 20  # adjust hit radius

    def draw(self, screen, player):
        screen_x = WINDOW_WIDTH // 2 + (self.x - player.x)
        screen_y = WINDOW_HEIGHT // 2 + (self.y - player.y)

        screen.blit(self.image, (screen_x - self.image.get_width()//2,
                                 screen_y - self.image.get_height()//2))


class Fireball(Ability):
    def __init__(self):
        super().__init__("Fireball", mana_cost=20, cooldown=500)
        self.crosses = []
        self.num_crosses = 5
        self.radius = 40

        # load sprite once
        sheet = pygame.image.load("sprites/abilities/fireball/crosses.png").convert_alpha()
        w = sheet.get_width() // 2
        h = sheet.get_height() // 2
        self.cross_image = sheet.subsurface((0, 0, w, h))
        print("Fireball updating", len(self.crosses))

    def spawn_crosses(self, player):
        self.crosses.clear()

        
        base_angle = math.atan2(player.last_dy, player.last_dx)
        spread = math.radians(120)
        start_angle = base_angle - spread / 2


        if player.last_dx == 0 and player.last_dy == 0:
            base_angle = -math.pi / 2
        else:
            base_angle = math.atan2(player.last_dy, player.last_dx)

        for i in range(self.num_crosses):
            t = (i - (self.num_crosses - 1) / 2) / (self.num_crosses - 1)
            angle = base_angle + t * spread

            x = player.x + math.cos(angle) * self.radius
            y = player.y + math.sin(angle) * self.radius
            self.crosses.append(FireCross(x, y, angle, self.cross_image))

    def update(self, dt, player, demon_manager):
        super().update(dt, player, demon_manager)

        base_angle = math.atan2(player.last_dy, player.last_dx)
        spread = math.radians(100)

        for i, cross in enumerate(self.crosses):
            if not cross.active:
                t = (i - (self.num_crosses - 1) / 2) / (self.num_crosses - 1)
                angle = base_angle + t * spread

                cross.x = player.x + math.cos(angle) * self.radius
                cross.y = player.y + math.sin(angle) * self.radius
                cross.angle = angle

            cross.update(player, demon_manager)
            self.crosses = [c for c in self.crosses if c.alive]

    def use(self, player, game):
        if not self.can_use(player):
            return

        player.mana -= self.mana_cost
        self.cooldown_timer = self.cooldown

        print("FIRE CROSS LAUNCH!")

        for cross in self.crosses:
            cross.launch()

        # respawn new crosses after shooting
        self.spawn_crosses(player)

        # TODO: spawn projectile



class Dash(Ability):
    def __init__(self):
        super().__init__("Dash", mana_cost=15, cooldown=800)

        self.dash_effect = pygame.mixer.Sound("assets/sounds/dash.wav")
        self.dash_effect.set_volume(0.9)

    def use(self, player, game):
        if not self.can_use(player):
            return

        self.dash_effect.play()

        dx = math.cos(player.rotation_angle)
        dy = math.sin(player.rotation_angle)

        # normalize (safety)
        length = math.hypot(dx, dy)
        if length == 0:
            return
        dx /= length
        dy /= length

        dash_distance = 120
        step_size = 2

        steps = int(dash_distance / step_size)

        for _ in range(steps):
            new_x = player.x + dx * step_size
            new_y = player.y + dy * step_size

            # ✅ STOP if hitting wall
            if player.is_wall(new_x, new_y):
                break

            player.x = new_x
            player.y = new_y

        player.mana -= self.mana_cost
        self.cooldown_timer = self.cooldown
