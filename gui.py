import pygame
import time
import random
from draw_cards import *
from best_cards import *
from value_cards import *


# TODO# When gui is imported, a black screen is temporarily displayed. Fix this...
def draw_gui(game):
    draw_BG(game)
    draw_time(game)
    cards = game.cards
    for i in range(0, len(game.seat_positions)):
        seat_text = game.font.render(f"Seat No: {i + 1}", 1, "black")
        game.gui.blit(seat_text, game.seat_positions[i])
    draw_player_info(game)
    draw_dealer(game)

    if game.state == 'not_started':
        game.common_cards_shown = 0
    elif game.state == "pre_flop":
        game.common_cards_shown = 0
        draw_pot(game)
        draw_hidden_cards(game)

    elif game.state == "flop":
        game.common_cards_shown = 3
        draw_pot(game)
        draw_hidden_cards(game)
    elif game.state == "turn":
        game.common_cards_shown = 4
        draw_pot(game)
        draw_hidden_cards(game)
    elif game.state == "river":
        game.common_cards_shown = 5
        draw_pot(game)
        draw_hidden_cards(game)
    elif game.state == "showdown":
        game.common_cards_shown = 5
        draw_pot(game)
        draw_shown_cards(game)
        game.decide_winner()
        draw_winner(game)
    # print common cards according to game stage (depending on game.common_cards_shown)
    card_position = 0
    for card in cards[0:game.common_cards_shown]:
        game.gui.blit(card.image, (
            game.width / 2 + card_position * CARD_WIDTH - 2.5 * CARD_WIDTH, (game.height / 2) - 0.5 * CARD_HEIGHT))
        card_position += 1

    pygame.display.update()


def draw_hidden_cards(game):
    for i in range(0, game.num_p):
        game.gui.blit(game.joker, game.seat_positions[i])
        game.gui.blit(game.joker, (game.seat_positions[i][0] + CARD_WIDTH, game.seat_positions[i][1]))


def draw_shown_cards(game):
    for i in range(0, game.num_p):
        game.gui.blit(game.players[i].cards[0].image, game.seat_positions[i])
        game.gui.blit(game.players[i].cards[1].image,
                      (game.seat_positions[i][0] + CARD_WIDTH, game.seat_positions[i][1]))


def draw_player_info(game):
    for player in game.players:
        text = game.font.render(f"{player.name}:{player.chips}", 1, "black")
        game.gui.blit(text, (game.seat_positions[player.seat_number][0] - game.width / 50,
                             game.seat_positions[player.seat_number][1] - game.height / 15))
        bet_text = game.font.render(f"{player.bet}", 1, "black")
        game.gui.blit(bet_text, (
            game.seat_positions[player.seat_number][0], game.seat_positions[player.seat_number][1] + (2 * game.height / 10)))


def draw_pot(game):
    pot_text = game.font.render(f"Pot:{game.pot}", 1, "red")
    game.gui.blit(pot_text, (game.width / 2, game.height / 2 + game.height / 10))


def draw_winner(game):
    winner = game.players[game.winner_num]
    winner_text = game.font.render(f"{winner.name} WINS with:{categorize_value(winner.value)}", 1, "blue")
    game.gui.blit(winner_text, (358, 200))
    return game


def draw_dealer(game):
    # WIN.blit(game.dealer_image, (game.seat_positions[game.dealer][0]+game.width/50,game.seat_positions[
    # game.dealer][1]+game.height/5)) pygame.draw.circle(WIN, 'red', (game.seat_positions[game.dealer][
    # 0]+game.width/50,game.seat_positions[game.dealer][1]+game.height/5), 10,draw_bottom_left=True)  # DRAW CIRCLE
    dealer_text = game.font.render(f"D", 1, "red")
    game.gui.blit(dealer_text, (
        game.seat_positions[game.dealer_loc][0] + game.width / 15,
        game.seat_positions[game.dealer_loc][1] + game.height / 5))


def draw_time(game):
    time_text = game.font.render(f"Time: {int(time.time() - game.start_time)}", 1, "black")
    game.gui.blit(time_text, (0, 0))


def draw_BG(game):
    game.gui.blit(game.background, (0, 0))
