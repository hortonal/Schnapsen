from AI.NeuralNetwork.SimpleLinear.NNSimpleLinearPlayer import NNSimpleLinearPlayer
from AI.NeuralNetwork.SimpleLinear.Trainer import Trainer
from AI.BetterPlayer import BetterPlayer
from AI.RandomPlayer import RandomPlayer
from Game.Game import Game
import logging
import sys

train_mode = True
train_existing_model = True

logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.debug('Starting main')

opponents = []
# Training against the NN player
neural_network_player = NNSimpleLinearPlayer()
neural_network_player.load_model()
opponents.append(neural_network_player)
opponents.append(BetterPlayer())
opponents.append(RandomPlayer())

nn_player = NNSimpleLinearPlayer()

trainer = Trainer(nn_player, opponents)

if train_existing_model:
    nn_player.load_model()
    trainer.initialise_with_players_model()

trainer.train(number_actions=10000000, memory_size=20000, batch_size=300, update_reference_model=1000)
# No longer need to save the model as the trainer does this when reference model updated
# nn_player.save_model()
