import random
import pygame
from constants import CARD_WIDTH,CARD_HEIGHT


class Card:
    def __init__(self):
        self.value = random.randint(2, 14)
        self.suit = random.randint(1, 4)
        self.combo = (self.value, self.suit)
        self.height=CARD_HEIGHT
        self.width=CARD_WIDTH
        self.image = self.generate_card_image()

    def generate_card_image(self):
        # Define mappings for special card values
        value_mapping = {11: 'jack', 12: 'queen', 13: 'king', 14: 'ace'}
        suit_mapping = {1: 'hearts', 2: 'spades', 3: 'diamonds', 4: 'clubs'}

        # Map value and suit to their corresponding values
        card_value = value_mapping.get(self.value, str(self.value))
        card_suit = suit_mapping.get(self.suit, str(self.suit))

        # Generate the desired string format
        result_string = f"Cards/{card_value}_of_{card_suit}.png"
        card_image = pygame.transform.scale(pygame.image.load(result_string), (self.width, self.height))

        return card_image

    def make_specific(self, value, suit):
        self.value = value
        self.suit = suit
        self.combo = (self.value, self.suit)
        self.image = self.generate_card_image()


def draw_cards(number):
    drawn_combos = []
    played_cards = []
    while len(drawn_combos) < number:
        new_card = Card()
        if new_card.combo not in drawn_combos:
            drawn_combos.append((new_card.value, new_card.suit))
            played_cards.append(new_card)
    return played_cards


def value_cards(cards):
    value = None
    if len(cards) == 5:
        cards_value = [0, 0, 0, 0, 0]
        cards_suit = [0, 0, 0, 0, 0]
        for x in range(0, 5):
            cards_value[x] = cards[x].value
            cards_suit[x] = cards[x].suit

        counts_store = [0] * 14
        for i in range(1, 15):  # from 2 to 14 counts how many of "2" or "3" etc. there are.
            counts_store[i - 2] = cards_value.count(i)
            # We can now find all the pairs, triples, four of a kind and full houses.
            # If there are only "1"'s there are no pairs.
            # If there is 1 "2" there is couple.
            # If there is 1 "3" it's a three of a kind.
            # If there is 1 "4" it's a four of a kind.
            # If there is 1 "2" and 1 "3" there is a full house.
            # If there are 2 "2" and 2 "2" there are two pairs.
        sorted_cards = sorted(cards_value)
        value = sorted_cards[-1]  # Minimum value equal to high card?

        # IF ALL CARDS HAVE DIFFERENT VALUES(straight,flush,straight flush)
        if counts_store.count(1) == 5:
            straight = False
            flush = False
            if sorted_cards[0] == sorted_cards[1] - 1:
                if sorted_cards[0] == sorted_cards[2] - 2:
                    if sorted_cards[0] == sorted_cards[3] - 3:
                        if sorted_cards[0] == sorted_cards[4] - 4:
                            straight = True
                            value = 40000
                            value = value + sorted_cards[4]
                            # print("straight")
            #TODO# Flush is valued incorrectly when 4 same suit on board and difference is on final player card...
            # Could also have to do with split working incorrectly? Seems like it's the latter.
            if cards_suit[0] == cards_suit[1] == cards_suit[2] == cards_suit[3] == cards_suit[4]:
                value = 50000 + (sorted_cards[-1] * 100) + (sorted_cards[-2] * 1) + (sorted_cards[-3] * 0.01) + (
                        sorted_cards[
                            -4] * 0.0001) + (sorted_cards[-5] * 0.000001)
                flush = True
                # print("flush")
            if flush and straight:
                value = 80000
                # print("straight flush")
                if cards_value.count(14) == 1:
                    value = 100000
                # print("royal flush")
        # MIXED VALUES (all other combos)#
        elif counts_store.count(2) == 1:
            if counts_store.count(3) == 1:
                value = 60000
                for i in range(0, 14):
                    if counts_store[i] == 3:
                        value = value + (i + 2) * 100
                        # the 3 of a kind is valued higher than the pair
                    elif counts_store[i] == 2:
                        value = value + i + 2
                # print("full house")
            else:
                value = 10000
                for i in range(1, 15):
                    if counts_store[i - 1] == 2:
                        value = value + (i - 1) * 100
                    elif counts_store[i - 1] == 1:
                        value = value + i - 1
                # print("one pair")

        elif counts_store.count(2) == 2:
            # print("two_pairs")
            value = 20000
            lowest_pair = True
            # First pair to find is the lowest pair of the two.
            for i in range(0, 14):
                if counts_store[i] == 2:
                    if lowest_pair:
                        value = value + (i + 2)
                        lowest_pair = False
                    else:
                        # high_pair
                        value = value + (i + 2) * 100
                elif counts_store[i] == 1:
                    value = value + (i + 2) * 0.001  # 5th card
        elif counts_store.count(3) == 1:
            value = 30000
            low_kicker = True
            for i in range(0, 14):
                if counts_store[i] == 3:
                    value = value + (i + 2) * 100  # value contribution of 3 of a kind
                elif counts_store[i] == 1:
                    if low_kicker:
                        value = value + (i + 2) * 0.0001  # value contribution of "low" kicker
                        low_kicker = False
                    else:
                        value = value + (i + 2) * 0.01  # value contribution of "high" kicker
        elif counts_store.count(4) == 1:
            value = 70000
            # print("four of a kind")
            for i in range(0, 14):
                if counts_store[i] == 4:
                    value = value + (i + 2) * 100
                elif counts_store[i] == 1:
                    value = value + i + 2
    elif len(cards) == 2:
        print("not implemented for 2 cards")
    elif len(cards) == 6:
        print("not implemented for 6 cards")
    elif len(cards) == 7:
        print("not implemented for 7 cards")
    return value


def categorize_value(value):
    if 0 <= value < 10000:
        return "High Card"
    elif 10000 <= value < 20000:
        return "Pair"
    elif 20000 <= value < 30000:
        return "Two Pair"
    elif 30000 <= value < 40000:
        return "Three of a Kind"
    elif 40000 <= value < 50000:
        return "Straight"
    elif 50000 <= value < 60000:
        return "Flush"
    elif 60000 <= value < 70000:
        return "Full House"
    elif 70000 <= value < 80000:
        return "Four of a Kind"
    elif 80000 <= value < 90000:
        return "Straight Flush"
    elif 90000 <= value < 100000:
        return "Royal Flush"
    else:
        return "Invalid value"


def check_uniqueness(vectors):
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):  # Start from i + 1 to avoid self-comparison and redundant checks
            if vectors[i] == vectors[j]:
                return False  # If any duplicate is found, return False
    return True  # If no duplicates are found, return True


def combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i + 1, r):
            indices[j] = indices[j - 1] + 1
        yield tuple(pool[i] for i in indices)


def best_cards(cards):
    k = combinations(cards,
                     5)  # when cards=7 this is 7 choose 5, so we can use it to find the hand with the highest value.
    best_value = 0
    best_five = cards[0:5]

    for combo in k:
        temp = value_cards(combo)
        if temp > best_value:
            best_value = temp
            best_five = combo

    return best_five, best_value
