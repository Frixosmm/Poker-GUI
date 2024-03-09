import time

import pygame

from card import draw_cards, best_cards, categorize_value
from player import Player
from constants import *


class Game:
    def __init__(self, num_p=6, bb=2, start_funds=100):
        self.num_p = num_p
        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.state = "not_started"
        self.cards = draw_cards(5 + num_p * 2)
        self.pot = 0
        self.big_blind_amount = bb
        self.small_blind_amount = bb / 2
        self.current_bet = 0
        self.start_funds = start_funds
        self.winner_loc = -1
        self.players = []
        self.hand_players = []
        for i in range(0, self.num_p):
            self.players.append(Player("Player" + str(i + 1), self.start_funds, [], i))
            # self.cards[5 + i * 2:7 + i * 2]
        for player in self.players:
            if player.chips > 0:
                self.hand_players.append(player)

        self.common_cards_show = 0
        self.dealer_loc = self.hand_players[-1].seat_number

        self.new_round = None
        self.update_bool = True
        self.actions_remaining = 0
        self.hand_count = 0
        self.acting_player = None
        self.previous_bet = False
        self.previous_bet_amount: float
        self.previous_bet_amount = 0.0
        self.round_done = True
        self.winners_found = False
        self.split = False
        self.split_winners = None

    def check_chip_count(self):
        total_chips = self.start_funds * self.num_p

        current_chips = 0
        for player in self.players:
            current_chips += player.chips

        current_chips += self.pot

        if total_chips != current_chips:
            print(f"GAME CORRUPTED!!!: Chip count is wrong. It is {current_chips}")

    def deal_cards(self):
        for i in range(0, self.num_p):
            self.players[i].cards = self.cards[5 + i * 2:7 + i * 2]
            # Highest value card is first
            if self.players[i].cards[0].value < self.players[i].cards[1].value:
                self.players[i].cards[0], self.players[i].cards[1] = self.players[i].cards[1], self.players[i].cards[0]

            if self.players[i].cards[0].value == self.players[i].cards[0].value and self.players[i].cards[0].suit < \
                    self.players[i].cards[1].suit:
                self.players[i].cards[0].suit, self.players[i].cards[1].suit = self.players[i].cards[1].suit, \
                    self.players[i].cards[0].suit

            # Each player calculates the value of their starting hand
            # for player in self.players:
            #    player.value_starting_hand()

    def next_dealer_pos(self):
        check_seat = (self.dealer_loc + 1) % self.num_p
        while self.players[check_seat] not in self.hand_players:
            check_seat = (check_seat + 1) % self.num_p
        self.dealer_loc = check_seat

    def post_blinds(self):
        dealer = self.players[self.dealer_loc]
        # If dealer still in game, find his
        # position in active player list, and
        # move forward by correct increment
        # without going out of index.
        if dealer in self.hand_players:
            dealer_index = self.hand_players.index(dealer)
            sb_index = (dealer_index + 1) % (len(self.hand_players))
            bb_index = (dealer_index + 2) % (len(self.hand_players))
        else:
            # Dealer is out of the game, so find the next "taken" seat after dealer seat
            search = (self.dealer_loc + 1) % self.num_p
            while self.players[search] not in self.hand_players:
                search = (search + 1) % self.num_p
            sb_index = self.hand_players.index(self.players[search])
            bb_index = (sb_index + 1) % (len(self.hand_players))

        small_blind = self.hand_players[sb_index]
        big_blind = self.hand_players[bb_index]
        # Players place max blinds or whatever they have left
        small_blind.bet = min(self.small_blind_amount, small_blind.chips)
        big_blind.bet = min(self.big_blind_amount, big_blind.chips)
        # pot is increased
        self.pot += small_blind.bet + big_blind.bet
        # current bet is max of small blind bet or big blind bet
        self.current_bet = max(small_blind.bet, big_blind.bet)
        # chips reduced
        small_blind.chips -= small_blind.bet
        big_blind.chips -= big_blind.bet
        #
        self.actions_remaining = len(self.hand_players)

    def new_game(self):
        if self.pot != 0:
            for player in self.hand_players:  # use previous hand players to give back chips
                player.chips += player.bet
                player.bet = 0
            self.pot = 0
            for player in self.players:
                player.bet = 0
        self.hand_count += 1
        self.current_bet = 0
        self.state = "pre_flop"
        self.hand_players = self.players.copy()
        for player in self.players:  # Knocked out players don't participate in next hand.
            if player.chips <= 0:
                self.hand_players.remove(player)
            player.best_five = None
            player.showdown_value = 0
            player.bet = 0
            player.bet_amount = 0
            player.raise_amount = 0
            player.playing_for = 0

        self.cards = draw_cards(5 + len(self.players) * 2)
        self.deal_cards()

        ####test
        """""""""
        for player in self.hand_players:
            player.cards[0].make_specific(10, 3)
            player.cards[1].make_specific(2, 1)

        self.hand_players[1].cards[0].make_specific(12, 3)
        self.hand_players[1].cards[1].make_specific(11, 4)

        self.hand_players[2].cards[0].make_specific(12, 1)
        self.hand_players[2].cards[1].make_specific(7, 4)

        self.cards[0].make_specific(8, 4)
        self.cards[1].make_specific(3, 4)
        self.cards[2].make_specific(4, 4)
        self.cards[3].make_specific(9, 3)
        self.cards[4].make_specific(6, 4)

        ####test
         """""""""
        for player in self.hand_players:
            player.value_starting_hand()
        self.next_dealer_pos()
        # self.update_acting_player()

        self.post_blinds()
        self.winners_found = False

        self.split = False
        self.split_winners = []

        self.previous_bet = False

    def next_stage(self):
        if self.state == 'not_started':
            self.state = 'pre_flop'
        elif self.state == 'pre_flop':
            self.state = 'flop'
        elif self.state == 'flop':
            self.state = 'turn'
        elif self.state == 'turn':
            self.state = 'river'
        elif self.state == 'river':
            self.state = 'showdown'

    def decide_winner(self):
        print("-------------------SHOWDOWN-----------------")
        if len(self.hand_players) == 1:
            # Single player so single winner
            self.winner_loc = self.players.index(self.hand_players[0])
            self.players[self.winner_loc].chips += self.pot
            self.pot = 0
        else:  # Multiple hand players
            for player in self.hand_players:  # Assign active players their best cards and showdown value
                valued_cards = player.cards + self.cards[0:5]
                player.best_five, player.showdown_value = best_cards(valued_cards)
                # TODO # showdown value is wrong for last digit when flush and lowest is 2...
                # but it is correct if calculated in test scenario...
                #print(f"Cards are:{player.best_five[0].combo},{player.best_five[1].combo},{player.best_five[2].combo},{player.best_five[3].combo},{player.best_five[4].combo},")
                #print(f"Value is: {player.showdown_value}")
            self.hand_players = sorted(self.hand_players, key=lambda p: p.showdown_value, reverse=True)
            # sort active players according to showdown value

            # If top showdown value is unique, and top player has max bet: Player wins whole pot.
            if self.hand_players[0].showdown_value != self.hand_players[1].showdown_value and self.hand_players[
                0].bet == self.current_bet:
                self.winner_loc = self.players.index(self.hand_players[0])
                self.players[self.winner_loc].chips += self.pot
                self.pot = 0

            else:  # we are in at least two-way split...
                print("We have a split")
                self.split = True
                self.split_winners = []
                # We should find how much each player is playing for, because they might be top score and max bet,
                # but opponents down the line could have a lower bet.
                for player in self.hand_players:
                    # for each player still playing
                    for paying_player in self.hand_players:
                        # go through all players (still playing), (including self)
                        player.playing_for += min(paying_player.bet, player.bet)
                        # find how much player is playing for. It's min of their own bet, and other player bet
                # Now we know how much each player would get if they were top showdown_value
                # But, they will instead receive the minimum of that amount, and how much is remaining in pot,
                # after paying everyone with a higher showdown_value.
                while self.pot > 0:
                    paid_players = []  # find which player(s) have top score (in this round of chip distribution)
                    for player in self.hand_players:
                        # player has top score so is in winners
                        if player.showdown_value == self.hand_players[0].showdown_value:
                            paid_players.append(player)
                            self.split_winners.append(player)  # Save everyone receiving chips in split for GUI

                    if len(paid_players) != 0:
                        pie_of_pot = self.pot / len(paid_players)
                    else:
                        pie_of_pot = 0
                    for player in paid_players:
                        # player gets what they are playing for, or their share of pot, or the remainder of the pot.
                        player.chips += min(player.playing_for, pie_of_pot, self.pot)
                        self.pot -= min(player.playing_for, pie_of_pot, self.pot)
                        if self.pot < 0: print("WARNING:Pot went negative")
                        # player has been paid so remove from playing players.
                        self.hand_players.remove(player)

        self.winners_found = True

        for player in self.players:
            if player.showdown_value>0:
                print(
                    f"{player.name},SH.V:{round(player.starting_hand_value, 2)},ShowDV:{player.showdown_value},Hand-Rank:{categorize_value(player.showdown_value)}")
                print(
                    f"Cards are:{player.best_five[0].combo},{player.best_five[1].combo},{player.best_five[2].combo},{player.best_five[3].combo},{player.best_five[4].combo},")

    def betting_round(self, gui):
        self.check_chip_count()

        self.previous_bet = False  # New round, so first bet is indeed a bet, not a raise.
        self.decide_acting_player()
        print(f'-------------------NEW BETTING ROUND-{self.state}-----------------')
        print(f"Current Bet: {self.current_bet}, Pot:{self.pot}")
        self.actions_remaining = len(self.hand_players)

        while self.actions_remaining > 0:
            self.acting_player.decides(game=self)
            self.acting_player.takes_action(game=self, decision=self.acting_player.decision,
                                            bet_amount=self.acting_player.bet_amount,
                                            raise_amount=self.acting_player.raise_amount)

            # Can show each player action
            if gui is not None:
                gui.render_gui(self)
                time.sleep(gui.delay)

            print(
                f"{self.acting_player.name} {self.acting_player.decision}s: {self.acting_player.bet_amount}/{self.acting_player.raise_amount}.P.Bet : {self.acting_player.bet}"
                f""
                f" C.Bet : {self.current_bet}, Playing for:{self.acting_player.playing_for},ShowDV:{self.acting_player.showdown_value}")
            self.check_chip_count()
            self.update_acting_player()

        self.next_stage()
        self.new_round = False
        self.round_done = True

    def run_main(self, gui):
        self.new_game()
        run = True
        while run:
            gui.render_gui(self)
            # time.sleep(1)
            if self.new_round:
                self.betting_round(gui)
            time.sleep(gui.delay)
            gui.render_gui(self)
            self.clock.tick(60)

            if self.state == "showdown" and not self.winners_found:
                self.decide_winner()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        break
                    if event.key == pygame.K_n:
                        if self.state != "pre_flop":
                            self.new_game()
                        else:
                            print("A new game is already being played")
                    if event.key == pygame.K_p:
                        if self.state != "showdown" and self.state != "not_started":
                            self.new_round = True
                if event.type == pygame.MOUSEBUTTONDOWN:  # if you click, show mouse position, useful for placing
                    print(pygame.mouse.get_pos())

        pygame.quit()

    def update_acting_player(self):
        seat_check = (self.acting_player.seat_number + 1) % self.num_p
        while self.players[seat_check] not in self.hand_players:  # while next player not in game
            seat_check = (seat_check + 1) % self.num_p
        self.acting_player = self.players[seat_check]

    def decide_acting_player(self):
        if self.state == "pre_flop":
            increment = 3
        else:
            increment = 1
        dealer = self.players[self.dealer_loc]
        # If dealer still in game, find his
        # position in active player list, and
        # move forward by correct increment
        # without going out of index.
        if dealer in self.hand_players:
            dealer_index = self.hand_players.index(dealer)
            acting_index = (dealer_index + increment) % (len(self.hand_players))
        else:
            search = (self.dealer_loc + 1) % self.num_p
            while self.players[search] not in self.hand_players:
                search = (search + 1) % self.num_p
            acting_index = self.hand_players.index(self.players[search])

        self.acting_player = self.hand_players[acting_index]
