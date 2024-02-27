import time

from best_cards import *
from data import simulate
from draw_cards import *
from gui import draw_gui


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
        self.value = 0
        self.seat_number = seat_number
        self.bet = 0
        self.best_five = cards

    def decides(self, game, decision=None):
        # TODO# Check validity of each action
        # Can you check?
        # Can you raise?
        # Can you bet?

        # TODO# Use ML for decisions.
        if self.chips == 0:
            pass
        elif self.bet == game.current_bet:
            decision = "check"
        else:
            decision = "call"

        bet_amount = 0
        raise_amount = 0

        if game.pot <= 100:
            if self.seat_number == 4:  # and game.state == "flop"
                decision = "bet"
                bet_amount = game.big_blind_amount
            elif self.seat_number == 5:
                decision = "raise"
                raise_amount = 2 * game.big_blind_amount

        return decision, bet_amount, raise_amount

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
        # TODO# Call when you have less than current bet is all in
        self.chips -= game.current_bet - self.bet
        game.pot += game.current_bet - self.bet
        self.bet = game.current_bet

    def raises(self, game, raise_amount):
        if raise_amount >= game.big_blind_amount and raise_amount >= game.last_bet:
            self.calls(game)
            self.bets(game, raise_amount)
            game.last_bet = raise_amount
        else:
            raise_amount = max(game.last_bet, game.big_blind_amount)
            self.calls(game)
            self.bets(game, raise_amount)
            game.last_bet = raise_amount
        # TODO# Raise without having enough to raise is all in
        # TODO# Raise must be >=big blind, and >= previous bet (DONE, but move to decides)
        # TODO# Check if player has money to raise (probably in decide)

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
        # self.big_blind = []
        # self.small_blind = []
        self.actions_remaining = 0
        self.hand_count = 0
        self.acting_player = None
        self.last_bet = 0

    def deal_cards(self):
        for i in range(0, self.num_p):
            self.players[i].cards = self.cards[5 + i * 2:7 + i * 2]

    def next_dealer_pos(self):
        if self.dealer_loc + 1 < self.num_p:
            self.dealer_loc += 1
        else:
            self.dealer_loc = 0

    def post_blinds(self):
        if self.dealer_loc < self.num_p - 2:
            self.players[self.dealer_loc + 1].bets(self, self.small_blind_amount)
            self.players[self.dealer_loc + 2].raises(self, self.big_blind_amount)
        elif self.dealer_loc < self.num_p - 1:
            self.players[self.dealer_loc + 1].bets(self, self.small_blind_amount)
            self.players[0].raises(self, self.big_blind_amount)
        else:
            self.players[0].bets(self, self.small_blind_amount)
            self.players[1].raises(self, self.big_blind_amount)

    def new_game(self):
        if self.pot != 0:
            for player in self.players:
                print(player.chips, player.bet)
                player.chips += player.bet
                player.bet = 0
            self.pot = 0
        self.hand_count += 1
        self.hand_players = self.players
        self.current_bet = 0
        self.winner_num = -1
        self.state = "pre_flop"
        self.cards = draw_cards(5 + len(self.players) * 2)
        self.deal_cards()
        self.next_dealer_pos()
        self.post_blinds()
        self.update_acting_player()

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
        max_value = 0
        for i in range(0, self.num_p):
            valued_cards = self.players[i].cards + self.cards[0:5]
            self.players[i].best_five, self.players[i].value = best_cards(valued_cards)
            self.players[i].bet = 0
            if self.players[i].value > max_value:
                max_value = self.players[i].value
                self.winner_num = i

        self.players[self.winner_num].chips += self.pot
        self.pot = 0

    def update_game(self):
        # self.next_dealer_pos()
        self.update_bool = False

    def update_acting_player(self):
        # TODO# Hard coding self.players[2] as initial acting player is ok as long as games don't start with empty
        #  seats.
        if self.acting_player is None:
            self.acting_player = self.players[2]

        seat_check = self.acting_player.seat_number
        # print(f"Seat Check is{seat_check} before if")
        if seat_check + 1 < len(self.players):  # if next seat exists
            seat_check += 1  # check next seat (normally)
        else:
            seat_check = 0  # else loop to first seat
        # print(f"Seat Check is{seat_check} after if")
        while self.players[seat_check] not in self.hand_players:  # while next player not in game
            if seat_check + 1 < len(self.players):  # if next seat exists
                seat_check += 1  # check next seat (normally)
            else:
                seat_check = 0  # else loop to first seat

        # print(f"acting player is now{self.acting_player.name}")
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
        # print(self.state)
        print(f'-------------------NEW BETTING ROUND-{self.state}-----------------')
        self.actions_remaining = len(self.hand_players)

        while self.actions_remaining > 0:
            decision, bet_amount, raise_amount = self.acting_player.decides(game=self)
            self.acting_player.takes_action(game=self, decision=decision, bet_amount=bet_amount,
                                            raise_amount=raise_amount)
            # Can show each player action draw_gui(self) time.sleep(2) print(f"{self.acting_player.name},
            # {decision}s,PBet:{self.acting_player.bet}, Pot:{self.pot},CBet={self.current_bet}")

            self.update_acting_player()
        self.round_bool = False

    def run_main(self):

        self.new_game()
        run = True
        while run:
            draw_gui(self)
            # time.sleep(1)
            if self.round_bool:
                self.betting_round()
            draw_gui(self)
            self.clock.tick(60)
            """""""""
            while self.update_bool:
                self.update_game()
            """""""""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        break
                    if event.key == pygame.K_n:
                        self.new_game()
                    if event.key == pygame.K_p:
                        self.decide_acting_player()
                        self.next_stage()
                        if self.state != "showdown":
                            self.round_bool = True
                if event.type == pygame.MOUSEBUTTONDOWN:  # if you click, show mouse position, useful for placing
                    # buttons
                    print(pygame.mouse.get_pos())

        pygame.quit()


if __name__ == '__main__':
    # g = Game(num_p=6)
    # g.run_main()

    # Simulate 5 common cards 1000 times,rank all 1326 starting hands based on ratio of 1326 hands they beat
    df = simulate(n_hands=1000, output_save_loc="Data/hand_rankings_1000.xlsx")
    # df=pd.read_excel("Data/hand_rankings_1000.xlsx")
    pass
