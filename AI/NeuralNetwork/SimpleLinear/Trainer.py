"""
Lifted heavily from https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
"""
from AI.NeuralNetwork.SimpleLinear.LinearModule import LinearModule
from AI.NeuralNetwork.IOHelpers import IOHelpers
from AI.NeuralNetwork.ReplayMemory import ReplayMemory, Transition
import torch
import torch.optim as optim
import torch.nn.functional as F

BATCH_SIZE = 500
GAMMA = 0.9


class Trainer:

    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.player.automated = False    # Override the automatic action behaviour when training

        mock_inputs = IOHelpers.create_input_from_game_state(game, player)
        hidden_layer_size = 1000
        input_size = len(mock_inputs)
        # Play, play_marriage + swap trump + close deck = 44 possible actions.
        output_size = 20 * 2 + 2
        # Define simple NN layers
        self.model = LinearModule(input_size, hidden_layer_size, output_size)
        # Maybe use this for stability?
        # self.reference_model = LinearModule(input_size, hidden_layer_size, output_size)
        learning_rate = 1e-3
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)

    def __player_reward(self, prior_game_points, prior_match_points, game_points, match_points):
        # won match is worth 1, won game point is 1/66.
        # The game lasting another hand is worth a negative amount (to encourage quick wins where possible)
        life_decay = -.05
        return life_decay + (match_points - prior_match_points) + (game_points - prior_game_points) / self.game.game_point_limit

    def __optimize(self):
        if len(self.memory) < BATCH_SIZE:
            return
        transitions = self.memory.sample(BATCH_SIZE)

        batch = Transition(*zip(*transitions))

        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)
        next_state_batch = torch.cat(batch.next_state)

        # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
        # columns of actions taken. These are the actions which would've been taken
        # for each batch state according to model
        state_action_values = self.model(state_batch).gather(1, action_batch)

        # Compute V(s_{t+1}) for all next states.
        # Could use a reference net here instead for stability
        next_state_values = self.model(next_state_batch).max(1)[0].detach()
        # Compute the expected Q values
        expected_state_action_values = (next_state_values * GAMMA) + reward_batch

        # Compute Huber loss
        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.model.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()

    def train(self, number_actions=10000):

        memory = ReplayMemory(500)

        for i in range(number_actions):

            # Increment state if action not on NN player
            self.game.progress_automated_actions()

            prior_game_points = self.player.game_points
            prior_match_points = self.player.match_points

            state = IOHelpers.create_input_from_game_state(self.game, self.player)
            # Call NN to give me next move
            action = self.model(state)
            self.game.do_next_action(self.player, action)
            next_state = IOHelpers.create_input_from_game_state(self.game, self.player)
            reward = self.__player_reward(prior_game_points, prior_match_points,
                                          self.player.game_points, self.player.match_points)

            memory.push(state, action, next_state, reward)

            self.__optimize()

            # Update game state as necessary
            if self.game.have_match_winner:
                self.game.new_match()
                self.game.new_game()
            if self.game.have_game_winner:
                self.game.new_game()
