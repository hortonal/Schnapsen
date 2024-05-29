"""Monte Carlo Trial."""
from __future__ import annotations

from dataclasses import dataclass
import math
from random import choice
from typing import List

import numpy as np

from schnapsen.ai.better_player import BetterPlayer
from schnapsen.core.action import Action
from schnapsen.core.actions import ALL_GAME_ACTIONS
from schnapsen.core.actions import get_action_index
from schnapsen.core.match_controller import MatchController
from schnapsen.core.match_helpers import play_automated_matches
from schnapsen.core.player import Player
from schnapsen.core.state import MatchState


@dataclass
class Node:
    """A node in a monte carlo tree search."""
    match_controller: MatchController
    state: MatchState
    root_player: Player
    parent: Node = None
    action_id: int = None
    children: List[Node] = None
    expandable_moves: List[Action] = None
    visit_count: int = 0
    value_sum: float = 0
    c: float = math.sqrt(2)

    def __post_init__(self) -> None:
        """Initialise node state."""
        self.expandable_moves = self.match_controller.get_valid_actions(state=self.state)
        self.children = []

    def is_fully_expanded(self) -> bool:
        """Check if node has been fully expanded.

        Returns:
            bool: True if terminal state, otherwise False.
        """
        return len(self.expandable_moves) == 0 and len(self.children) > 0

    def select(self) -> Node:
        """Decide the next child node to explore.

        Returns:
            Node: Selected node.
        """
        best_child = None
        best_ucb = -np.inf
        for child in self.children:
            ucb = self.get_ucb(child)
            if ucb > best_ucb:
                best_child = child
                best_ucb = ucb

        return best_child

    def get_ucb(self, child: Node) -> float:
        """Determine the "UCB" score.

        The purpose of this is to help us traverse our node tree by best outcomes first but with a bias towards
        unexplored paths.

        Args:
            child (Node): The node to calculate UCB score for.

        Returns:
            float: The calculated ucb score.
        """
        q_value = ((child.value_sum / child.visit_count) + 1) / 2
        # If the child node represents an opponent's move, the q_value is "opposite" of what it is for us
        # e.g. a perfect match position for us is q_value 1. An opponents q_value is 1, this is bad for us
        # We want to put the child in the worst possible state.
        # If the child node is the result of swapping a trump (for example) then the q_value does not need adjusting.
        if child.state.active_player != self.state.active_player:
            q_value = 1 - q_value
        return q_value + self.c * math.sqrt(math.log(self.visit_count) / child.visit_count)

    def expand(self) -> Node:
        """Expand node at random, updating children state and returning new expansion.

        Returns:
            Node: Newly added child.
        """
        # Sample a child action/state at random
        action_ix = choice(range(len(self.expandable_moves)))
        # Remove and select random action possible moves
        action = self.expandable_moves.pop(action_ix)

        # Set up a child state. We setup the game state assuming
        child_state = self.state.copy()
        self.match_controller.perform_action(child_state, action)
        # Note that we don't use the match controller to progress game states as we now want random exploration!
        child = Node(match_controller=self.match_controller,
                     state=child_state, root_player=self.root_player, parent=self,
                     action_id=get_action_index(action))
        self.children.append(child)
        return child

    def simulate(self) -> float:
        """Simulate value of node path.

        Returns:
            float: A value score for path.
        """
        rollout_state = self.state.copy()
        current_player = self.state.active_player
        # Update the imperfect knowledge in the state.
        # Without doing this, we end up exploring states with the knowledge of what's to come which is a naughty
        # abuse of game state access!
        self.match_controller.shuffle_imperfect_information(rollout_state, self.root_player)

        # Progress the game at random until it ends!
        while True:
            # Pick random move
            action = choice(self.match_controller.get_valid_actions(rollout_state))
            # Update game state
            self.match_controller.perform_action(rollout_state, action)
            # Stop if/when we have a winner
            value, is_terminal = rollout_state.normalised_value_is_terminal()
            if is_terminal:
                # Adjust value if the "winner" is not the player at the start of the simulation.
                if rollout_state.round_winner != current_player:
                    value *= -1
                return value

    def back_propagate(self, value: int) -> None:
        """Update parent node based on child visit.

        Args:
            value (int): Node value to back-propagate.
        """
        self.value_sum += value
        self.visit_count += 1

        if self.parent is not None:
            if self.parent.state.active_player != self.state.active_player:
                value *= -1
            self.parent.back_propagate(value)


