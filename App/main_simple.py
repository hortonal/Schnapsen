"""Main file (test for now)"""
import logging
import sys
import Game.GameHelpers as GameHelpers
from SimpleGame.SimpleGame import SimpleGame
from SimpleGame.SimplePlayer import SimplePlayer
from SimpleGame.SimpleHuman import SimpleHumanPlayer

from AI.NeuralNetwork.SimpleLinear.NNSimpleLinearPlayer_SimpleGame import NNSimpleGamePlayer
from GUI.GUI import GUI

if __name__ == "__main__":

    logging.basicConfig(stream=sys.stderr)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.debug('Starting main')

    simon = SimplePlayer
    human = SimpleHumanPlayer
    nanny = NNSimpleGamePlayer
#    nanny = NeuralNetwork

    player1 = human()
    player2 = nanny()
    # player1 = randy()
    # player1 = simon('simon')

    human = None
    for player in [player1, player2]:
        if type(player) is SimpleHumanPlayer:
            human = player
        if player.requires_model_load:
            player.load_model()

    player1_wins = 0
    player2_wins = 0

    game = SimpleGame(player1, player2)

    if human is not None:
        human.UI = GUI(game, human)
        human.UI.mainloop()

    else:
        GameHelpers.play_automated_games(game, 1000)
