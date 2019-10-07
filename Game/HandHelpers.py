class HandHelpers:

    # Returns the suits of available marriages and a boolean
    # ToDo: There's probably a sexy pythonic way to do this with comprehension/filters/maps
    @staticmethod
    def available_marriages(hand):

        # Keep track of a running count of matches for each suit
        dic = {0: 0, 1: 0, 2: 0, 3: 0}

        for card in hand:
            if card.value == 3 or card.value == 4:
                dic[card.suit] += 1

        # Any dic item with a count of 2 is marriage
        result = []
        for suit, count in dic.items():
            if count == 2:
                result.append(suit)

        return len(result) > 0, result
