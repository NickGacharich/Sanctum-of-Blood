import pygame
import random

from pygame import event
from abilities import Fireball, Dash
from settings import *
pygame.font.init()
FONT = pygame.font.SysFont("Arial", 28)


class UpgradeCard:
    def __init__(self, name, effect, description="", icon_path=None):
        self.name = name
        self.effect = effect
        self.description = description
        self.rect = None

        if icon_path:
            self.icon = pygame.image.load(icon_path).convert_alpha()
            self.icon = pygame.transform.scale(self.icon, (48, 48))
        else:
            self.icon = None

class LevelUpManager:
    def __init__(self):
        self.active = False
        self.cards = []
        self.selected = None
        self.level_up_sound = pygame.mixer.Sound("assets/sounds/ominous_bell.wav")
        self.level_up_sound.set_volume(0.8)

        # Example upgrades
        self.available_upgrades = [
            UpgradeCard("More Health", self.upgrade_health, "+20 HP"),
            UpgradeCard("More Damage", self.upgrade_damage, "+5 damage"),
            UpgradeCard("Faster Shots", self.upgrade_fire_rate, "Shoot faster"),
            UpgradeCard("Move Speed", self.upgrade_speed,"Move Speed increase"),
            UpgradeCard("More Mana", self.upgrade_mana, "Mana +10"),
            UpgradeCard("Life Steal", self.upgrade_lifesteal, "Life Steal"),
            UpgradeCard("Multi Shot", self.upgrade_multishot, "Multi Shot increase"),
            UpgradeCard("Dash", effect=lambda player: player.abilities.append(Dash()), description="Dash forward [press 1] (15 mana)")

        ]


    def upgrade_health(self, player):
        player.max_health += 20



    def upgrade_damage(self, player):
        player.damage += 5


    def upgrade_fire_rate(self, player):
        player.fire_rate *= 0.85  # shoots faster


    def upgrade_speed(self, player):
        if player.move_speed < 15:
            player.move_speed += 1


    def upgrade_mana(self, player):
        player.max_mana += 15


    def upgrade_lifesteal(self, player):
        player.lifesteal = getattr(player, "lifesteal", 0) + 0.05


    def upgrade_multishot(self, player):
        player.multishot = getattr(player, "multishot", 1) + 1

    def upgrade_dash(self, player):
        player.abilities.append(Dash())
        print([a.name for a in player.abilities])

    def give_fireball(self, player):
        ability = Fireball()
        ability.spawn_crosses(player)
        player.abilities.append(ability)


    def trigger(self):
        self.active = True
        self.selected = None
        self.cards = random.sample(self.available_upgrades, 3)

    def render(self, screen):
        if not self.active:
            return

        self.level_up_sound.play()
        # Dim background
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))

        # Card text
        font = pygame.font.SysFont(None, 24)
        small_font = pygame.font.SysFont(None, 18)

        # Draw 3 cards
        card_width = 200
        card_height = 120
        padding = 20

        num_cards = len(self.cards)

        # how many cards per row?
        cards_per_row = max(1, WINDOW_WIDTH // (card_width + padding))

        # total rows needed
        rows = (num_cards + cards_per_row - 1) // cards_per_row

        start_y = (WINDOW_HEIGHT - (rows * (card_height + padding))) // 2

        mouse_pos = pygame.mouse.get_pos()

        click = pygame.mouse.get_pressed()[0]

        for i, card in enumerate(self.cards):
            row = i // cards_per_row
            col = i % cards_per_row

            x = col * (card_width + padding) + padding
            y = start_y + row * (card_height + padding)

            rect = pygame.Rect(x, y, card_width, card_height)
            card.rect = rect  # ✅ ALWAYS assign

            hovered = rect.collidepoint(mouse_pos)

            # --- DRAW CARD ---
            pygame.draw.rect(screen, (40, 40, 40), rect)

            if hovered:
                pygame.draw.rect(screen, (80, 80, 80), rect)

            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

            # --- ICON ---
            if card.icon:
                screen.blit(card.icon, (rect.x + 10, rect.y + 10))

            # --- NAME ---
            name_text = font.render(card.name, True, (255, 255, 255))
            screen.blit(name_text, (rect.x + 70, rect.y + 10))

            # --- DESCRIPTION ---
            desc_text = small_font.render(card.description, True, (200, 200, 200))
            screen.blit(desc_text, (rect.x + 10, rect.y + 70))

            # --- Hover ---
            if hovered:
                pygame.draw.rect(screen, (120, 120, 120), rect, 4)

            # --- CLICK ---
            if hovered and click:
                self.selected = card
                self.active = False

    def apply_upgrade(self, player):
        if self.selected:
            self.selected.effect(player)
            self.active = False

            player.health = player.max_health
            player.mana = player.max_mana


