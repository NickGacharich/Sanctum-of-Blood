# wave_manager.py
import random
from settings import *
from demon import Demon, FastDemon, TankDemon, ShooterDemon
from boss import Boss   # you will create this next
from demon_manager import DemonManager
from player import Player

class WaveManager:
    def __init__(self, map_ref, demon_manager, player):
        self.wave = 0
        self.kills_this_wave = 0
        self.required_kills = 5  # monsters per wave
        self.map = map_ref
        self.dm = demon_manager
        self.wave_active = False
        self.player = player
        self.show_wave_text = False
        self.wave_text_timer = 0
        self.wave_text_duration = 1500  # milliseconds

        # boss rotation
        self.boss_names = ["Wrath", "Greed", "Lust", "Pride", "Gluttony", "Envy", "Sloth"]
        self.next_boss_index = 0

    def start_next_wave(self):

        self.wave += 1

        # trigger splash
        self.show_wave_text = True
        self.wave_text_timer = self.wave_text_duration

        self.kills_this_wave = 0

        # spawn normal demons
        num_to_spawn = 3 + self.wave * 2
        self.required_kills = num_to_spawn

        grid = self.map.current_map

        enemy_type = random.choices(
            ["normal", "fast", "tank", "shooter"],
            weights=[50, 25, 15, 10]
        )[0]

        for _ in range(num_to_spawn):

            while True:
                row = random.randint(0, len(grid) - 1)
                col = random.randint(0, len(grid[0]) - 1)

                # spawn only on empty tiles
                if grid[row][col] == 0:
                    x = col * TILESIZE + TILESIZE // 2
                    y = row * TILESIZE + TILESIZE // 2
                    if self.wave < 3:
                        demon = Demon(x, y, self.player)

                    elif self.wave < 6:
                        demon = random.choice([Demon(x, y, self.player), FastDemon(x, y, self.player)])

                    elif self.wave < 10:
                        demon = random.choice([FastDemon(x, y, self.player), TankDemon(x, y, self.player)])

                    else:
                        demon = random.choice([FastDemon(x, y, self.player), TankDemon(x, y, self.player), ShooterDemon(x, y, self.player)])

                    self.dm.demons.append(demon)

                    break

    def demon_killed(self):
        self.kills_this_wave += 1

        # wave complete?
        if self.kills_this_wave >= self.required_kills:
            self.start_next_wave()


    def update(self, dt):
        if self.show_wave_text:
            self.wave_text_timer -= dt
            if self.wave_text_timer <= 0:
                self.show_wave_text = False