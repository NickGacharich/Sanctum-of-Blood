import pygame
from pygame import font

pygame.init()

from PlayerHUD import PlayerHUD
from raycaster import Raycaster
from settings import *
from map import Map
from player import Player
from demon_manager import DemonManager
from level_up_manager import LevelUpManager
from wave_manager import WaveManager
from abilities import Ability

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

map = Map()

level_up_manager = LevelUpManager()

player = Player(map, level_up_manager)

raycaster = Raycaster(player, map)

demon_manager = DemonManager(map, level_up_manager)

wave_manager = WaveManager(map, demon_manager, player)

demon_manager.wave_manager = wave_manager

wave_font = pygame.font.SysFont("Arial", 24)


print("Starting game...")
# start wave spawn
wave_manager.start_next_wave()

hud = PlayerHUD(max_health=100, max_mana=50, max_xp=100, player=player)

background_image = pygame.image.load("background.png")

game_over_playing = False

pygame.mixer.init()
background_sound = pygame.mixer.Sound("assets/sounds/background_music.wav")
background_sound.set_volume(0.4)

game_over_sound = pygame.mixer.Sound("assets/sounds/game_over.wav")
game_over_sound.set_volume(0.4)

EXIT_ZONE_RECT = pygame.Rect(320, 288, 150, 150)
fire_attacks = []

clock = pygame.time.Clock()
dt = 0
background_sound.play(-1)

def draw_game_over(screen):


    font_big = pygame.font.SysFont("Arial", 72)
    font_small = pygame.font.SysFont("Arial", 32)

    # Dark overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Text
    game_over_text = font_big.render("GAME OVER", True, (200, 0, 0))
    restart_text = font_small.render("Press R to Restart", True, (255, 255, 255))

    screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
    screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2))

def reset_game():
    global player

    player.health = player.max_health
    player.is_dead = False
    player.x = WINDOW_WIDTH / 2
    player.y = WINDOW_HEIGHT / 2
    player.level = 1
    player.xp_to_next_level = 100
    player.xp = 0
    player.move_speed = 3
    player.max_mana = 100
    player.mana = 0
    player.fire_rate = 400
    player.damage = 10
    wave_manager.wave = 0
    wave_manager.kills_this_wave = 0
    wave_manager.required_kills = 5
    demon_manager.demons.clear()

    wave_manager.start_next_wave()

while True:
    dt = clock.tick(60)

    keys = pygame.key.get_pressed()




    # INPUT
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if not level_up_manager.active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.shoot()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                player.shoot()
                keys = pygame.key.get_pressed()

        if not level_up_manager.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    if len(player.abilities) > 0:
                        player.abilities[0].use(player, None)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and len(player.abilities) > 0:
                player.abilities[0].use(player, None)

            if event.key == pygame.K_2 and len(player.abilities) > 1:
                player.abilities[1].use(player, None)

    # LEVEL-UP PAUSE
    if level_up_manager.active:
        level_up_manager.render(screen)
        pygame.display.update()
        continue

    if level_up_manager.selected:
        level_up_manager.apply_upgrade(player)
        level_up_manager.selected = None

    # UPDATE
    if not player.is_dead:
        player.update(dt, demon_manager)
        player.update_weapon(dt)
        wave_manager.update(dt)
        demon_manager.update(player, dt, raycaster)




        # RENDER
        screen.fill((0,0,0))
        raycaster.castAllRays()
        raycaster.render(screen)
        demon_manager.render(screen, player, raycaster)

        for ability in player.abilities:
            if hasattr(ability, "crosses"):
                for cross in ability.crosses:
                    screen_x = WINDOW_WIDTH // 2 + (cross["x"] - player.x)
                    screen_y = WINDOW_HEIGHT // 2 + (cross["y"] - player.y)
                    print("Drawing cross")  # DEBUG
                    print("last_dx:", player.last_dx, "last_dy:", player.last_dy)
                    img = ability.cross_image
                    img = pygame.transform.scale(img, (64, 64))
                    # glow
                    glow = img.copy()
                    glow.fill((255, 200, 100), special_flags=pygame.BLEND_RGB_ADD)
                    # draw glow first (behind)
                    screen.blit(glow, (screen_x - img.get_width() // 2,
                                      screen_y - img.get_height() // 2))
                    # draw sprite on top
                    screen.blit(img, (screen_x - img.get_width() // 2,
                                      screen_y - img.get_height() // 2))

        hud.render(screen,
                   player.health,
                   player.max_health,
                   player.mana,
                   player.max_mana,
                   player.xp,
                   player.xp_to_next_level)

        color = (255, 255, 255)

        if wave_manager.wave >= 5:
            color = (255, 200, 0)
        if wave_manager.wave >= 10:
            color = (255, 0, 0)

        wave_text = wave_font.render(f"Wave: {wave_manager.wave}", True, color)

        # top-right position
        bg_rect = wave_text.get_rect()
        bg_rect.topright = (WINDOW_WIDTH - 10, 10)
        bg_rect.inflate_ip(10, 6)

        pygame.draw.rect(screen, (0, 0, 0), bg_rect)
        screen.blit(wave_text, bg_rect)

        player.render_weapon(screen)

        if wave_manager.show_wave_text:
            font = pygame.font.SysFont("Arial", 72)

            text = f"WAVE {wave_manager.wave}"

            # fade effect
            alpha = int(255 * (wave_manager.wave_text_timer / wave_manager.wave_text_duration))

            # scale effect
            scale = 1 + 0.3 * (1 - wave_manager.wave_text_timer / wave_manager.wave_text_duration)

            text_surface = font.render(text, True, (255, 255, 255))
            text_surface = pygame.transform.rotozoom(text_surface, 0, scale)

            text_surface.set_alpha(alpha)

            rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

            glow = text_surface.copy()
            glow.fill((255, 100, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(glow, rect)
            screen.blit(text_surface, rect)

    if player.is_dead:

        if not game_over_playing:
            background_sound.stop()
            game_over_sound.play(-1)
            game_over_playing = True

        draw_game_over(screen)

        if keys[pygame.K_r]:
            game_over_sound.stop()
            background_sound.play(-1)

            game_over_playing = False
            reset_game()

    pygame.display.update()

    # IMPORTANT — reset only after updates
    player.did_shoot = False


