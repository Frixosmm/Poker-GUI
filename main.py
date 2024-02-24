import time

from best_cards import *
from draw_cards import *
from value_cards import *
from gui import draw_gui

#TODO# Perhaps it would be more appropriate to create a GUI object instead of holding all gui variables in Game object?
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
        # TODO# Use ML for decisions
        if self.chips == 0:
            pass
        elif self.bet == game.current_bet:
            decision = "check"
        else:
            decision = "call"
        return decision

    def bets(self, game, amount):
        self.chips -= amount
        game.pot += amount
        self.bet += amount
        game.current_bet += amount

    def checks(self):
        pass

    def calls(self, game):
        # TODO# Call when you have less than current bet is all in
        if self.bet < game.current_bet:
            self.chips -= game.current_bet - self.bet
            game.pot += game.current_bet - self.bet
            self.bet = game.current_bet

    def raises(self, game, raise_amount):
        if raise_amount > game.big_blind_amount:
            # calls
            self.chips -= game.current_bet - self.bet
            game.pot += game.current_bet - self.bet
            self.bet = game.current_bet
            # bets raise amount
            self.chips -= raise_amount
            game.pot += raise_amount
            self.bet += raise_amount
            game.current_bet += raise_amount
            # self.calls(self,game)
            # self.bets(self,game,raise_amount)

        # TODO# Raise without having enough to raise is all in
        # TODO# Raise has to be at least one big blind, and at least as much as the previous bet

    def folds(self, game):
        self.bet = 0
        game.hand_players.remove(self)
        self.cards = None

    def all_ins(self, game):
        game.pot += self.chips
        self.bet += self.chips
        self.chips = 0
        game.current_bet += self.bet

    def takes_action(self, game, decision, bet_amount=None, raise_amount=None):
        if decision == "check":
            self.checks()
        elif decision == "fold":
            self.folds(game)
        elif decision == 'call':
            self.calls(game)
        elif decision == 'raise':
            self.raises(game, raise_amount=raise_amount)
        elif decision == "bet":
            self.bets(game, amount=bet_amount)
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
            self.players[self.dealer_loc + 2].bets(self, self.big_blind_amount)
            # self.dealer_loc += 1
        elif self.dealer_loc < self.num_p - 1:
            self.players[self.dealer_loc + 1].bets(self, self.small_blind_amount)
            self.players[0].bets(self, self.big_blind_amount)
            # self.dealer_loc += 1
        else:
            self.players[0].bets(self, self.small_blind_amount)
            self.players[1].bets(self, self.big_blind_amount)
            # self.dealer_loc = 0

    def new_game(self):
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
        # self.update_bool = True
        self.update_acting_player()
        # print("---------------------NEW GAME--------------------")

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
        # TODO# Hard coding self.players[2] as the initial acting player should be ok as long as games don't start with empty seats.
        if self.acting_player is None:
            self.acting_player = self.players[
                2]  # set big blind as initial acting player, because it will be updated to next one over
            # print(f"acting player is now{self.acting_player.name}")

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

    def betting_round(self):

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
        # print('-------------------NEW BETTING ROUND------------------')
        self.actions_remaining = len(self.hand_players)
        while self.actions_remaining > 0:
            decision = self.acting_player.decides(game=self)
            self.acting_player.takes_action(game=self, decision=decision)
            # print(
            #    f"{self.acting_player.name}, {decision}s,PBet:{self.acting_player.bet}, Pot:{self.pot},CBet={self.current_bet}")
            self.update_acting_player()
        self.round_bool = False

    def run_main(self):
        run = True
        self.new_game()

        while run:
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
                        self.next_stage()

                        if self.state != "showdown":
                            self.round_bool = True
                if event.type == pygame.MOUSEBUTTONDOWN:  # if click, show mouse position, useful for placing buttons
                    print(pygame.mouse.get_pos())
            if self.round_bool:
                self.betting_round()

        pygame.quit()


if __name__ == '__main__':
    g = Game(num_p=6)
    # g.new_game()
    # g.betting_round()
    g.run_main()
