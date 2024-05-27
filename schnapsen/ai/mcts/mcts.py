"""Monte Carlo Trial."""
from __future__ import annotations

from dataclasses import dataclass
import math
from random import choice
from typing import List

import numpy as np

from schnapsen.ai.random_player import RandomPlayer
from schnapsen.core.action import Action
from schnapsen.core.match_controller import MatchController
from schnapsen.core.player import Player
from schnapsen.core.state import MatchState


@dataclass
class Node:
    """A node in a monte carlo tree search."""
    match_controller: MatchController
    state: MatchState
    parent: Node = None
    action_taken: Action = None
    children: List[Node] = None
    expandable_moves: List[Action] = None
    visit_count: int = 0
    value_sum: float = 0
    c: float = math.sqrt(2)

    def __post_init__(self) -> None:
        """Initialise node state."""
        self.exandable_moves = self.match_controller.get_valid_moves(state=self.state)
        self.children = []
        self.expandable_moves = []

    def is_fully_expanded(self) -> bool:
        """Check if Node has been completely explored.

        Returns
        -------
        _type_
            _description_
        """
        return self.match_controller.round_state.have_round_winner

    def select(self) -> Node:
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

        Parameters
        ----------
        child : Node
            The node to calculate UCB score for

        Returns
        -------
        float
            The calculated ucb score.
        """
        q_value = child.value_sum / child.visit_count
        # If the child node represents an opponent's move, the q_value is "opposite" of what it is for us
        # e.g. a perfect match position for us is q_value 1. An opponents q_value is 1, this is bad for us
        # We want to put the child in the worst possible state.
        # If the child node is the result of swapping a trump (for example) then the q_value does not need adjusting.
        if child.match_controller.round_state.active_player != self.match_controller.round_state.active_player:
            q_value = 1 - q_value
        return q_value + self.c * math.sqrt(math.log(self.visit_count) / child.visit_count)

    def expand(self) -> Node:
        # Sample a child state at random
        action_ix = choice(range(len(self.expandable_moves)))
        # Remove and select random action possible moves
        action = self.expandable_moves.pop(action_ix)

        # Set up a child state. We setup the game state assuming
        child_state = self.state.copy()
        self.match_controller.update_state_with_action(child_state, action)
        # This might require some thought!... Doesn't exist but should be simple to implement
        # child_state = state.change_perspective(child_state)
        child = Node(match_controller=self.match_controller,
                     state=child_state, parent=self, action_taken=action)
        self.children.append(child)
        return child

    def simulate(self) -> float:
        is_terminal = self.state.round_winner is not None
        if is_terminal:
            return self.state.player_states[self.state.round_winner].match_points

        rollout_state = self.state.copy()
        rollout_player = self.state.active_player

        while True:
            # Pick random move
            action = choice(
                self.match_controller.get_valid_moves(rollout_state))
            self.match_controller.update_state_with_action(
                rollout_state, action, rollout_player)
            is_terminal = rollout_state.round_winner is not None
            if is_terminal:
                return rollout_state.player_states[rollout_state.round_winner].match_points

            rollout_player = rollout_state.get_other_player(rollout_player)

    def backpropagate(self, value: int) -> None:
        self.value_sum += value
        self.visit_count += 1
        # TODO flip sign if parent is opponent. Not always true
        if self.parent is not None:
            self.parent.backpropagate(value)


@dataclass
class MCTS:
    """Monte Carlo Tress Search Implementation."""

    match_controller: MatchController

    def search(self, state: MatchState, number_of_searches: int):

        root_node = Node(match_controller=MatchController, state=state)

        # Node Selection
        for _ in range(number_of_searches):
            node = root_node

            while node.is_fully_expanded():
                node = node.select()

            # self.game.get_value_and_terminated(self.state, self.action_taken)
            is_terminal = node.state.round_winner is not None
            value = node.state.player_states[node.state.round_winner].match_points
            # Might need to negate this value to be from opponents perspective.

            if not is_terminal:
                # Expansion
                node = node.expand()
                # Simulation
                value = node.simulate()

            # Backpropagation
            node.backpropagate(value)

        # return visit_counts
        action_probs = np.zeros(self.game.action_size)
        for child in root_node.children:
            action_probs[child.action_taken] = child.visit_count

        action_probs /= np.sum(action_probs)
        return action_probs


class MctsPlayer(Player):
    """Simple monty carlo player."""

    def __init__(self) -> None:
        """Initialise Player object."""
        super().__init__(name="Monty", automated=True)
        self.mcts = MCTS(match_controller=MatchController())

    def select_action(self, state: MatchState, legal_actions: List[Action]) -> Action:
        mcts_probs = self.mcts.search(state=state, number_of_searches=10)
        action = np.argmax(mcts_probs)
        return action


if __name__ == "__main__":
    match_controller = MatchController()
    state = match_controller.get_new_match_state(
        player_1=RandomPlayer(name="Randy"),
        player_2=MctsPlayer())
    match_controller.reset_round_state(state)
    match_controller.progress_automated_actions(state)

