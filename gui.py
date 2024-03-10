import time
import random

import pygame

from card import categorize_value
from constants import *


class GUI:
    def __init__(self, delay=1):
        self.delay = delay

        self.width = DISPLAY_WIDTH
        self.height = DISPLAY_HEIGHT
        self.card_width = CARD_WIDTH
        self.card_height = CARD_HEIGHT

        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Texas Holdem")
        pygame.font.init()
        self.font = pygame.font.SysFont('comicsans', 30)
        self.background = pygame.transform.scale(pygame.image.load('Images/no back wood d2.png'),
                                                 (self.width, self.height))
        self.seat_positions = [(self.width / 2, self.height / 8),
                               (7 * self.width / 8, self.height / 8),
                               (7 * self.width / 8, 2 * self.height / 2.7),
                               (self.width / 2, 2 * self.height / 2.7),
                               (self.width / 8, 2 * self.height / 2.7),
                               (self.width / 8, self.height / 8)]
        self.joker = pygame.transform.scale(pygame.image.load("Cards/red_joker.png"),
                                            (self.card_width, self.card_height))
        self.red_chip = pygame.transform.scale(pygame.image.load("Images/red_chip.png"),
                                               (CHIP_WIDTH, CHIP_HEIGHT))
        self.blue_chip = pygame.transform.scale(pygame.image.load("Images/blue_chip.png"),
                                               (CHIP_WIDTH, CHIP_HEIGHT))
        self.green_chip = pygame.transform.scale(pygame.image.load("Images/green_chip.png"),
                                               (CHIP_WIDTH, CHIP_HEIGHT))
        self.purple_chip = pygame.transform.scale(pygame.image.load("Images/purple_chip.png"),
                                               (CHIP_WIDTH, CHIP_HEIGHT))
        self.red_chip_3d = pygame.transform.scale(pygame.image.load("Images/red_chip_3d.png"),
                                                  (CHIP_WIDTH, CHIP_HEIGHT))
        self.stack_10_green = pygame.transform.scale(pygame.image.load("Images/10_stack_green.png"),
                                                 (CHIP_WIDTH, CHIP_HEIGHT))
        self.stack_5_green = pygame.transform.scale(pygame.image.load("Images/5_stack_green.png"),
                                                 (CHIP_WIDTH, CHIP_HEIGHT))
        self.stack_10_red = pygame.transform.scale(pygame.image.load("Images/10_stack_red.png"),
                                                 (CHIP_WIDTH, CHIP_HEIGHT))

    def render_gui(self, game):
        self.render_bg()
        self.render_time(game)
        self.render_chips_test((500, 500))

        for i in range(0, len(self.seat_positions)):
            seat_text = self.font.render(f"Seat No: {i + 1}", 1, "black")
            self.display.blit(seat_text, self.seat_positions[i])
        self.render_player_info(game)
        self.render_dealer(game)
        if len(game.hand_players) == 1:
            # print("Not enough opponents")
            game.common_cards_shown = 5
            self.render_pot(game)
            self.render_shown_cards(game)
            # game.decide_winner()
            self.render_winners(game)

        elif game.state == 'not_started':
            game.common_cards_shown = 0
        elif game.state == "pre_flop":
            game.common_cards_shown = 0
            self.render_pot(game)
            self.render_hidden_cards(game)

        elif game.state == "flop":
            game.common_cards_shown = 3
            self.render_pot(game)
            self.render_hidden_cards(game)
        elif game.state == "turn":
            game.common_cards_shown = 4
            self.render_pot(game)
            self.render_hidden_cards(game)
        elif game.state == "river":
            game.common_cards_shown = 5
            self.render_pot(game)
            self.render_hidden_cards(game)
        elif game.state == "showdown":
            game.common_cards_shown = 5
            self.render_pot(game)
            self.render_shown_cards(game)
            # game.decide_winner()
            self.render_winners(game)
        # print common cards according to game stage (depending on game.common_cards_shown)
        card_position = 0
        for card in game.deck[0:game.common_cards_shown]:
            self.display.blit(card.image, (
                self.width / 2.08 + card_position * (self.card_width * 1.2) - 2.5 * self.card_width,
                (self.height / 2) - 0.5 * self.card_height))
            card_position += 1

        pygame.display.update()

    def render_card(self, card):
        self.display.blit(card.image, (100, 100))

    def render_hidden_cards(self, game):
        for i in range(0, game.num_p):
            if game.players[i] in game.hand_players:
                self.display.blit(self.joker, self.seat_positions[i])
                self.display.blit(self.joker,
                                  (self.seat_positions[i][0] + self.card_width, self.seat_positions[i][1]))

    def render_shown_cards(self, game):
        if not game.split:
            for i in range(0, game.num_p):
                if game.players[i] in game.hand_players:
                    self.display.blit(game.players[i].cards[0].image, self.seat_positions[i])
                    self.display.blit(game.players[i].cards[1].image,
                                      (self.seat_positions[i][0] + self.card_width, self.seat_positions[i][1]))
        else:
            for player in game.split_winners:
                self.display.blit(player.cards[0].image, self.seat_positions[player.seat_number])
                self.display.blit(player.cards[1].image,
                                  (self.seat_positions[player.seat_number][0] + self.card_width,
                                   self.seat_positions[player.seat_number][1]))

    def render_player_info(self, game):
        for player in game.players:
            text = self.font.render(f"{player.name}:{player.chips}", 1, "black")
            self.display.blit(text, (self.seat_positions[player.seat_number][0] - self.width / 50,
                                     self.seat_positions[player.seat_number][1] - self.height / 15))
            bet_text = self.font.render(f"{player.bet}", 1, "black")
            self.display.blit(bet_text, (
                self.seat_positions[player.seat_number][0],
                self.seat_positions[player.seat_number][1] + (2 * self.height / 10)))

    def render_pot(self, game):
        pot_text = self.font.render(f"Pot:{game.pot}", 1, "red")
        self.display.blit(pot_text, (self.width / 2, self.height / 2 + self.height / 10))

    def render_winners(self, game):
        if not game.split:
            winner = game.players[game.winner_loc]
            winner_text = self.font.render(f"{winner.name} WINS with:{categorize_value(winner.showdown_value)}", 1,
                                           "blue")
            self.display.blit(winner_text, (0.44 * self.width, 0.64 * self.height))

        else:
            winners_names = ','.join(player.name for player in game.split_winners)
            winner_text_1 = self.font.render(f"The pot is split. Winners are:", 1, "blue")
            winner_text_2 = self.font.render(f"{winners_names}", 1, "blue")
            self.display.blit(winner_text_1, (0.44 * self.width, 0.64 * self.height))
            self.display.blit(winner_text_2, (0.44 * self.width, 0.66 * self.height))

    def render_dealer(self, game):
        dealer_text = self.font.render(f"D", 1, "red")
        self.display.blit(dealer_text, (
            self.seat_positions[game.dealer_loc][0] + self.width / 15,
            self.seat_positions[game.dealer_loc][1] + self.height / 5))

    def render_time(self, game):
        time_text = self.font.render(f"Time: {int(time.time() - game.start_time)}", 1, "black")
        self.display.blit(time_text, (0, 0))

    def render_bg(self):
        self.display.fill("gray")
        self.display.blit(self.background, (0, 0))

    def render_chips_test(self, loc=(0, 0)):
        #for i in range(0,20):
        #    self.display.blit(self.red_chip, (loc[0]+(i*2), loc[1]-(i+0.5)))
        self.display.blit(self.stack_10_green
                          , (loc[0]+35, loc[1]+10))
        self.display.blit(self.stack_10_red, (loc[0]+55, loc[1]+20))
        self.display.blit(self.stack_5_green, (loc[0] - 45, loc[1] - 20))
        #self.display.blit(self.red_chip_3d, (loc[0]-35, loc[1]+20))

    """""""""
    def render_call_check_button(self, game):
        # Draw the button
        font = pygame.font.Font(None, 36)
        if game.players[3].bet != game.current_bet:
            text = font.render("Call", True, "white")
        else:
            text = font.render("Check", True, "white")
        text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        pygame.draw.rect(self.display, "black", (button_x, button_y, button_width, button_height))
        self.display.blit(text, text_rect)

    
    def render_fold_button(self):
        # Draw the button
        font = pygame.font.Font(None, 36)
        text_2 = font.render("Fold", True, "white")
        text_rect_2 = text_2.get_rect(center=(button_x+button_width*1.05 + button_width // 2 , button_y + button_height // 2))
        pygame.draw.rect(self.display, "black", (button_x+button_width*1.05, button_y, button_width, button_height))
        self.display.blit(text_2, text_rect_2)

    def render_raise_sliding_bar(self):
        font = pygame.font.Font(None, 24)

        # Draw the bar
        pygame.draw.rect(self.display, "yellow", (bar_x, bar_y, bar_width, bar_height))

        # Draw the handle
        pygame.draw.rect(self.display, "blue", (handle_x, handle_y, handle_width, handle_height))

        # Draw value text
        value_text = font.render(
            f"{int((handle_x - bar_x) / (bar_width - handle_width) * (max_value - min_value) + min_value)}", True,
            "BLACK")
        self.display.blit(value_text, (bar_x + bar_width + 10, bar_y + (bar_height - value_text.get_height()) // 2))
    """""""""
