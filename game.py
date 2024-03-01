import time

import pygame

from card import draw_cards, best_cards
from player import Player


class Game:
    def __init__(self, num_p=6, bb=10, start_funds=1000):
        self.num_p = num_p
        self.clock = pygame.time.Clock()
        self.start_time = time.time()  # TODO# Start time of application != start time of game ?
        self.state = "not_started"
        self.cards = draw_cards(5 + num_p * 2)
        self.players = []
        self.hand_players = []
        self.pot = 0
        self.big_blind_amount = bb
        self.small_blind_amount = bb / 2
        self.current_bet = 0
        self.current_player = 0
        self.start_funds = start_funds
        self.winner_num = -1
        for i in range(0, self.num_p):
            self.players.append(Player("Player" + str(i + 1), self.start_funds, [], i))
            # self.cards[5 + i * 2:7 + i * 2]
        self.common_cards_show = 0
        self.dealer_loc = -1
        self.round_bool = None
        self.update_bool = True
        self.actions_remaining = 0
        self.hand_count = 0
        self.acting_player = None
        self.previous_bet = 0
        self.round_done = False

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
        if self.dealer_loc + 1 < self.num_p:
            self.dealer_loc += 1
        else:
            self.dealer_loc = 0

    def post_blinds(self):
        if self.dealer_loc < self.num_p - 2:
            self.players[self.dealer_loc + 1].bets(self, self.small_blind_amount)
            self.players[self.dealer_loc + 2].bets(self, self.big_blind_amount)
        elif self.dealer_loc < self.num_p - 1:
            self.players[self.dealer_loc + 1].bets(self, self.small_blind_amount)
            self.players[0].bets(self, self.big_blind_amount)
        else:
            self.players[0].bets(self, self.small_blind_amount)
            self.players[1].bets(self, self.big_blind_amount)

    def new_game(self):
        if self.pot != 0:
            for player in self.hand_players:
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
        self.cards = draw_cards(5 + len(self.players) * 2)
        self.deal_cards()
        for player in self.hand_players:
            player.value_starting_hand()
        self.next_dealer_pos()
        self.update_acting_player()
        self.post_blinds()

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
        # highest_showdown_value = -1
        # winners = []
        for player in self.players:  # Assign all players their best cards and the showdown value of these cards
            if player in self.hand_players:  # Player participating in showdown
                valued_cards = player.cards + self.cards[0:5]
                player.best_five, player.showdown_value = best_cards(valued_cards)
            else:  # player is not playing so no cards and negative value for redundancy
                player.best_five, player.showdown_value = [], -1
        # Sort according to showdown value, with
        self.hand_players = sorted(self.hand_players, key=lambda p: p.showdown_value, reverse=True)
        # Players participating in showdown are sorted in descending showdown value
        self.winner_num = self.hand_players[0].seat_number

        # highest_showdown_value=self.hand_players[0].showdown_value
        # TODO# Test split functionality
        for player in self.hand_players:
            # for each player still playing
            for paying_player in self.hand_players:
                # go through OTHER players
                if player != paying_player:
                    player.playing_for += min(paying_player.bet, player.bet)
                    # find how much player is playing for. It's min of their own bet, and other player bet

        while self.pot > 0:
            paid_players = []  # find which player(s) have top score
            for player in self.hand_players:
                # player has top score so is in winners
                if player.showdown_value == self.hand_players[0].showdown_value:
                    paid_players.append(player)

            # (Current) Top score players have been found.
            # Loop through them and give them min (their fraction of the pot, what they are playing for)
            for player in paid_players:
                # player gets what they are playing for, or their share of pot
                player.chips += min(player.playing_for, self.pot / len(paid_players))
                # remove same amount from pot
                self.pot -= min(player.playing_for, self.pot / len(paid_players))
                # player has been paid so remove.
                paid_players.remove(player)

        for player in self.players:
            player.bet = 0

    def update_game(self):
        # self.next_dealer_pos()
        self.update_bool = False

    def update_acting_player(self):
        # TODO# Hard coding self.players[2] as initial acting player is ok as long as games don't start with empty
        #  seats.
        if self.acting_player is None:
            self.acting_player = self.players[2]
        seat_check = self.acting_player.seat_number
        if seat_check + 1 < len(self.players):  # if next seat exists
            seat_check += 1  # check next seat (normally)
        else:
            seat_check = 0  # else loop to first seat

        while self.players[seat_check] not in self.hand_players:  # while next player not in game
            if seat_check + 1 < len(self.players):  # if next seat exists
                seat_check += 1  # check next seat (normally)
            else:
                seat_check = 0  # else loop to first seat

        self.acting_player = self.players[seat_check]

    def decide_acting_player(self):
        if self.state == "pre_flop":
            increment = 3
        else:
            increment = 1

        if self.dealer_loc + increment < self.num_p:
            seat_check = self.dealer_loc + increment
        else:
            seat_check = self.dealer_loc + increment - self.num_p - 1
        while self.players[seat_check] not in self.hand_players:
            if seat_check + 1 <= self.num_p:
                seat_check += 1
            else:
                seat_check = 0

        self.acting_player = self.players[seat_check]

    def betting_round(self, gui):
        self.decide_acting_player()
        print(f'-------------------NEW BETTING ROUND-{self.state}-----------------')
        self.actions_remaining = len(self.hand_players)

        while self.actions_remaining > 0:
            self.acting_player.decides(game=self)
            self.acting_player.takes_action(game=self, decision=self.acting_player.decision,
                                            bet_amount=self.acting_player.bet_amount,
                                            raise_amount=self.acting_player.raise_amount)
            # Can show each player action
            gui.render_gui(self)
            # time.sleep(0.5)
            print(
                f"{self.acting_player.name},{self.acting_player.decision}s,C.Bet={self.current_bet},P.Bet:{self.acting_player.bet}, Pot:{self.pot},SHand Value:{round(self.acting_player.starting_hand_value, 2)} Playing for:{self.acting_player.playing_for},5Value:{self.acting_player.showdown_value}")

            self.update_acting_player()

        self.next_stage()
        self.round_bool = False
        self.round_done = True

    def run_main(self, gui):
        self.new_game()
        run = True
        while run:
            gui.render_gui(self)
            # time.sleep(1)
            if self.round_bool:
                self.betting_round(gui)
            time.sleep(gui.delay)
            gui.render_gui(self)
            self.clock.tick(60)

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
                            self.round_bool = True
                if event.type == pygame.MOUSEBUTTONDOWN:  # if you click, show mouse position, useful for placing
                    # buttons
                    print(pygame.mouse.get_pos())

        pygame.quit()
