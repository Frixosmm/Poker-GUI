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

            if cards_suit[0] == cards_suit[1] == cards_suit[2] == cards_suit[3] == cards_suit[4]:
                # TODO# Resulting Value for flushes will differentiate between flushes using very
                #  small numbers. Take care not to cause bugs with this. (DONE)
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
                for i in range(1, 15):
                    if counts_store[i - 1] == 3:
                        value = value + (i - 1) * 100
                        # the 3 of a kind is valued higher than the pair
                    elif counts_store[i - 1] == 2:
                        value = value + i - 1
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
            for i in range(1, 15):
                if counts_store[i - 1] == 2:
                    if lowest_pair:
                        value = value + (i - 1)
                        lowest_pair = False
                    else:
                        # high_pair
                        value = value + (i - 1) * 100
                elif counts_store[i - 1] == 1:
                    value = value + (i - 1) * 0.001
        elif counts_store.count(3) == 1:
            value = 30000
            low_kicker = True
            # print("three of a kind")
            for i in range(1, 15):
                if counts_store[i - 1] == 3:
                    if low_kicker:
                        value = value + (i - 1)
                        low_kicker = False
                    value = value + (i - 1) * 100
                elif counts_store[i - 1] == 1:
                    value = value + (i - 1) * 0.001

        elif counts_store.count(4) == 1:
            value = 70000
            # print("four of a kind")
            for i in range(1, 15):
                if counts_store[i - 1] == 4:
                    value = value + (i - 1) * 100
                elif counts_store[i - 1] == 1:
                    value = value + i - 1
    elif len(cards) == 2:
        print("not implemented for 2 cards")
    elif len(cards) == 6:
        print("not implemented for 6 cards")
    elif len(cards) == 7:
        print("not implemented for 7 cards")
    return value


def categorize_value(value):
    if 0 <= value <= 10000:
        return "High Card"
    elif 10001 <= value <= 20000:
        return "Pair"
    elif 20001 <= value <= 30000:
        return "Two Pair"
    elif 30001 <= value <= 40000:
        return "Three of a Kind"
    elif 40001 <= value <= 50000:
        return "Straight"
    elif 50001 <= value <= 60000:
        return "Flush"
    elif 60001 <= value <= 70000:
        return "Full House"
    elif 70001 <= value <= 80000:
        return "Four of a Kind"
    elif 80001 <= value <= 90000:
        return "Straight Flush"
    elif 90001 <= value <= 100000:
        return "Royal Flush"
    else:
        return "Invalid value"


def check_uniqueness(vectors):
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):  # Start from i + 1 to avoid self-comparison and redundant checks
            if vectors[i] == vectors[j]:
                return False  # If any duplicate is found, return False
    return True  # If no duplicates are found, return True
