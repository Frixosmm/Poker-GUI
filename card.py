import itertools
import random
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT


class Card:
    def __init__(self):
        self.value = random.randint(2, 14)
        self.suit = random.randint(1, 4)
        self.combo = (self.value, self.suit)
        self.height = CARD_HEIGHT
        self.width = CARD_WIDTH
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
    value = 0.0
    if len(cards) == 5:
        cards_value = [0, 0, 0, 0, 0]
        cards_suit = [0, 0, 0, 0, 0]
        for x in range(0, 5):
            cards_value[x] = cards[x].value
            cards_suit[x] = cards[x].suit

        counts_store = [0] * 13
        for i in range(1, 14):  # from 2 to 14 counts how many of "2" or "3" etc. there are.
            counts_store[i - 1] = cards_value.count(i + 1)
            # We can now find all the pairs, triples, four of a kind and full houses.
            # If there are only "1"'s there are no pairs.
            # If there is 1 "2" there is couple.
            # If there is 1 "3" it's a three of a kind.
            # If there is 1 "4" it's a four of a kind.
            # If there is 1 "2" and 1 "3" there is a full house.
            # If there are 2 "2" and 2 "2" there are two pairs.
        sorted_cards = sorted(cards_value)
        # sorted_cards are in ascending value
        # Minimum value equal to high cards
        """"""""" High Card """""""""
        value = (sorted_cards[-1] * 10 ** 8
                 + sorted_cards[-2] * 10 ** 6
                 + sorted_cards[-3] * 10 ** 4
                 + sorted_cards[-4] * 10 ** 2
                 + sorted_cards[-5] * 10 ** 0)

        # If all cards have different values : (straight,flush,straight flush)
        if counts_store.count(1) == 5:
            straight = False
            flush = False
            if sorted_cards[0] == sorted_cards[1] - 1:
                if sorted_cards[0] == sorted_cards[2] - 2:
                    if sorted_cards[0] == sorted_cards[3] - 3:
                        if sorted_cards[0] == sorted_cards[4] - 4:
                            """"""""" Straight """""""""
                            straight = True
                            value = 5 * 10 ** 10
                            value = value + sorted_cards[4] * 10 ** 8

            if cards_suit[0] == cards_suit[1] == cards_suit[2] == cards_suit[3] == cards_suit[4]:
                """"""""" Flush """""""""
                value = sum([6 * 10 ** 10,
                             (sorted_cards[-1] * 10 ** 8)
                                , (sorted_cards[-2] * 10 ** 6)
                                , (sorted_cards[-3] * 10 ** 4)
                                , (sorted_cards[-4] * 10 ** 2)
                                , (sorted_cards[-5] * 10 ** (0))
                             ])
                flush = True
            if flush and straight:
                """"""""" Straight Flush """""""""
                value = 9 * 10 ** 10
                value += cards[-1].value * 10 ** 8
                if cards_value.count(14) == 1:
                    """"""""" Royal Flush """""""""
                    value = 10 * 10 ** 11
        # All cards don't have different values : (pair,two pair,triplets,quads,full house)
        elif counts_store.count(2) == 1:
            if counts_store.count(3) == 1:
                """"""""" Full-House """""""""
                value = 7 * 10 ** 10
                for i in range(0, 13):
                    if counts_store[i] == 3:
                        value = value + (i + 2) * 10 ** 8
                        # the 3 of a kind is valued higher than the pair
                    elif counts_store[i] == 2:
                        value = value + (i + 2) * 10 ** 6
            else:
                """"""""" One pair """""""""
                value = 2 * 10 ** 10
                c = 3
                for i in range(0, 13):
                    if counts_store[i] == 2:
                        value = value + (i + 2) * 10 ** 8
                    elif counts_store[i] == 1:
                        value = value + (i + 2) * 10 ** (8 - 2 * c)
                        c -= 1
        elif counts_store.count(2) == 2:
            """"""""" Two Pairs """""""""
            value = 3 * 10 ** 10
            lowest_pair = True
            # First pair to find is the lowest pair of the two.
            for i in range(0, 13):
                if counts_store[i] == 2:
                    if lowest_pair:
                        value = value + (i + 2) * 10 ** 6
                        lowest_pair = False
                    else:
                        # high_pair
                        value = value + (i + 2) * 10 ** 8
                elif counts_store[i] == 1:
                    # 5th card
                    value = value + (i + 2) * 10 ** 4
        elif counts_store.count(3) == 1:
            """"""""" Three of a kind """""""""
            value = 4 * 10 ** 10
            low_kicker = True
            for i in range(0, 13):
                if counts_store[i] == 3:
                    # value contribution of 3 of a kind
                    value = value + (i + 2) * 10 ** 8
                elif counts_store[i] == 1:
                    if low_kicker:
                        # value contribution of "low" kicker
                        value = value + (i + 2) * 10 ** 4
                        low_kicker = False
                    else:
                        # value contribution of "high" kicker
                        value = value + (i + 2) * 10 ** 6
        elif counts_store.count(4) == 1:
            """"""""" Four of a kind """""""""
            value = 8 * 10 ** 10
            for i in range(0, 13):
                if counts_store[i] == 4:
                    value = value + (i + 2) * 10 ** 8
                elif counts_store[i] == 1:
                    value = value + (i + 2) * 10 ** 6
    elif len(cards) == 2:
        print("not implemented for 2 cards")
    elif len(cards) == 6:
        print("not implemented for 6 cards")
    elif len(cards) == 7:
        print("not implemented for 7 cards")
    return value


def categorize_value(value):
    if 0 <= value < 2 * 10 ** 10:
        return "High Card"
    elif 2 * 10 ** 10 <= value < 3 * 10 ** 10:
        return "Pair"
    elif 3 * 10 ** 10 <= value < 4 * 10 ** 10:
        return "Two Pair"
    elif 4 * 10 ** 10 <= value < 5 * 10 ** 10:
        return "Three of a Kind"
    elif 5 * 10 ** 10 <= value < 6 * 10 ** 10:
        return "Straight"
    elif 6 * 10 ** 10 <= value < 7 * 10 ** 10:
        return "Flush"
    elif 7 * 10 ** 10 <= value < 8 * 10 ** 10:
        return "Full House"
    elif 8 * 10 ** 10 <= value < 9 * 10 ** 10:
        return "Four of a Kind"
    elif 9 * 10 ** 10 <= value < 10 * 10 ** 10:
        return "Straight Flush"
    elif 10 * 10 ** 10 <= value <= 10 * 10 ** 10:
        return "Royal Flush"
    else:
        return "Invalid value"


def check_uniqueness(vectors):
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):  # Start from i + 1 to avoid self-comparison and redundant checks
            if vectors[i] == vectors[j]:
                return False  # If any duplicate is found, return False
    return True  # If no duplicates are found, return True


def combinations(cards, choose=7):
    return list(itertools.combinations(cards, choose))


def best_cards(cards):
    combos = combinations(cards, 5)
    # when cards=7 this is 7 choose 5, so we can use it to find the hand with the highest value.
    best_value = 0
    best_five = []
    for combo in combos:
        value = value_cards(combo)
        if value > best_value:
            best_value = value
            best_five = combo
    return best_five, best_value
