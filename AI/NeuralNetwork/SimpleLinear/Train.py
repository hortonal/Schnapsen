from AI.NeuralNetwork.SimpleLinear.Player import Player
from AI.NeuralNetwork.SimpleLinear.Trainer import Trainer
from AI.BetterPlayer import BetterPlayer
from Game.Game import Game
import Game.GameHelpers as GameHelpers

opponent = BetterPlayer()
nn_player = Player()
game = Game(nn_player, opponent)
trainer = Trainer(game, nn_player)
trainer.train()

# Play for reals?
nn_player.automated = True
GameHelpers.play_automated_games(game, 1000)
