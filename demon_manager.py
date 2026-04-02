import pygame
import math
from settings import *
import random
from demon import Demon, FastDemon, TankDemon, ShooterDemon


class DemonManager:
    def __init__(self, map, level_up_manager):
        self.map = map
        self.level_up_manager = level_up_manager
        self.wave_manager = None
        self.demons = []

        # spawn demons where the map has "3"
        #for row in range(len(map.current_map)):
        #    for col in range(len(map.current_map[row])):
        #        if map.current_map[row][col] == 3:
        #            x = col * TILESIZE + TILESIZE // 2
        #            y = row * TILESIZE + TILESIZE // 2
        #            self.demons.append(Demon(x, y))

    # ----------------------------------------------------
    # UPDATE — Logic only, no drawing
    # ----------------------------------------------------
    def update(self, player, dt, raycaster):
        grid = self.map.current_map
        shot_processed = False

        for demon in self.demons[:]:

            # update movement + AI
            demon.update(player, dt, grid)

            # -----------------------------------
            # HIT DETECTION (ray from player)
            # -----------------------------------
            if player.did_shoot and not shot_processed and demon.state != "die":
                if self.ray_hits_demon(player.shot_ray, demon):
                    demon.take_damage(player.damage)
                    shot_processed = True

                    # Level-up handling
                    if demon.health <= 0:
                        leveled_up = player.gain_xp(demon.xp_reward)

                        if leveled_up:
                            self.level_up_manager.trigger()

            # -----------------------------------
            # REMOVE FINISHED CORPSES
            # -----------------------------------
            if demon.is_dead_finished():
                # notify wave manager
                self.wave_manager.demon_killed()

                self.demons.remove(demon)






    # ----------------------------------------------------
    # RENDER — Draw sprites only
    # ----------------------------------------------------
    def render(self, screen, player, raycaster):
        for demon in sorted(self.demons, key=lambda d: math.hypot(d.x - player.x, d.y - player.y), reverse=True):

            dx = demon.x - player.x
            dy = demon.y - player.y
            dist = math.hypot(dx, dy)

            demon_angle = math.atan2(dy, dx)
            angle_diff = demon_angle - player.rotation_angle

            # normalize
            while angle_diff > math.pi: angle_diff -= 2 * math.pi
            while angle_diff < -math.pi: angle_diff += 2 * math.pi

            # outside field of view
            if abs(angle_diff) > math.radians(30):
                continue

            screen_x = (angle_diff / math.radians(30)) * (WINDOW_WIDTH // 2) + WINDOW_WIDTH // 2

            if dist < 0.5: dist = 0.5

            sprite_size = int((64 / dist) * 300)

            if isinstance(demon, FastDemon):
                sprite_size = int(sprite_size * 0.8)

            sprite_size = min(sprite_size, 500)
            sprite = pygame.transform.scale(demon.get_current_frame(), (sprite_size, sprite_size))

            draw_x = screen_x - sprite_size // 2
            draw_y = WINDOW_HEIGHT // 2 - sprite_size // 2

            screen_col = int(screen_x)

            if 0 <= screen_col < len(raycaster.depth_buffer):
                if dist < raycaster.depth_buffer[screen_col]:
                    screen.blit(sprite, (draw_x, draw_y))

    # ----------------------------------------------------
    # RAY → DEMON COLLISION (simple)
    # ----------------------------------------------------
    def ray_hits_demon(self, ray, demon):
        if ray is None:
            return False

        (x1, y1, x2, y2) = ray

        dx = demon.x - x1
        dy = demon.y - y1
        ray_dx = x2 - x1
        ray_dy = y2 - y1

        t = max(0, min(1, (dx * ray_dx + dy * ray_dy) /
                       (ray_dx * ray_dx + ray_dy * ray_dy)))

        closest_x = x1 + t * ray_dx
        closest_y = y1 + t * ray_dy

        dist = math.hypot(demon.x - closest_x, demon.y - closest_y)
        return dist < 30