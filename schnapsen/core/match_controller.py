"""Card Game Class."""

import logging
import random
from typing import List, Optional

from schnapsen.core.action import Action
from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value
from schnapsen.core.deck import Deck
from schnapsen.core.hand import Hand
from schnapsen.core.marriage import Marriage
from schnapsen.core.player import Player
from schnapsen.core.state import MatchState


class MatchController:
    """Core game controller object."""

    def __init__(self) -> None:
        """Create match controller."""
        self._logger = logging.getLogger()
        self.action_callback = None  # Func set externally for event handling, e.g. in a GUI.

    def get_new_match_state(self, player_1: Player, player_2: Player) -> MatchState:
        """Create a new game state.

        Args:
            player_1 (Player): First player.
            player_2 (Player): Second player.

        Returns:
            MatchState: State object
        """
        state = MatchState(players=(player_1, player_2), deck=Deck())
        # Select player at random for first deal.
        state.player_with_1st_deal = random.choice([player_1, player_2])
        return state

    def reset_round_state(self, state: MatchState, deck: Optional[Deck] = None) -> None:
        """Update/Reset state for a new round.

        Args:
            state (MatchState): State to update
            deck (Optional[Deck], optional): Specify a deck to be used. Set only for testing. Defaults to None.
        """
        # Replenish the deck
        if deck is None:
            state.deck = Deck()
        else:
            state.deck = deck

        # Reset hands/points
        for player_state in state.player_states.values():
            player_state.hand = Hand()
            player_state.cards_won = []
            player_state.round_points = 0

        # Reset round points related state
        state.deck_closed = False
        state.deck_closer = None

        state.round_winner = None
        state.round_winner_match_points = 0
        state.marriages_info = {}
        self._deal(state)
        # if isinstance(state.player_with_1st_deal, MatchController):
        #     pass
        # if isinstance(state.active_player, MatchController):
        #     pass
        state.leading_player = state.player_with_1st_deal
        state.active_player = state.leading_player

    def get_valid_moves(self, state: MatchState) -> List[Action]:
        """Return valid moves for active player.

        Args:
            state (MatchState): Current match state.

        Returns:
            List[Action]: Set of legal/valid actions.
        """
        legal_actions = []
        if state.leading_card is None:
            legal_actions.extend(self._valid_leading_actions(state))
        else:
            legal_actions.extend(self._valid_follower_actions(state))
        return legal_actions

    def _valid_leading_actions(self, state: MatchState) -> List[Action]:
        legal_actions = []
        current_hand = state.player_states[state.active_player].hand

        if current_hand.has_card(Card(state.trump_card.suit, Value.JACK)) and not state.deck_closed:
            legal_actions.append(Action(swap_trump=True))

        if not state.deck_closed:
            legal_actions.append(Action(close_deck=True))

        marriages = current_hand.available_marriages()
        for marriage in marriages:
            legal_actions.append(Action(card=marriage.queen, declare_marriage=True))
            legal_actions.append(Action(card=marriage.king, declare_marriage=True))
        for card in current_hand:
            legal_actions.append(Action(card=card))
        return legal_actions

    def _valid_follower_actions(self, state: MatchState) -> List[Action]:
        legal_actions = []
        further_legal_actions_exist = True
        leading_card = state.leading_card
        current_hand = state.player_states[state.active_player].hand

        # Handle special rules around a closed deck first.
        if state.deck_closed:
            # If deck closed, player must follow suit and win if possible
            for card in current_hand.cards_of_same_suit(suit=leading_card.suit, greater_than=leading_card.value):
                legal_actions.append(Action(card=card))
                further_legal_actions_exist = False

            # Player must follow suit if they can't win
            if further_legal_actions_exist:
                for card in current_hand.cards_of_same_suit(suit=leading_card.suit):
                    legal_actions.append(Action(card=card))
                    further_legal_actions_exist = False

            # Player must trump if they can't follow suit
            if further_legal_actions_exist:
                for card in current_hand.cards_of_same_suit(suit=state.trump_card.suit):
                    legal_actions.append(Action(card=card))
                    further_legal_actions_exist = False

        # Failing the above, player can play any card.
        if further_legal_actions_exist:
            [legal_actions.append(Action(card=card)) for card in current_hand]

        return legal_actions

    def shuffle_imperfect_information(self, state: MatchState, fixed_player: Player) -> None:
        """Update the imperfect information game state.

        In this case, it's the content of the deck and the opponents hand.

        This gets complicated by marriages! There could be one or more halves an unplayed marriages floating around.

        TODO: This is generally inefficient but works. Add testing an simplify!

        Args:
            state (MatchState): Current match state.
            fixed_player (Player): The player for whom we have fixed knowledge.
        """
        other_player = state.get_other_player(fixed_player)
        other_player_state = state.player_states[other_player]

        all_unknown_cards = []
        all_unknown_cards.extend(state.deck)
        all_unknown_cards.extend(other_player_state.hand)

        # Build list of marriage cards in other_player's hand.
        marriage_cards_in_other_players_hand = []
        for marriage_info in state.marriages_info.values():
            # Must use __eq__ here as object reference might be a copy.
            if other_player == marriage_info["player"]:
                marriage = marriage_info["marriage"]
                for card in marriage.cards:
                    if card in other_player_state.hand:
                        marriage_cards_in_other_players_hand.append(card)

        # Marriage cards are not unknowns so remove them from the list.
        [all_unknown_cards.remove(card) for card in marriage_cards_in_other_players_hand]

        # Put the unknown cards back in their respective places.
        random.shuffle(all_unknown_cards)
        nb_deck_cards = len(state.deck)
        state.deck = Deck(all_unknown_cards[:nb_deck_cards])
        # Keep declared marriage cards in hand.
        other_player_state.hand = Hand(all_unknown_cards[nb_deck_cards:] + marriage_cards_in_other_players_hand)

    def update_state_with_action(self, state: MatchState, action: Action) -> None:
        """Update state object with a given action.

        Args:
            state (MatchState): State to act upon.
            action (Action): Action to perform
        """
        player = state.active_player
        is_leader = player is state.leading_player
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.log(logging.DEBUG, 'Action %s, card %s, marriage %s, close deck: %s, swap_trump: %s',
                             player.name, str(action.card is not None), str(action.declare_marriage),
                             str(action.close_deck), str(action.swap_trump))

        play_card = None
        if action.swap_trump:
            self._swap_trump(state)

        if action.close_deck:
            self._close_deck(state)

        if action.declare_marriage:
            self._declare_marriage(state=state, suit=action.card.suit)

        if action.card is not None:
            play_card = state.player_states[player].hand.pop_card(action.card)
            if is_leader:
                state.leading_card = play_card
                state.active_player = state.get_other_player(player)
            else:
                state.following_card = play_card

        # Used for UI event handling
        if self.action_callback is not None:
            self.action_callback(action)

        # Finally handle end of hand
        if not is_leader and state.round_winner is None:
            self._end_of_hand(state)

    @staticmethod
    def play_automated_match(player_1: Player, player_2: Player) -> MatchState:
        """Progress match/game state automatically.

        Args:
            player_1 (Player): First player.
            player_2 (Player): Second player.

        Returns:
            MatchState: Match state including results.
        """
        controller = MatchController()
        state = controller.get_new_match_state(player_1=player_1, player_2=player_2)
        while state.match_winner is None:
            controller.reset_round_state(state=state)
            while state.round_winner is None:
                if isinstance(state.active_player, MatchController):
                    pass
                controller.progress_automated_actions(state)
        return state

    def progress_automated_actions(self, state: MatchState) -> None:
        """Progress automated actions until no more automated actions exist or the game finishes.

        Args:
            state (MatchState): State to update.
        """
        while state.active_player.automated and state.round_winner is None:
            self._logger.log(logging.DEBUG, 'performing next AI action')
            legal_actions = self.get_valid_moves(state=state)
            if len(legal_actions) > 0:
                self.update_state_with_action(state, state.active_player.select_action(state, legal_actions))

    def _end_of_hand(self, state: MatchState) -> None:
        # Determine hand winner. Start by assuming the leader wins then handle cases where this isn't true
        state.hand_winner = state.leading_player
        following_player = state.get_other_player(state.leading_player)
        if state.leading_card.suit == state.following_card.suit:
            if state.following_card.value > state.leading_card.value:
                state.hand_winner = following_player
        else:
            if state.following_card.suit == state.trump_card.suit:
                state.hand_winner = following_player

        loser = state.get_other_player(state.hand_winner)

        # Award points. First figure out if marriage points need handling
        marriage_points = 0
        for marriage_info in state.marriages_info.values():
            marriage_player = marriage_info["player"]
            marriage = marriage_info["marriage"]
            if not marriage.points_awarded and state.hand_winner is marriage_player:
                marriage.points_awarded = True
                marriage_points += marriage.points

        points = state.leading_card.value + state.following_card.value + marriage_points

        # Award points and track cards won by each player
        winning_player_state = state.player_states[state.hand_winner]
        losing_player_state = state.player_states[loser]
        winning_player_state.round_points += points
        winning_player_state.cards_won.extend((state.leading_card, state.following_card))

        self._logger.debug(state.hand_winner.name + ' wins')

        # Deal extra cards, winner first
        if not state.deck_closed:
            self._give_cards(state=state, hand=winning_player_state.hand, number_of_cards=1)
            self._give_cards(state=state, hand=losing_player_state.hand, number_of_cards=1)

        # Reset hand state
        state.leading_card = None
        state.following_card = None
        state.leading_player = state.hand_winner
        state.active_player = state.leading_player

        self._handle_round_win_points_limit_met(state)
        self._handle_round_win_points_limit_not_met(state)
        # Handle match win
        if state.round_winner:
            for player in state.players:
                if state.player_states[player].match_points >= state.match_point_limit:
                    state.match_winner = player

    def _handle_round_win_points_limit_met(self, state: MatchState) -> None:
        # Check for standard round win conditions
        for player in state.players:
            player_state = state.player_states[player]
            other_players_state = state.player_states[state.get_other_player(player)]
            match_points = 0
            if player_state.round_points >= state.round_point_limit:
                state.round_winner = player
                # Award default match points (adjusted when deck was closed)
                if state.deck_closer is not None:
                    match_points = player_state.match_points_on_offer
                else:
                    # Award standard points
                    if other_players_state.round_points == 0:
                        match_points = 3
                    elif other_players_state.round_points < state.round_point_limit / 2:
                        match_points = 2
                    else:
                        match_points = 1
                player_state.match_points += match_points
                state.round_winner_match_points = match_points

                state.player_with_1st_deal = state.get_other_player(state.player_with_1st_deal)

    def _handle_round_win_points_limit_not_met(self, state: MatchState) -> None:
        # Handle case where all cards are played but round point limit has not been reached.
        # Check any player's hand to see if it's empty.
        if len(next(iter(state.player_states.values())).hand) == 0 and (state.round_winner is None):

            if state.deck_closer is None:
                state.round_winner = state.hand_winner
                state.round_winner_match_points = 1
                state.player_states[state.round_winner].match_points += 1
            else:
                # We know closer doesn't have enough points! So award non-closer with the right points
                non_closing_player = state.get_other_player(state.deck_closer)
                non_closing_player_state = state.player_states[non_closing_player]
                state.round_winner = non_closing_player
                match_points = non_closing_player_state.match_points_on_offer
                if state.player_states[state.deck_closer].round_points == 0:
                    match_points = 3

                non_closing_player_state.match_points += match_points
                state.round_winner_match_points = match_points

    def _declare_marriage(self, state: MatchState, suit: Suit) -> None:
        """Update state to declare a marriage.

        Args:
            state (MatchState): Current state.
            suit (Suit): The suit of the marriage to declare.

        Raises:
            ValueError: If illegal action.
        """
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug('Marriage declared by %s for %s', state.active_player.name, suit)
        if state.active_player is not state.leading_player:
            raise ValueError('Invalid marriage - Only leading player can declare marriage')

        marriage = Marriage(Card(suit=suit, value=Value.QUEEN), Card(suit=suit, value=Value.KING))
        marriage.set_points(state.trump_card.suit)

        state.marriages_info[suit] = {
            "marriage": marriage,
            "player": state.active_player
        }

        # Award player points immediately if possible
        active_player_state = state.player_states[state.active_player]
        if active_player_state.round_points != 0:
            active_player_state.round_points += marriage.points
            marriage.points_awarded = True

    def _close_deck(self, state: MatchState) -> None:
        """Updates state to close the deck.

        Args:
            state (MatchState): The current match state.

        Raises:
            ValueError: If action is illegal.
        """
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug('Player closing deck %s', state.active_player)

        if state.deck_closed:
            raise ValueError("Deck already closed")
        if state.active_player is not state.leading_player:
            raise ValueError("non-leading player can't close deck")

        state.deck_closed = True
        state.deck_closer = state.active_player

        active_player_state = state.player_states[state.active_player]
        opponent_state = state.player_states[state.get_other_player(state.active_player)]

        # Default points available
        active_player_state.match_points_on_offer = 1
        # The non-closer gets at least 2 points if he wins
        opponent_state.match_points_on_offer = 2

        if opponent_state.round_points == 0:
            active_player_state.match_points_on_offer = 3
            opponent_state.match_points_on_offer = 3
        elif opponent_state.round_points < 33:
            active_player_state.match_points_on_offer = 2

    def _swap_trump(self, state: MatchState) -> None:
        current_hand = state.player_states[state.active_player].hand

        if state.deck_closed:
            raise ValueError('Trump cannot be swapped as deck is closed')

        jack_of_trumps = Card(suit=state.trump_card.suit, value=Value.JACK)
        if current_hand.has_card(jack_of_trumps):
            current_hand.pop_card(jack_of_trumps)
        else:
            raise ValueError('Player can not swap trump as requisite card not in hand')

        current_hand.append(state.trump_card)
        state.trump_card = jack_of_trumps

    def _deal(self, state: MatchState) -> None:
        # Decide which hand is dealt to first
        second_player = state.get_other_player(state.player_with_1st_deal)
        first_deal_hand = state.player_states[state.player_with_1st_deal].hand
        second_deal_hand = state.player_states[second_player].hand

        self._give_cards(state, first_deal_hand, 3)
        self._give_cards(state, second_deal_hand, 3)
        state.trump_card = state.deck.pop()
        self._give_cards(state, first_deal_hand, 2)
        self._give_cards(state, second_deal_hand, 2)

    def _give_cards(self, state: MatchState, hand: Hand, number_of_cards: int) -> None:
        for _ in range(number_of_cards):
            # Giving out the trump card is a special case when the face down deck is finished
            if len(state.deck) == 0 and number_of_cards == 1:
                state.deck_closed = True
                hand.append(state.trump_card)
            else:
                hand.append(state.deck.pop())
