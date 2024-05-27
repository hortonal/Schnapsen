"""A reinforcement learning training module.

Heavily references https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
"""
from dataclasses import dataclass
import logging
import math
import random
from typing import List, Tuple

import torch
from torch.nn.functional import smooth_l1_loss

from schnapsen.ai.neural_network.replay_memory import ReplayMemory
from schnapsen.ai.neural_network.replay_memory import Transition
from schnapsen.ai.neural_network.simple_linear.io_helpers import IOHelpers
from schnapsen.ai.neural_network.simple_linear.nn_linear_module import LinearModule
from schnapsen.core import match_helpers
from schnapsen.core.action import Action
from schnapsen.core.match_controller import MatchController
from schnapsen.core.player import Player
from schnapsen.core.state import MatchState
from schnapsen.core.state import PlayerState

GAMMA = 0.95
REWARD_COST_OF_LIVING = -0.10
HIDDEN_LAYER_SIZE = 500
LEARNING_RATE = 0.0001

EPS_START = 0.95
EPS_END = 0.05
EPS_DECAY = 100000

random.seed(0)

@dataclass
class TrainConfig:
    """Container for basic training config.

    TODO: Detail what this parameters do
    """
    # The total number of actions to train for.
    number_actions: int
    # The number of actions to retain in a memory. Used for bulk optimisations.
    memory_size: int = 1000
    # How many actions to sample from memory for each optimisation step.
    batch_size: int = 100
    # After how many actions do we save out a copy of the latest model and udate our reference model.
    nb_training_loops_before_reference_model_update: int = 1000
    # If true, we save the udpated model to disk upon reference model update. (Gets set to false for testing purposes).
    update_model_on_disk: bool = True


