import pygame
import math
from settings import *
from pathfinding import a_star
from player import Player

class Demon:
    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.player = player

        # tile-space path
        self.path = []
        self.path_index = 0
        self.repath_timer = 0
        self.repath_interval = 800  # ms

        # animation
        self.speed = 1.5
        self.health = 100
        self.state = "walk"
        self.frame = 0
        self.frame_timer = 0
        self.flash_timer = 0
        self.flash_duration = 100
        self.xp_reward = 20
        self.distance_to_player = 9999
        self.attack_sound = pygame.mixer.Sound("assets/sounds/ghost_demon_attack.wav")
        self.attack_sound.set_volume(0.5)
        self.death_sound = pygame.mixer.Sound("assets/sounds/ghost_demon_death.wav")
        self.death_sound.set_volume(0.8)

        # Load sprites
        self.walk_frames = [pygame.image.load(f"sprites/demon/walk/ghost_walk_{i}.png") for i in range(1,8)]
        self.attack_frames = [pygame.image.load(f"sprites/demon/attack/ghost_attack_{i}.png") for i in range(1,8)]
        self.death_frames = [pygame.image.load(f"sprites/demon/death/ghost_death_{i}.png") for i in range(1,8)]
        self.current_sprite = self.walk_frames[0]

        self.dead = False

    # -----------------------------
    # TILE HELPERS
    # -----------------------------
    def tile_pos(self):
        return int(self.x // TILESIZE), int(self.y // TILESIZE)

    def start_death(self):
        self.death_sound.play()
        self.state = "die"
        self.frame = 0
        self.frame_timer = 0
        self.dead = True
        self.current_sprite = self.death_frames[0]

    def take_damage(self, amount):
        if self.dead:
            return

        self.health -= amount
        print("Demon hit! HP:", self.health)

        self.flash_timer = self.flash_duration

        # ✅ APPLY LIFESTEAL ON HIT
        if hasattr(self.player, "lifesteal"):
            lifesteal_amount = max(1, int(amount * self.player.lifesteal))
            self.player.health = min(
                self.player.max_health,
                self.player.health + lifesteal_amount
            )
            print("Lifesteal healed:", lifesteal_amount)

        # ✅ HANDLE DEATH SEPARATELY
        if self.health <= 0:
            self.start_death()

    def update(self, player, dt, grid):
        # world distance
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        self.distance_to_player = dist

        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.state == "die":
            self.update_animation(dt)
            return

        # ATTACK
        if dist < 30:
            self.attack_sound.play()
            self.state = "attack"

            if not hasattr(self, "attack_timer"):
                self.attack_timer = 0
            self.attack_timer += dt
            if self.attack_timer >= 500:
                self.attack_timer = 0
                player.take_damage(10)

        else:
            self.state = "walk"

        # PATHFINDING UPDATE
        self.repath_timer += dt
        if self.repath_timer > self.repath_interval:
            self.repath_timer = 0
            self.calculate_path_to_player(player, grid)

        # follow path
        if self.state == "walk":
            self.follow_path(dt)

        # animate
        self.update_animation(dt)

    # -----------------------------
    # PATHFINDING → Player
    # -----------------------------
    def calculate_path_to_player(self, player, grid):
        demon_tile = self.tile_pos()
        player_tile = (int(player.x // TILESIZE), int(player.y // TILESIZE))

        new_path = a_star(grid, demon_tile, player_tile)
        if new_path and len(new_path) > 1:
            self.path = new_path
            self.path_index = 1  # skip index 0 (demon’s current tile)

    def follow_path(self, dt):
        if not self.path or self.path_index >= len(self.path):
            return

        target_tile = self.path[self.path_index]
        target_x = target_tile[0] * TILESIZE + TILESIZE // 2
        target_y = target_tile[1] * TILESIZE + TILESIZE // 2

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < 2:
            self.path_index += 1
            return

        self.x += (dx / dist) * self.speed * (dt / 1000)
        self.y += (dy / dist) * self.speed * (dt / 1000)

    # -----------------------------
    # ANIMATION
    # -----------------------------
    def update_animation(self, dt):
        self.frame_timer += dt
        if self.frame_timer < 120:
            return

        self.frame_timer = 0

        # --- WALKING ANIMATION ---
        if self.state == "walk":
            self.frame = (self.frame + 1) % len(self.walk_frames)
            self.current_sprite = self.walk_frames[self.frame]

        # --- ATTACK ANIMATION ---
        elif self.state == "attack":
            self.frame = (self.frame + 1) % len(self.attack_frames)
            self.current_sprite = self.attack_frames[self.frame]

        # --- DEATH ANIMATION ---
        elif self.state == "die":
            if self.frame < len(self.death_frames) - 1:
                self.frame += 1
                self.current_sprite = self.death_frames[self.frame]
            # once animation reaches last frame, freeze on last
    # -----------------------------
    # SPRITE ACCESS
    # -----------------------------
    def get_current_frame(self):
        sprite = self.current_sprite

        if self.flash_timer > 0 and int(self.flash_timer / 50) % 2 == 0:
            # Create a white flash version
            flash_sprite = sprite.copy()
            flash_sprite.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            return flash_sprite

        return sprite

    # -----------------------------
    # DEATH STATE
    # -----------------------------
    def kill(self):
        self.state = "die"
        self.frame = 0
        self.frame_timer = 0

    def is_dead_finished(self):
        return self.state == "die" and self.frame >= len(self.death_frames) - 1

class FastDemon(Demon):
    def __init__(self, x, y, player):
        super().__init__(x, y, player)
        print("Fast demon spawned")
        self.player = player
        self.speed = 2.5
        self.health = 40
        self.damage = 5
        self.xp_reward = 8
        self.attack_sound = pygame.mixer.Sound("assets/sounds/fast_demon_attack.wav")
        self.attack_sound.set_volume(0.5)
        self.death_sound = pygame.mixer.Sound("assets/sounds/fast_demon_death.wav")
        self.death_sound.set_volume(0.5)

        self.walk_frames = [pygame.image.load(f"sprites/demon_fast/walk/demon_fast_walk_{i}.png").convert_alpha() for i in range(1,6)]
        self.attack_frames = [pygame.image.load(f"sprites/demon_fast/attack/demon_fast_attack_{i}.png").convert_alpha() for i in range(1,5)]
        self.death_frames = [pygame.image.load(f"sprites/demon_fast/death/demon_fast_death_{i}.png").convert_alpha() for i in range(1,5)]

class TankDemon(Demon):
    def __init__(self, x, y, player):
        super().__init__(x, y, player)
        print("Tank demon spawned")
        self.player = player
        self.speed = 2.0
        self.health = 140
        self.damage = 25
        self.xp_reward = 20
        self.attack_sound = pygame.mixer.Sound("assets/sounds/tank_demon_attack.wav")
        self.attack_sound.set_volume(0.5)
        self.death_sound = pygame.mixer.Sound("assets/sounds/tank_demon_death.wav")
        self.death_sound.set_volume(0.5)

        self.walk_frames = [pygame.image.load(f"sprites/demon_tank/walk/demon_tank_walk_{i}.png").convert_alpha() for i in range(1, 6)]
        self.attack_frames = [pygame.image.load(f"sprites/demon_tank/attack/demon_tank_attack_{i}.png").convert_alpha() for i in range(1, 6)]
        self.death_frames = [pygame.image.load(f"sprites/demon_tank/death/demon_tank_death_{i}.png").convert_alpha() for i in range(1, 5)]

class ShooterDemon(Demon):
    def __init__(self, x, y, player):
        super().__init__(x, y, player)
        print("Shooter demon spawned")
        self.player = player
        self.speed = 1.75
        self.health = 60
        self.damage = 8
        self.xp_reward = 12
        self.shoot_cooldown = 2.0
        self.attack_sound = pygame.mixer.Sound("assets/sounds/shooter_demon_attack.wav")
        self.attack_sound.set_volume(0.5)
        self.death_sound = pygame.mixer.Sound("assets/sounds/shooter_demon_death.wav")
        self.death_sound.set_volume(0.5)

        self.walk_frames = [pygame.image.load(f"sprites/demon_shooter/walk/demon_shooter_walk_{i}.png").convert_alpha() for i in range(1, 7)]
        self.attack_frames = [pygame.image.load(f"sprites/demon_shooter/attack/demon_shooter_attack_{i}.png").convert_alpha() for i in range(1, 7)]
        self.death_frames = [pygame.image.load(f"sprites/demon_shooter/death/demon_shooter_death_{i}.png").convert_alpha() for i in range(1, 7)]