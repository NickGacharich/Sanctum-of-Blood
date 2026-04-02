import pygame as pg
from settings import *

class ObjectRender:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_texture()
        self.sky_image = self.get_texture('textures/mech_doom_sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0

    def draw(self):
        self.draw_background()
        self.render_game_objects()


    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))

        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))
    def render_game_objects(self):
        list_objects = self.game.raycaster.objects_to_render
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_texture(self):
        return {
            1: self.get_texture('textures/tile_1_1024.png'),
            2: self.get_texture('textures/tile_2_1024.png'),
            3: self.get_texture('textures/tile_3_1024.png'),
            4: self.get_texture('textures/tile_4_1024.png'),
        }