import time

import pandas as pd

from best_cards import *
from data import simulate
from draw_cards import *
from gui import render_gui


# TODO# When gui is imported, a black screen is temporarily displayed. Fix this...

# TODO#Sounds for call,check,fold,raise
# TODO#(Human) Player buttons
# TODO#(Human) Player cards shown
# TODO# Cards moving animation
# TODO# Better table background, higher resolution
# TODO# Adjust seat positions for 1920/1080.

# TODO# Perhaps it would be more appropriate to create a GUI object instead of holding all gui variables in Game object?
class Player:

    def __init__(self, name, chips, cards, seat_number):
        self.name = name
        self.chips = chips
        self.turn = 0
        self.cards = cards
        self.showdown_value = 0
        self.starting_hand_value = 0
        self.seat_number = seat_number
        self.bet = 0
        self.best_five = cards
        self.decision = None
        self.raise_amount = 0
        self.bet_amount = 0
        self.valid_choice = None
        self.playing_for = 0

    def value_starting_hand(self, data_loc="Data/hand_rankings_100.xlsx"):
        df = pd.read_excel(data_loc)
        search = [self.cards[0].value, self.cards[0].suit, self.cards[1].value, self.cards[1].suit]
        mask = df.apply(lambda row: all(row.iloc[i] == search[i] for i in range(len(search))), axis=1)
        result = df[mask]
        # print(f"Length result is"{len(result)})
        # print(len(result.iloc[0]))
        if result.empty:
            print(f"The valuing function failed, while searching for:{search}")
            print(f"Result was:")
            # print(result)
            self.starting_hand_value = 0
        else:
            self.starting_hand_value = result.iloc[0, 4]

    def check_valid_choice(self, game):
        player = self
        if player.chips > 0 and len(game.hand_players) > 1 and (player in game.hand_players):
            # If opponents exist and player is still in the game and has chips
            # Move to check validity of player decision
            if player.decision is None or player.decision == "fold":
                player.valid_choice = True  # folding or doing nothing is always valid
            elif player.decision == "check":
                if player.bet != game.current_bet:  # Can't check if you need to put money in pot
                    print("Can't check, so you fold instead")
                    # print("Must chose fold or call.")
                    player.decision = "fold"

                    player.valid_choice = False
                else:
                    player.valid_choice = True

            elif player.decision == "call":
                if player.chips < game.current_bet - player.bet:  # Can't call, not enough chips
                    print(
                        "Player chose call, but doesn't have enough chips to cover current bet.")  # p.chips > 0 = True
                    player.decision = "all-in"
                    print("Player goes all-in instead.")
                    player.valid_choice = False
                else:  # Can call, valid choice
                    player.valid_choice = True

            elif player.decision == "bet":
                if player.chips >= game.current_bet - player.bet + player.bet_amount:  # Has enough to call AND bet
                    player.valid_choice = True
                elif player.chips >= game.current_bet - player.bet:  # Has enough to call only
                    player.decision = "call"
                    print("Player tried to bet, but didn't have enough. Player calls instead.")
                    player.valid_choice = False
                else:  # Chips>0 from beginning
                    player.decision = "all-in"
                    print("Player tried to bet, but didn't even have enough to call. Player goes all-in instead")
                    player.valid_choice = False

            elif player.decision == "raise":  # TODO# It is only a raise if someone has previously bet
                if player.chips >= game.current_bet - player.bet + player.raise_amount:  # Has enough to call AND raise
                    if player.raise_amount >= game.big_blind_amount and player.raise_amount >= game.previous_bet:  # Raise amount is player.valid
                        player.valid_choice = True

                    else:  # Raise amount is invalid but player has enough to raise the minimum
                        print("Raise amount was invalid.")
                        print("Raise amount adjusted to minimum raise amount.")
                        player.raise_amount = min(game.big_blind_amount, game.previous_bet)
                        player.valid_choice = False

                elif player.chips > game.current_bet - player.bet:  # Has enough to call but not raise
                    print(F"{player.name} doesn't have enough to raise, they call instead.")
                    player.decision = "call"
                    player.valid_choice = False
                else:  # Has chips>0 but cant raise or call
                    player.decision = "all-in"
                    player.valid_choice = False
            elif player.decision == "all-in":  # Since player in game, has opponents and has chips, all-in is always valid.
                player.valid_choice = True
            else:
                print("Player decision not recognised")
                player.valid_choice = False
        else:  # If no opponents exist or player not in game, or player is in game but has 0 chips, player does nothing
            player.decision = None

        return

    def decides(self, game):
        self.decision = None
        self.bet_amount = 0
        self.raise_amount = 0

        if self.starting_hand_value < 0.55 and self.bet < game.current_bet and len(game.hand_players) != 1:
            self.decision = "fold"
        elif self.starting_hand_value < 0.7:
            if self.bet == game.current_bet:
                self.decision = "check"
            else:
                self.decision = "call"
        elif self.starting_hand_value >= 0.7:
            if game.pot <= 100:
                self.decision = "bet"
                self.bet_amount = game.big_blind_amount
            else:
                self.decision = "check"

        self.check_valid_choice(game)
        if self.valid_choice:
            pass
        else:
            print("Invalid Choice was entered")  # TODO# If invalid choice is made, should ask player for another choice
        if self.decision is None:
            print("Choice is none")

    def checks(self):
        pass

    def bets(self, game, bet_amount):
        self.calls(game)
        game.pot += bet_amount
        game.current_bet += bet_amount
        self.bet = game.current_bet
        self.chips -= bet_amount
        game.actions_remaining = len(game.hand_players)

    def calls(self, game):
        self.chips -= game.current_bet - self.bet
        game.pot += game.current_bet - self.bet
        self.bet = game.current_bet

    def raises(self, game, raise_amount):
        self.calls(game)
        self.bets(game, raise_amount)
        game.previous_bet = raise_amount

    def folds(self, game):
        self.bet = 0
        game.hand_players.remove(self)
        self.cards = None

    def all_ins(self, game):
        game.pot += self.chips
        self.bet += self.chips
        self.chips = 0
        game.current_bet += self.bet

    def takes_action(self, game, decision, bet_amount=0, raise_amount=0):
        if decision == "check":
            self.checks()
        elif decision == "fold":
            self.folds(game)
        elif decision == 'call':
            self.calls(game)
        elif decision == 'raise':
            self.raises(game, raise_amount=raise_amount)
        elif decision == "bet":
            self.bets(game, bet_amount=bet_amount)
        elif decision == 'all-in':
            self.all_ins(game)
        elif decision == 'none':
            pass
        game.actions_remaining -= 1


