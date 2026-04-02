import pygame
pygame.font.init()
from settings import *
from player import Player

class PlayerHUD:
    def __init__(self, max_health=100, max_mana=100, max_xp=100, player=Player):
        # Max values
        self.player = player
        self.max_health = max_health
        self.max_mana = max_mana
        self.max_xp = max_xp

        # Current values
        self.health = max_health
        self.mana = max_mana
        self.xp = 0
        self.max_xp = max_xp

        # Bar dimensions
        self.bar_width = 100
        self.bar_height = 10
        self.bar_spacing = 5
        self.offset_x = 10
        self.offset_y = 10

        # Font for numbers
        self.font = pygame.font.SysFont('Arial', 16)


    # Reduce health
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    # Reduce mana
    def use_mana(self, amount):
        self.mana -= amount
        if self.mana < 0:
            self.mana = 0

    # Gain experience
    def gain_xp(self, amount):
        self.xp += amount
        if self.xp > self.max_xp:
            self.xp = self.max_xp

    def draw_health_bar(self, screen):
        # HEALTH BAR
        health_ratio = self.health / self.max_health
        health_bar_rect = pygame.Rect(self.offset_x, self.offset_y, int(self.bar_width * health_ratio), self.bar_height)
        pygame.draw.rect(screen, (200, 0, 0), health_bar_rect)  # Red bar
        pygame.draw.rect(screen, (255, 255, 255), (self.offset_x, self.offset_y, self.bar_width, self.bar_height), 2)

        # HEALTH TEXT
        health_text = self.font.render(f"HP: {self.health}/{self.max_health}", True, (255, 255, 255))
        screen.blit(health_text, (self.offset_x + self.bar_width + 10, self.offset_y))

    def draw_mana_bar(self, screen):
        # MANA BAR
        mana_ratio = max(0, min(1, self.mana / self.max_mana))
        mana_bar_rect = pygame.Rect(self.offset_x, self.offset_y + self.bar_height + self.bar_spacing,
                                    int(self.bar_width * mana_ratio), self.bar_height)
        pygame.draw.rect(screen, (0, 0, 200), mana_bar_rect)  # Blue bar
        pygame.draw.rect(screen, (255, 255, 255), (self.offset_x, self.offset_y + self.bar_height + self.bar_spacing,
                                                   self.bar_width, self.bar_height), 2)
        # MANA TEXT
        mana_text = self.font.render(f"MP: {self.mana}/{self.max_mana}", True, (255, 255, 255))
        screen.blit(mana_text,
                    (self.offset_x + self.bar_width + 10, self.offset_y + self.bar_height + self.bar_spacing))

    def draw_xp_bar(self, screen):
        # XP BAR
        xp_ratio = self.xp / self.max_xp
        xp_bar_rect = pygame.Rect(self.offset_x, self.offset_y + 2 * (self.bar_height + self.bar_spacing),
                                  int(self.bar_width * xp_ratio), self.bar_height)
        pygame.draw.rect(screen, (0, 200, 0), xp_bar_rect)  # Green bar
        pygame.draw.rect(screen, (255, 255, 255),
                         (self.offset_x, self.offset_y + 2 * (self.bar_height + self.bar_spacing),
                          self.bar_width, self.bar_height), 2)
        # XP TEXT
        xp_text = self.font.render(f"XP: {self.xp}/{self.max_xp}", True, (255, 255, 255))
        screen.blit(xp_text,
                    (self.offset_x + self.bar_width + 10, self.offset_y + 2 * (self.bar_height + self.bar_spacing)))

    def draw_abilities(self, screen):
        for i, ability in enumerate(self.player.abilities):
            text = self.font.render(f"{i + 1}: {ability.name}", True, (255, 255, 255))
            screen.blit(text, (10, 100 + i * 20))

    # Draw the HUD
    def render(self, screen, health, max_health, mana, max_mana, xp, max_xp):
        # update internal HUD values
        self.health = health
        self.max_health = max_health
        self.mana = mana
        self.max_mana = max_mana
        self.xp = xp
        self.max_xp = max_xp

        # now draw bars using these updated values
        self.draw_health_bar(screen)
        self.draw_mana_bar(screen)
        self.draw_xp_bar(screen)



