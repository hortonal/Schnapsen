"""
Lifted heavily from https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
"""
import torch
import torch.nn.functional as F
import time
import random
import logging
import math
import Game.GameHelpers as GameHelpers
from AI.NeuralNetwork.ReplayMemory import ReplayMemory, Transition
from AI.NeuralNetwork.SimpleLinear.IOHelpers import IOHelpers
from AI.NeuralNetwork.SimpleLinear.LinearModule import LinearModule

GAMMA = 0.95
REWARD_COST_OF_LIVING = -0.10
HIDDEN_LAYER_SIZE = 500
LEARNING_RATE = 0.0001

EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 100000


class Trainer:

    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.player.automated = False    # Override the automatic action behaviour when training
        self.memory = None
        self.logger = logging.getLogger()
        self.actions_selected = 0
        self.optimizer_count = 0
        self.reference_model = None
        self._cumulative_loss = 0
        mock_inputs = IOHelpers.create_input_from_game_state(game, player)

        input_size = len(mock_inputs)
        output_size = len(IOHelpers.output_actions)

        # Define simple NN layers
        self.model = LinearModule(input_size, HIDDEN_LAYER_SIZE, output_size)
        self.player.model = self.model
        self.reference_model = LinearModule(input_size, HIDDEN_LAYER_SIZE, output_size)
        self.__update_reference_model()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=LEARNING_RATE)

    def initialise_with_players_model(self):
        self.model = self.player.model
        self.__update_reference_model()

    def __player_reward(self, prior_game_points, prior_match_points, game_points, match_points):
        return torch.tensor(REWARD_COST_OF_LIVING +
                            (match_points - prior_match_points) + (game_points - prior_game_points) / self.game.game_point_limit
                            , dtype=torch.float)

    def __optimize(self, batch_size):
        if len(self.memory) < batch_size:
            return

        # Prepare batch replay
        transitions = self.memory.sample(batch_size)
        batch = Transition(*zip(*transitions))
        state_batch = torch.cat(batch.state).view(batch_size, -1)
        action_batch = torch.cat(batch.action).view(batch_size, -1)
        next_state_batch = torch.cat(batch.next_state).view(batch_size, -1)
        next_legal_actions_batch = torch.cat(batch.next_legal_actions).view(batch_size, -1)
        reward_batch = torch.tensor(batch.reward)

        # Build Q(S,A) map
        state_action_values = self.model(state_batch).gather(1, action_batch)

        # Use the reference model to decide future state value (for stability apparently...)
        next_state_q_values = self.reference_model(next_state_batch)
        next_state_values = IOHelpers.policy_batch(next_state_q_values, next_legal_actions_batch)
        expected_state_action_values = (next_state_values * GAMMA) + reward_batch

        # Compute Huber loss
        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))
        self._cumulative_loss += float(loss)

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.model.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()
        self.optimizer_count += 1

    def start_new_match(self):
        self.game.new_match()
        self.start_new_game()

    def start_new_game(self):
        self.game.new_game()
        # Increment state if action not on NN player
        self.game.progress_automated_actions()

    def __update_reference_model(self):
        self.reference_model.load_state_dict(self.model.state_dict())

    def train(self, number_actions=10000, training_time=0, memory_size=1000, batch_size=100, update_reference_model=1000):

        self.memory = ReplayMemory(memory_size)
        self.start_new_match()

        if training_time > 0:
            now = time.time()
            while time.time() - now < training_time:
                self.single_training_loop(batch_size)

        else:
            for i in range(number_actions):
                self.single_training_loop(batch_size)
                # Every few thousand epochs save out the trained model to disk
                # (so we can break the program without losing progress)
                if i % update_reference_model == 0:
                    self.__update_reference_model()
                    logging.info(str(i) + ' actions run. Optimizer count: ' + str(self.optimizer_count) + '. loss: ' + str(self._cumulative_loss / update_reference_model))
                    self._cumulative_loss = 0
                    self.player.save_model()
                    self.start_new_match()
                    self.player.automated = True
                    GameHelpers.play_automated_games(self.game, 100)
                    self.player.automated = False
                    self.start_new_match()

    def select_action(self, state):
        # Call NN to give me next move
        # todo: implement epsilon greedy
        sample = random.random()
        eps_threshold = EPS_END + (EPS_START - EPS_END) * math.exp(-1. * self.actions_selected / EPS_DECAY)
        self.actions_selected += 1

        if sample > eps_threshold:
            return IOHelpers.get_random_legal_action(self.game, self.player)
        else:
            with torch.no_grad():
                q_values = self.model(state)
            return IOHelpers.policy(q_values, self.game, self.player)

    def single_training_loop(self, batch_size):

        prior_game_points = self.player.game_points
        prior_match_points = self.player.match_points
        state = IOHelpers.create_input_from_game_state(self.game, self.player)
        action_id, action = self.select_action(state)

        # Apply action an perform any opponent actions. I.e. continue game until out turn to act
        self.game.do_next_action(self.player, action)
        self.game.progress_automated_actions()

        next_state = IOHelpers.create_input_from_game_state(self.game, self.player)
        reward = self.__player_reward(prior_game_points, prior_match_points,
                                      self.player.game_points, self.player.match_points)
        next_legal_actions, _ = IOHelpers.get_legal_actions(self.game, self.player)
        self.memory.push(state, action_id, next_state, next_legal_actions.unsqueeze(0), reward)
        self.__optimize(batch_size)
        # Update game state as necessary
        if self.game.have_match_winner:
            self.start_new_match()
        if self.game.have_game_winner:
            self.start_new_game()