class Game:
    def __init__(self, num_p=6, bb=10, start_funds=1000):

        self.width = 1920 / 2
        self.height = 1080 / 2
        self.gui = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Texas Holdem")
        pygame.font.init()
        self.font = pygame.font.SysFont('comicsans', 30)
        self.background = pygame.transform.scale(pygame.image.load('Images/poker_table.jpeg'),
                                                 (self.width, self.height))
        self.seat_positions = [(self.width / 2, self.height / 8),
                               (7 * self.width / 8, self.height / 8),
                               (7 * self.width / 8, 2 * self.height / 2.7),
                               (self.width / 2, 2 * self.height / 2.7),
                               (self.width / 8, 2 * self.height / 2.7),
                               (self.width / 8, self.height / 8)]
        self.joker = pygame.transform.scale(pygame.image.load("Cards/red_joker.png"), (CARD_WIDTH, CARD_HEIGHT))
        self.num_p = num_p
        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        #################
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
        highest_showdown_value = -1
        winners = []
        for player in self.players:  # Assign all players their best cards and the showdown value of these cards
            if player in self.hand_players:  # Player participating in showdown
                valued_cards = player.cards + self.cards[0:5]
                player.best_five, player.showdown_value = best_cards(valued_cards)
            else:  # player is not playing so no cards and negative value for redundancy
                player.best_five, player.showdown_value = [], -1
        # Sort according to showdown value, with
        self.hand_players = sorted(self.hand_players, key=lambda p: p.showdown_value, reverse=True)
        # Players participating in showdown are sorted in descending showdown value
        # highest_showdown_value=self.hand_players[0].showdown_value

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
                self.players.remove(player)

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

    def betting_round(self):
        self.decide_acting_player()
        print(f'-------------------NEW BETTING ROUND-{self.state}-----------------')
        self.actions_remaining = len(self.hand_players)

        while self.actions_remaining > 0:
            self.acting_player.decides(game=self)
            self.acting_player.takes_action(game=self, decision=self.acting_player.decision,
                                            bet_amount=self.acting_player.bet_amount,
                                            raise_amount=self.acting_player.raise_amount)
            # Can show each player action
            render_gui(self)
            time.sleep(0.5)
            print(
                f"{self.acting_player.name},{self.acting_player.decision}s,C.Bet={self.current_bet},P.Bet:{self.acting_player.bet}, Pot:{self.pot},SHand Value:{round(self.acting_player.starting_hand_value, 2)}")

            self.update_acting_player()

        self.next_stage()
        self.round_bool = False
        self.round_done = True

    def run_main(self):

        self.new_game()
        run = True
        while run:
            render_gui(self)
            # time.sleep(1)
            if self.round_bool:
                self.betting_round()
            time.sleep(1)
            render_gui(self)
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


if __name__ == '__main__':
    g = Game(num_p=6)
    # g.new_game()
    g.run_main()

    # Simulate 5 common cards 1000 times,rank all 1326 starting hands based on ratio of 1326 hands they beat
    # df = simulate(n_hands=10, output_save_loc="Data/hand_rankings_100.xlsx")
    # df = pd.read_excel("Data/hand_rankings_1000.xlsx")
