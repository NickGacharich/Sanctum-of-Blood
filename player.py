import pygame
import random
import level_up_manager
from level_up_manager import LevelUpManager
from settings import *
import math
import pygame as pg
import os
from map import Map

current_time = pygame.time.get_ticks()

class Player:
    def __init__(self, map, level_up_manager):
        self.x = WINDOW_WIDTH / 2
        self.y = WINDOW_HEIGHT / 2
        self.last_dx = 0
        self.last_dy = -1
        self.shot_ray = None
        self.rect = pg.Rect(self.x, self.y, 32, 32)
        self.radius = 3
        self.map = map
        self.level_up_manager = level_up_manager
        self.turnDirection = 0
        self.walkDirection = 0
        self.rotation_angle = 0
        self.move_speed = 3
        self.max_mana = 100
        self.mana = 0
        self.max_health = 100
        self.health = self.max_health
        self.rotationSpeed = 2 * (math.pi / 180)
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.last_damage_time = 0
        self.damage_cooldown = 500  # ms

        # --- Weapon Setup ---
        # Walking/idle frames for dual shotguns
        self.weapon_frames = [pg.image.load(f"sprites/player/idle/player_walking_{i}.png") for i in range(1, 7)]
        self.weapon_frame_index = 0
        self.weapon_frame_timer = 0

        self.player_damage = [
            pygame.mixer.Sound("assets/sounds/player_damage1.wav"),
            pygame.mixer.Sound("assets/sounds/player_damage2.wav"),
        ]

        self.shotgun_sounds = [
            pygame.mixer.Sound("assets/sounds/shotgun1.wav"),
            pygame.mixer.Sound("assets/sounds/shotgun2.wav"),
        ]


        # Magic abilities
        self.abilities = []

        # Shooting frames (muzzle flash + recoil)
        self.shoot_frames = []
        self.shoot_frame_method()

        self.shooting = False
        self.shoot_frame_index = 0
        self.shoot_frame_timer = 0
        self.last_shot_time = current_time

        self.damage = 10
        self.fire_rate = 400  # ms between shots
        self.time_since_shot = 0
        self.is_dead = False
        self.is_shooting = False
        self.did_shoot = False
        self.shoot_timer = 0

    def update(self, dt, demon_manager):
        keys = pg.key.get_pressed()

        self.turnDirection = 0
        self.walkDirection = 0

        if keys[pg.K_RIGHT]:
            self.turnDirection = 1
        if keys[pg.K_LEFT]:
            self.turnDirection = -1
        if keys[pg.K_UP]:
            self.walkDirection = 1
        if keys[pg.K_DOWN]:
            self.walkDirection = -1

        # Apply rotation
        self.rotation_angle += self.turnDirection * self.rotationSpeed
        self.rotation_angle %= (2 * math.pi)

        # Attempted movement
        moveStep = self.walkDirection * self.move_speed
        new_x = self.x + math.cos(self.rotation_angle) * moveStep
        new_y = self.y + math.sin(self.rotation_angle) * moveStep

        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

            self.last_dx = dx
            self.last_dy = dy

        for ability in self.abilities:
            if hasattr(ability, "crosses"):
                ability.update(dt, self, demon_manager)
            else:
                ability.update(dt, self, demon_manager)

        # --- WALL COLLISION CHECK ---
        # Move on X axis only if safe
        if not self.is_wall(new_x, self.y):
            self.x = new_x

        # Move on Y axis only if safe
        if not self.is_wall(self.x, new_y):
            self.y = new_y



    def is_wall(self, x, y):
        # Prevent crashes if player walks outside map bounds
        if x < 0 or y < 0:
            return True

        grid_x = int(x // TILESIZE)
        grid_y = int(y // TILESIZE)

        # Out-of-bounds is treated as a wall
        if grid_y >= len(self.map.current_map) or grid_x >= len(self.map.current_map[0]):
            return True

        return self.map.current_map[grid_y][grid_x] in [1,2,3]

    def map_spawn(self):
        if self.map.current_map == self.map.outside_house:
            self.x = WINDOW_WIDTH / 2
            self.y = WINDOW_HEIGHT / 2

    def take_damage(self, dmg):
        current_time = pygame.time.get_ticks()

        # prevent sound spam
        if current_time - self.last_damage_time < self.damage_cooldown:
            return

        self.last_damage_time = current_time

        self.health -= dmg
        print("Player hurt! HP:", self.health)

        damage_sound = random.choice(self.player_damage)
        damage_sound.set_volume(1.0)
        damage_sound.play()

        if self.health <= 0:
            self.is_dead = True
            print("PLAYER IS DEAD")

    def gain_xp(self, amount):
        self.xp += amount

        if self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1

            # Trigger the actual UI
            self.level_up_manager.trigger()

            # Increase required XP
            self.xp_to_next_level = int(self.xp_to_next_level * 1.4)

            return True

        return False

    def update_rect(self):
        # Keep the rect in sync with the player's raycasting position
        self.rect.center = (self.x, self.y)

    # --- Update Weapon Animation ---
    def update_weapon(self, dt):

        # Update cooldown timer
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
            if self.shoot_timer < 0:
                self.shoot_timer = 0

        if self.shooting and current_time - self.last_shot_time > 500:  # 500 ms delay
            shotgun_sound = random.choice(self.shotgun_sounds)
            shotgun_sound.set_volume(0.5)
            shotgun_sound.play()  # adjust volume (0.0 to 1.0)
            self.last_shot_time = current_time

        # Idle/walk animation
        self.weapon_frame_timer += dt
        if self.weapon_frame_timer > 120:
            self.weapon_frame_timer = 0
            self.weapon_frame_index = (self.weapon_frame_index + 1) % len(self.weapon_frames)

        # --- SHOOTING ANIMATION ---
        if self.shooting:

            self.shoot_frame_timer += dt
            if self.shoot_frame_timer > 30:  # speed of shooting frames
                self.shoot_frame_timer = 0
                self.shoot_frame_index += 1

                # End of shooting animation
                if self.shoot_frame_index >= len(self.shoot_frames):
                    self.shooting = False
                    self.shoot_frame_index = 0

    def shoot_frame_method(self):
        for i in range(1,7):
            image = pg.image.load(f"sprites/player/shooting/player_shooting_{i}.png").convert()
            image.set_colorkey((0,0,0))
            self.shoot_frames.append(image)


    # --- Shooting Method ---
    def shoot(self):
        shots = getattr(self, "multishot", 1)

        current_time = pygame.time.get_ticks()

        for i in range(shots):
            spread = (i - shots // 2) * 0.1
            angle = self.rotation_angle + spread

            # create ray using angle
        if self.shoot_timer <= 0:
            self.shoot_timer = self.fire_rate
            self.shooting = True
            self.shoot_frame_index = 0
            self.shoot_frame_timer = 0

            shotgun_sound = random.choice(self.shotgun_sounds)
            shotgun_sound.set_volume(random.uniform(0.4, 0.7))
            shotgun_sound.play()

            self.fire_weapon()


    def fire_weapon(self):
        ray_angle = self.rotation_angle
        start_x, start_y = self.x, self.y
        end_x = start_x + math.cos(ray_angle) * 2000
        end_y = start_y + math.sin(ray_angle) * 2000

        self.did_shoot = True
        self.shot_ray = (start_x, start_y, end_x, end_y)
        print("SHOT FIRED")  # DEBUG

    # --- Render Weapon ---
    def render_weapon(self, screen):
        if self.shooting:
            frame = self.shoot_frames[self.shoot_frame_index]
        else:
            frame = self.weapon_frames[self.weapon_frame_index]

        # scale frame (optional)
        frame = pg.transform.scale(frame, (int(frame.get_width()), int(frame.get_height())))

        # position bottom center of screen
        x = (WINDOW_WIDTH // 2) - (frame.get_width() // 2)
        y = WINDOW_HEIGHT - frame.get_height() + 150
        screen.blit(frame, (x, y))

    def render(self, screen):
        pg.draw.circle(screen, (255,0,0), (self.x, self.y), self.radius)

        pg.draw.line(screen, (255,0,0), (self.x, self.y), (self.x + math.cos(self.rotation_angle) * 50, self.y + math.sin(self.rotation_angle) * 50))



    #def movement(self):
    #    sin_a = math.sin(self.angle)
    #    cos_a = math.cos(self.angle)
    #    dx, dy = 0, 0
    #    speed = PLAYER_SPEED * self.game.delta_time
    #    speed_sin = speed * sin_a
    #    speed_cos = speed * cos_a

    #    keys = pg.key.get_pressed()
    #    if keys[pg.K_w]:
    #        dx += speed_cos
    #        dy += speed_sin
    #    if keys[pg.K_s]:
    #        dx += -speed_cos
    #        dy += -speed_sin
    #    if keys[pg.K_a]:
    #        dx += speed_sin
    #        dy += -speed_cos
    #    if keys[pg.K_d]:
    #        dx += -speed_sin
    #        dy += speed_cos

        #self.check_wall_collision(dx, dy)

    #def check_wall(self, x, y):
        #return (x, y) not in self.map.grid

    #def check_wall_collision(self, dx, dy):
        #scale = PLAYER_SIZE_SCALE / self.game.delta_time
        #if self.check_wall(int(self.x + dx), int(self.y)):
        #    self.x += dx
        #if self.check_wall(int(self.x), int(self.y + dy)):
        #    self.y += dy

    #def draw(self):
        #pg.draw.line(self.game.screen, 'yellow', (self.x * 100, self.y * 100 ), (self.x * 100 + WIDTH * math.cos(self.angle),self.y * 100 + WIDTH * math.sin(self.angle)), 2)
        #pg.draw.circle(self.game.screen, 'green', (self.x * 100, self.y * 100), 15)
    #    pass

    #def mouse_control(self):
    #    mx, my = pg.mouse.get_pos()
    #    if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
    #        pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
    #    self.rel = pg.mouse.get_rel()[0]
    #    self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
    #    self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time



