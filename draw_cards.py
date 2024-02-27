import random
import pygame


CARD_WIDTH = 50
CARD_HEIGHT = 100
class Card:
    def __init__(self):
        self.value = random.randint(2, 14)
        self.suit = random.randint(1, 4)
        self.combo = (self.value, self.suit)
        self.image = generate_card_image(self)

    def make_specific(self,value,suit):
        self.value=value
        self.suit=suit
        self.combo=(self.value,self.suit)
        self.image=(generate_card_image(self))


def generate_card_image(card):
    # Define mappings for special card values
    value_mapping = {11: 'jack', 12: 'queen', 13: 'king', 14: 'ace'}
    suit_mapping = {1: 'hearts', 2: 'spades', 3: 'diamonds', 4: 'clubs'}

    # Map value and suit to their corresponding values
    card_value = value_mapping.get(card.value, str(card.value))
    card_suit = suit_mapping.get(card.suit, str(card.suit))

    # Generate the desired string format
    result_string = f"Cards/{card_value}_of_{card_suit}.png"
    card_image = pygame.transform.scale(pygame.image.load(result_string), (CARD_WIDTH, CARD_HEIGHT))

    return card_image


def draw_cards(number):
    drawn_combos = []
    played_cards = []
    while len(drawn_combos) < number:
        new_card = Card()
        if new_card.combo not in drawn_combos:
            drawn_combos.append((new_card.value, new_card.suit))
            played_cards.append(new_card)
    return played_cards