@dataclass
class MCTS:
    """Monte Carlo Tress Search Implementation."""

    match_controller: MatchController

    def search(self, state: MatchState, number_of_searches: int) -> List[float]:
        """Explore problem space with Monte Carlo Tree Search.

        Args:
            state (MatchState): Current match state.
            number_of_searches (int): How many searches to perform.

        Returns:
            List[float]: A set of win probabilities for each action. This is effectively a policy function that returns
                win probabilities for each action under ALL_GAME_ACTIONS.
        """
        root_node = Node(match_controller=MatchController(), state=state, root_player=state.active_player)

        # Traverse our node tree a number of times
        for _ in range(number_of_searches):

            # Start each search from the root node.
            node = root_node

            # If a current node is fully expanded, select a child (assumed not fully expanded)
            while node.is_fully_expanded():
                # We select a child node from anywhere in our explored hierarchy.
                node = node.select()

            # Newly seleced node might be terminal
            value, is_terminal = node.state.normalised_value_is_terminal()
            if is_terminal:
                # Value is for winner. We compare winner to current node active player.
                # Active player is somewhat arbitrary in a terminal state but it doesn't matter as long we treat
                # the active player as the node owner and back propagate consistently!
                if node.state.round_winner != node.state.active_player:
                    value *= -1
            else:
                # Expansion
                node = node.expand()
                # Newly expanded node might be terminal
                value, is_terminal = node.state.normalised_value_is_terminal()
                if is_terminal:
                    if node.state.round_winner != node.state.active_player:
                        value *= -1
                else:
                    # Simulation
                    value = node.simulate()

            # Now a terminal value is determined, update node tree accordingly.
            node.back_propagate(value)

        # return visit_counts
        # This will effectively become a policy now so need to consider all possible game moves even if invalid.
        action_frequency = np.zeros(len(ALL_GAME_ACTIONS))
        for child in root_node.children:
            action_frequency[child.action_id] = child.visit_count

        # Return as a probability density of winning per action in ACTIONS list.
        return action_frequency / np.sum(action_frequency)


class MctsPlayer(Player):
    """Simple monty carlo player."""

    def __init__(self, number_of_searches_per_move: int) -> None:
        """Initialise Player object.

        Args:
            number_of_searches_per_move (int): How many monte carlo searches to perform per move.
        """
        super().__init__(name="Monty")
        self.number_of_searches = number_of_searches_per_move
        self.mcts = MCTS(match_controller=MatchController())

    def select_action(self, state: MatchState, legal_actions: List[Action]) -> Action:  # noqa:U100
        """Select a player action using the MCTS search.

        Args:
            state (MatchState): Current match state.
            legal_actions (List[Action]): Current legal actions.

        Returns:
            Action: Selected action.
        """
        action_win_probabilities = self.mcts.search(state=state, number_of_searches=self.number_of_searches)
        return ALL_GAME_ACTIONS[np.argmax(action_win_probabilities)]


if __name__ == "__main__":
    # A small test script to see how the number of searches impacts efficacy.
    # The BetterPlayer is not great but it's not completely terrible - it should be able to beat it most of the time.
    for i in [3, 7]:
        nb_searches = 2**i
        mcts_player = MctsPlayer(number_of_searches_per_move=nb_searches)
        better_player = BetterPlayer(name="Betty")
        print(nb_searches, play_automated_matches(player_1=mcts_player, player_2=better_player, number_of_matches=100))
