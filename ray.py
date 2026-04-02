import math, pygame
from settings import *
from map import Map
from player import Player


def normalize_angle(angle):
    angle = angle % (2 * math.pi)
    if (angle <= 0):
        angle = (2 * math.pi) + angle
    return angle


def distance_between(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))


class Ray:
    def __init__(self, angle, player, map):
        self.rayAngle = normalize_angle(angle)
        self.player: Player = player
        self.map: Map = map
        self.is_facing_down = self.rayAngle > 0 and self.rayAngle < math.pi
        self.is_facing_up = not self.is_facing_down
        self.is_facing_right = self.rayAngle < 0.5 * math.pi or self.rayAngle > 1.5 * math.pi
        self.is_facing_left = not self.is_facing_right
        self.texture_x = 0
        self.wall_hit_x = 0
        self.wall_hit_y = 0

        self.distance = 0

        self.color = 255

    def cast(self):
        # HORIZONTAL CHECKING
        found_horizontal_wall = False
        horizontal_hit_x = 0
        horizontal_hit_y = 0

        # finding first intersection
        if self.is_facing_up:
            first_intersection_y = ((self.player.y // TILESIZE) * TILESIZE) - 0.01
        else:
            first_intersection_y = ((self.player.y // TILESIZE) * TILESIZE) + TILESIZE

        first_intersection_x = self.player.x + (first_intersection_y - self.player.y) / math.tan(self.rayAngle)

        nextHorizontalX = first_intersection_x
        nextHorizontalY = first_intersection_y

        ya = -TILESIZE if self.is_facing_up else TILESIZE
        xa = ya / math.tan(self.rayAngle)

        while 0 <= nextHorizontalX < WINDOW_WIDTH and 0 <= nextHorizontalY < WINDOW_HEIGHT:
            if self.map.has_wall_at(nextHorizontalX, nextHorizontalY):
                found_horizontal_wall = True
                horizontal_hit_x = nextHorizontalX
                horizontal_hit_y = nextHorizontalY
                break
            nextHorizontalX += xa
            nextHorizontalY += ya

        # VERTICAL CHECKING
        found_vertical_wall = False
        vertical_hit_x = 0
        vertical_hit_y = 0

        if self.is_facing_right:
            first_intersection_x = ((self.player.x // TILESIZE) * TILESIZE) + TILESIZE
        else:
            first_intersection_x = ((self.player.x // TILESIZE) * TILESIZE) - 0.01

        first_intersection_y = self.player.y + (first_intersection_x - self.player.x) * math.tan(self.rayAngle)

        nextVerticalX = first_intersection_x
        nextVerticalY = first_intersection_y

        xa = TILESIZE if self.is_facing_right else -TILESIZE
        ya = xa * math.tan(self.rayAngle)

        while 0 <= nextVerticalX < WINDOW_WIDTH and 0 <= nextVerticalY < WINDOW_HEIGHT:
            if self.map.has_wall_at(nextVerticalX, nextVerticalY):
                found_vertical_wall = True
                vertical_hit_x = nextVerticalX
                vertical_hit_y = nextVerticalY
                break
            nextVerticalX += xa
            nextVerticalY += ya

        # DISTANCE
        horizontal_distance = distance_between(self.player.x, self.player.y, horizontal_hit_x,
                                               horizontal_hit_y) if found_horizontal_wall else 999999
        vertical_distance = distance_between(self.player.x, self.player.y, vertical_hit_x,
                                             vertical_hit_y) if found_vertical_wall else 999999

        # SELECT WHICH ONE WE USE
        if horizontal_distance < vertical_distance:
            self.wall_hit_x = horizontal_hit_x
            self.wall_hit_y = horizontal_hit_y
            self.distance = horizontal_distance
            self.hit_vertical = False
        else:
            self.wall_hit_x = vertical_hit_x
            self.wall_hit_y = vertical_hit_y
            self.distance = vertical_distance
            self.hit_vertical = True

        # DETERMINE WALL TYPE
        grid_x = int(self.wall_hit_x // TILESIZE)
        grid_y = int(self.wall_hit_y // TILESIZE)
        self.wall_type = self.map.current_map[grid_y][grid_x]

        # FISHEYE FIX
        self.distance *= math.cos(self.player.rotation_angle - self.rayAngle)

    def render(self, screen):
        pygame.draw.line(screen, (255, 0, 0),
                         (self.player.x, self.player.y),
                         (self.wall_hit_x, self.wall_hit_y))