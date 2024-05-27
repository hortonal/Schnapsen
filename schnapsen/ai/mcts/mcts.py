from random import choice
import math
import numpy as np
from typing import List
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from schnapsen.core.match_controller import MatchController
from schnapsen.core.action import Action

@dataclass
class MatchState():
    pass


@dataclass
class Node:
    # Each game needs to be its own complete state copy!!
    match_controller: MatchController
    state: MatchState
    parent: Node = None
    action_taken: Action = None
    children: List[Node] = []
    expandable_moves: List[Action] = []
    visit_count: int = 0
    value_sum: float = 0

    def __post_init__(self) -> None:
        exandable_moves = self.match_controller.get_valid_moves(self.state)
    # Exta args...

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
        action = self.expandable_moves[action_ix]
        # Remove selected action from possible moves
        self.expandable_moves.pop(action_ix)

        # Set up a child state. We setup the game state assuming 
        child_state = self.state.copy()
        child_state = self.match_controller.update_state_with_action(child_state, action)
        child_state = self.match_controller.change_perspective(child_state, player)
        
        child = Node(match_controller=self.match_controller, state=child_state, parent=self, action_taken=action)
        self.children.append(child)
        return child

    def simulate(self) -> float:
        is_terminal= self.match_controller.round_state.have_round_winner
        value = self.match_controller.round_state.round_winner.match_points
        
        if is_terminal:
            return value

        rollout_state = self.state.copy()
        rollout_player = None # TODO: Get current player
        
        while True:
            valid_moves = self.match_controller.get_valid_moves(rollout_state)
            # Pick random move
            action_ix = choice(range(len(self.expandable_moves)))
            action = self.expandable_moves[action_ix]
            rollout_state = self.match_controller.update_state_with_action(rollout_state, action, rollout_player)

            # TODO - Update game logic first!
            # is_terminal= self.match_controller.round_state.have_round_winner
            # value = self.match_controller.round_state.round_winner.match_points

        value = ''


@dataclass
class MCTS:
    """Monte Carlo Tress Search Implementation."""
    
    match_controller: MatchController
        
    def search(self, state: MatchState, number_of_searches: int):
        
        root_node = Node(match_controller=MatchController, state=state)

        # Node Selection
        for i_search in range(number_of_searches):
            node = root_node

            while node.is_fully_expanded():
                node = node.select()

            # self.game.get_value_and_terminated(self.state, self.action_taken)
            is_terminal= self.match_controller.round_state.have_round_winner
            value = self.match_controller.round_state.round_winner.match_points

            if not is_terminal:
                # Expansion
                node = node.expand()

                # Simulation
                value = node.simulate()
                           

            # Backpropagation

        # return visit_counts
