import math
import pygame
from settings import *
from ray import Ray

class Raycaster:
    def __init__(self, player, game_map):
        self.player = player
        self.map = game_map
        self.rays = []
        self.wall_textures = {
            1: pygame.image.load("textures/horror_house_wall_1.png").convert(),
            2: pygame.image.load("textures/horror_house_bath.png").convert(),
            3: pygame.image.load("textures/horror_house_door.png").convert()

        }

        # depth buffer for sprite occlusion
        self.depth_buffer = [99999] * WINDOW_WIDTH

    def castAllRays(self):
        self.rays = []
        start_angle = self.player.rotation_angle - FOV / 2
        angle_step = FOV / NUM_RAYS

        ray_angle = start_angle

        for i in range(NUM_RAYS):
            ray = Ray(ray_angle, self.player, self.map)
            ray.cast()
            self.rays.append(ray)

            # Fill depth buffer: convert NUM_RAYS to WINDOW_WIDTH
            col_width = WINDOW_WIDTH / NUM_RAYS
            start_col = int(i * col_width)
            end_col = int((i + 1) * col_width)

            for col in range(start_col, min(end_col, WINDOW_WIDTH)):
                self.depth_buffer[col] = ray.distance

            ray_angle += angle_step

    def render(self, screen):
        for i, ray in enumerate(self.rays):
            perp_distance = max(ray.distance * math.cos(ray.rayAngle - self.player.rotation_angle), 0.2)
            line_height = int(TILESIZE * WINDOW_HEIGHT / perp_distance)

            draw_begin = int(WINDOW_HEIGHT // 2 - line_height // 2)
            draw_end = draw_begin + line_height

            # clamp
            draw_begin = max(0, draw_begin)
            draw_end = min(WINDOW_HEIGHT, draw_end)

            # --- determine texture from map value ---
            map_x = int(ray.wall_hit_x // TILESIZE)
            map_y = int(ray.wall_hit_y // TILESIZE)
            wall_value = self.map.current_map[map_y][map_x]
            texture = self.wall_textures.get(wall_value, self.wall_textures[1])

            tex_width = texture.get_width()
            tex_height = texture.get_height()

            # determine exact hit position for texture
            if ray.hit_vertical:
                wall_x = ray.wall_hit_y - (int(ray.wall_hit_y / TILESIZE) * TILESIZE)
            else:
                wall_x = ray.wall_hit_x - (int(ray.wall_hit_x / TILESIZE) * TILESIZE)

            wall_x /= TILESIZE  # normalize to 0..1
            tex_x = int(wall_x * texture.get_width())

            # flip texture
            if ray.hit_vertical and ray.is_facing_left:
                tex_x = tex_width - tex_x - 1
            if not ray.hit_vertical and ray.is_facing_up:
                tex_x = tex_width - tex_x - 1

            col_width = int(WINDOW_WIDTH / NUM_RAYS)

            draw_end = draw_begin + line_height
            draw_begin = max(0, draw_begin)
            draw_end = min(WINDOW_HEIGHT, draw_end)

            for y in range(draw_begin, draw_end):
                tex_y = int(((y - draw_begin) / line_height) * tex_height)
                color = texture.get_at((tex_x, tex_y))

                for w in range(col_width):
                    screen.set_at((i * col_width + w, y), color)