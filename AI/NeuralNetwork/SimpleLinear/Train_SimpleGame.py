from AI.NeuralNetwork.SimpleLinear.NNSimpleLinearPlayer_SimpleGame import NNSimpleGamePlayer
from AI.NeuralNetwork.SimpleLinear.Trainer import Trainer
from SimpleGame.SimplePlayer import SimplePlayer
from SimpleGame.SimpleGame import SimpleGame
import Game.GameHelpers as GameHelpers
import logging
import sys

train_mode = True
train_existing_model = False

logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.debug('Starting main')

opponent = SimplePlayer('simon')
nn_player = NNSimpleGamePlayer()
game = SimpleGame(opponent, nn_player)
if train_mode:
    trainer = Trainer(game, nn_player)
    if train_existing_model:
        nn_player.load_model()
    # trainer.train(number_actions=100000, memory_size=1000, batch_size=250)
    trainer.train(number_actions=10000000, memory_size=50000, batch_size=500, update_reference_model=5000)
    nn_player.save_model()
else:
    nn_player.load_model()

#Reset some shit
game.new_match()
game.new_game()
nn_player.automated = True
GameHelpers.play_automated_games(game, 100)
