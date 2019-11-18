from AI.NeuralNetwork.SimpleLinear.NNSimpleLinearPlayer import NNSimpleLinearPlayer
from AI.NeuralNetwork.SimpleLinear.Trainer import Trainer
from AI.BetterPlayer import BetterPlayer
from Game.Game import Game
import logging
import sys

train_mode = True
train_existing_model = False

logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.debug('Starting main')

opponent = BetterPlayer()
nn_player = NNSimpleLinearPlayer()
game = Game(nn_player, opponent)
trainer = Trainer(game, nn_player)

if train_existing_model:
    nn_player.load_model()
    trainer.initialise_with_players_model()

trainer.train(number_actions=10000000, memory_size=20000, batch_size=100, update_reference_model=1000)
nn_player.save_model()