class Trainer:
    """A trainer for the simple reinforcement neural network.

    TODO: Flesh out the details once I'm re-familiarised with them.
    """

    def __init__(self, player: Player, opponents: List[Player]) -> None:
        """Create trainer instance.

        Parameters
        ----------
        player : Player
            The learning agent.
        opponents : List[Player]
            A set of opponent players. This can be more AI or simple bots.
        """
        self.match_controller: MatchController = MatchController()
        self.match_state: MatchState = None
        self.player: Player = player
        self.player_state: PlayerState = None   # For convenience
        self.opponents = opponents       # Collection of AI opponents to train against
        # Override the automatic action behaviour when training
        self.player.automated = False
        self.memory = None
        self.logger = logging.getLogger()
        self.actions_selected = 0
        self.optimizer_count = 0
        self.reference_model = None
        self._cumulative_loss = 0

        # Create a usable game state just figure out require vector sizes for network.
        self.__create_match_vs_random_opponent()
        self.match_controller.reset_round_state(self.match_state)
        mock_inputs = IOHelpers.create_input_from_game_state(state=self.match_state)

        input_size = len(mock_inputs)
        output_size = len(IOHelpers.output_actions)

        # Define simple NN layers
        self.model = LinearModule(input_size, HIDDEN_LAYER_SIZE, output_size)
        self.player.model = self.model
        self.reference_model = LinearModule(input_size, HIDDEN_LAYER_SIZE, output_size)
        self._update_reference_model()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=LEARNING_RATE)

    def initialise_with_players_model(self) -> None:
        """Update our NN reference state from that of the player (assumed to be a freshly loaded model state)."""
        self.model = self.player.model
        self._update_reference_model()

    def __create_match_vs_random_opponent(self):
        self.match_state = self.match_controller.get_new_match_state(
            player_1=self.player, player_2=random.choice(self.opponents))
        self.player_state = self.match_state.player_states[self.player]

    def __player_reward(self, prior_round_points, prior_match_points, round_points, match_points):
        # TODO: Detail the logic here. This can/should almost certainly be tweaked!
        return torch.tensor(
            # Letting the game go on for no reason is bad. Discourage living forever
            REWARD_COST_OF_LIVING +                 # noqa: W504
            # Reward more match points
            (match_points - prior_match_points) +   # noqa: W504
            # Game points (but not as much as match points)
            (round_points - prior_round_points) / \
            self.match_state.round_point_limit,
            dtype=torch.float)

    def __optimize(self, batch_size):
        if len(self.memory) < batch_size:
            return
        # Prepare batch replay

        transitions = self.memory.sample(batch_size)
        batch = Transition(*zip(*transitions))
        state_batch = torch.cat(batch.state).view(batch_size, -1)
        action_batch = torch.cat(batch.action).view(batch_size, -1)
        next_state_batch = torch.cat(batch.next_state).view(batch_size, -1)
        next_legal_actions_batch = torch.cat(
            batch.next_legal_actions).view(batch_size, -1)
        reward_batch = torch.tensor(batch.reward)

        # Build Q(S,A) map
        state_action_values = self.model(state_batch).gather(1, action_batch)

        # Use the reference model to decide future state value (for stability apparently...)
        next_state_q_values = self.reference_model(next_state_batch)
        next_state_values = IOHelpers.policy_batch(
            next_state_q_values, next_legal_actions_batch)
        expected_state_action_values = (
            next_state_values * GAMMA) + reward_batch

        # Compute Huber loss
        loss = smooth_l1_loss(state_action_values,
                              expected_state_action_values.unsqueeze(1))
        self._cumulative_loss += float(loss)

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.model.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()
        self.optimizer_count += 1

    def _start_new_match(self) -> None:
        self.__create_match_vs_random_opponent()
        self._start_new_game()

    def _start_new_game(self) -> None:
        self.match_controller.reset_round_state(self.match_state)
        # Increment state if action not on NN player
        self.match_controller.progress_automated_actions(self.match_state)

    def _update_reference_model(self) -> None:
        self.reference_model.load_state_dict(self.model.state_dict())

    def train(self, train_config: TrainConfig) -> None:
        """Main training routing entry point.

        Parameters
        ----------
        train_config : TrainConfig
            A training config object. See TrainConfig for details.
        """
        self.memory = ReplayMemory(train_config.memory_size)
        self._start_new_match()

        for i in range(train_config.number_actions):
            self.single_training_loop(train_config.batch_size)
            # Every few thousand epochs save out the trained model to disk
            # (so we can break the program without losing progress)
            if i % train_config.nb_training_loops_before_reference_model_update == 0 and i > 0:
                self._update_reference_model()
                logging.info("%i actions run. Optimizer count: %i. loss: %f", i, self.optimizer_count,
                             self._cumulative_loss / train_config.nb_training_loops_before_reference_model_update)
                self._cumulative_loss = 0

                # For testing we may wish to not update the persisted model
                if train_config.update_model_on_disk:
                    self.player.save_model()

                # Reset game state and play a bunch of games for validation
                self._start_new_match()
                self.player.automated = True
                match_helpers.play_automated_matches(player_1=self.match_state.players[0],
                                                     player_2=self.match_state.players[1],
                                                     number_of_matches=100)
                self.player.automated = False

                self._start_new_match()

    def select_action(self, state: MatchState) -> Tuple[int, Action]:
        """Select action with the neural network to select next move.

        To avoid local minima, introduce some random selections to our actor via the eps_threshold.
        """
        sample = random.random()
        eps_threshold = EPS_END + \
            (EPS_START - EPS_END) * \
            math.exp(-1. * self.actions_selected / EPS_DECAY)
        self.actions_selected += 1

        if sample > eps_threshold:
            action = random.choice(self.match_controller.get_valid_moves(self.match_state))
            i = IOHelpers.get_index_for_action(action)
            return torch.tensor([i], dtype=torch.long), action
        else:
            with torch.no_grad():
                q_values = self.model(state)
            return IOHelpers.policy(q_values, self.match_state)

    def single_training_loop(self, batch_size: int):
        prior_round_points = self.player_state.round_points
        prior_match_points = self.player_state.match_points
        state = IOHelpers.create_input_from_game_state(self.match_state)
        action_id, action = self.select_action(state)

        # Apply action and perform any opponent actions. I.e. continue game until our turn to act
        self.match_controller.update_state_with_action(self.match_state, action)
        self.match_controller.progress_automated_actions(self.match_state)

        next_state = IOHelpers.create_input_from_game_state(self.match_state)
        reward = self.__player_reward(prior_round_points, prior_match_points,
                                      self.player_state.round_points, self.player_state.match_points)
        next_legal_actions, _ = IOHelpers.get_legal_actions(self.match_state)
        self.memory.push(state, action_id, next_state,
                         next_legal_actions.unsqueeze(0), reward)
        self.__optimize(batch_size)
        # Update game state as necessary
        if self.match_state.match_winner:
            self._start_new_match()
        if self.match_state.round_winner:
            self._start_new_game()
