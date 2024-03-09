import pandas as pd


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
        if (player in game.hand_players) and player.chips > 0 and len(game.hand_players) > 1 and (
                sum(1 for p in game.hand_players if p.chips != 0) != 1):
            # If player in game, and player has chips, and opponents exist, and opponents have chips to bet

            # Move to check validity of player decision
            # First check if raise should become bet, or bet should become raise.
            if player.decision == "bet" and game.previous_bet == True:
                # bet becomes raise
                # print("Bet becomes raise.")
                player.decision = "raise"
                player.raise_amount = player.bet_amount
                player.bet_amount = 0
                player.valid_choice = False
            elif player.decision == "raise" and game.previous_bet == False:
                # raise becomes bet
                # print("Raise becomes bet.")
                player.decision = "bet"
                player.bet_amount = player.raise_amount
                player.raise_amount = 0
                player.valid_choice = False

            # Now check for validity
            if player.decision is None or player.decision == "fold":
                player.valid_choice = True  # folding or doing nothing is always valid.
                # Doing nothing should only happen when player is out.
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
                    # TODO # When player wants to call but doesn't have enough, he goes all-in. In this case,
                    #  his chips go negative...

                    print(
                        "Player chose call, but doesn't have enough chips to cover current bet.")  # p.chips > 0 = True
                    player.decision = "all-in"
                    print("Player goes all-in instead.")
                    player.valid_choice = False
                else:  # Can call, valid choice
                    player.valid_choice = True

            elif player.decision == "bet":
                # Adjust player bet to minimum
                if player.bet_amount >= game.big_blind_amount:
                    pass
                else:
                    player.bet_amount = game.big_blind_amount
                    player.valid_choice = False
                    print("Player tried to bet an amount smaller than the minimum allowed, so his bet was adjusted")
                    # Bet is adjusted to minimum bet. If player doesn't have minimum bet and still chooses bet?What then?
                    # Then will trigger else, bet is 0 and player goes all in.

                if player.chips >= game.current_bet - player.bet + player.bet_amount:  # Has enough to call AND bet
                    player.valid_choice = True
                elif player.chips >= game.current_bet - player.bet:  # Has enough to call only
                    player.decision = "call"
                    print("Player tried to bet, but didn't have enough. Player calls instead.")
                    player.valid_choice = False
                else:  # Chips>0 from beginning
                    player.bet_amount = 0
                    player.decision = "all-in"

                    print("Player tried to bet, but didn't even have enough to call. Player goes all-in instead")
                    player.valid_choice = False

            elif player.decision == "raise":
                if player.chips >= game.current_bet - player.bet + player.raise_amount:  # Has enough to call AND raise
                    if player.raise_amount >= game.big_blind_amount and player.raise_amount >= game.previous_bet_amount:  # Raise amount is valid
                        player.valid_choice = True

                    else:  # Raise amount is invalid but player has enough to raise the minimum
                        print("Raise amount was invalid.")
                        print("Raise amount adjusted to minimum raise amount.")
                        player.raise_amount = min(game.big_blind_amount, game.previous_bet_amount)
                        player.valid_choice = False

                elif player.chips > game.current_bet - player.bet:  # Has enough to call but not raise
                    print(F"{player.name} doesn't have enough to raise, they call instead.")
                    player.decision = "call"
                    player.valid_choice = False
                else:  # Has chips>0 but cant raise or call
                    player.decision = "all-in"
                    player.valid_choice = False
            # Since player in game, has opponents and has chips, all-in is always valid.
            elif player.decision == "all-in":
                player.valid_choice = True
            else:
                print("Player decision not recognised")
                player.valid_choice = False
        else:  # If no opponents exist or player not in game, or player is in game but has 0 chips, player waits
            player.decision = "Wait"
            self.valid_choice = True

    def decides(self, game):
        self.decision = None
        self.bet_amount = 0
        self.raise_amount = 0

        if self.starting_hand_value < 0.1 and self.bet < game.current_bet and len(game.hand_players) != 1:
            self.decision = "fold"
        elif self.starting_hand_value < 0.5:
            if self.bet == game.current_bet:
                self.decision = "check"
            else:
                self.decision = "call"
        elif self.starting_hand_value < 0.8:
            if game.pot <=50:
                self.decision = "bet"
                self.bet_amount = max(game.big_blind_amount, game.pot * 0.5)
                # self.bet_amount = game.big_blind_amount * 0.5
            elif self.bet == game.current_bet:
                self.decision = "check"
            elif (game.current_bet - self.bet) / (game.pot / len(
                    game.hand_players)) < 1:  # If amount needed to call is less than pot/num players in game.
                self.decision = "call"
            else:
                self.decision = "fold"
        elif self.starting_hand_value >= 0.8 and self.chips > 0:
            self.decision = "all-in"
        else:
            pass
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
        # Bet and all-in *decisions* have potential to make next player decision and action a raise.
        # Call also uses bet *action*, but decision will be "call" so next player action isn't a raise.
        if self.decision == "bet":
            game.previous_bet = True
            game.previous_bet_amount = bet_amount
        elif self.decision == "all-in" and self.bet > game.current_bet:
            # If bet action is result of all-in and if all in increased current bet, next action is raise not bet.
            game.previous_bet = True
            temp = game.previous_bet_amount
            game.previous_bet_amount = max(bet_amount, temp)
        elif self.decision == "raise":
            game.previous_bet = True
            game.previous_bet_amount = self.raise_amount
    def calls(self, game):
        self.chips -= game.current_bet - self.bet
        game.pot += game.current_bet - self.bet
        self.bet = game.current_bet

    def raises(self, game, raise_amount):
        self.calls(game)
        self.bets(game, raise_amount)
        game.previous_bet_amount = raise_amount

    def folds(self, game):
        self.bet = 0
        game.hand_players.remove(self)
        self.cards = None

    def all_ins(self, game):

        # TODO #game.current_bet += bet_amount
        self.bet += self.chips
        game.pot += self.chips
        previous_current_bet = game.current_bet
        game.current_bet = max(previous_current_bet, self.bet)
        self.chips = 0
        # If all in resulted in increased current bet, other players act
        if game.current_bet != previous_current_bet:
            game.actions_remaining = len(game.hand_players)

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
