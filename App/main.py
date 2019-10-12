"""Main file (test for now)"""
import logging
from Game.Game import Game
from AI.RandomPlayer import RandomPlayer
from AI.BetterPlayer import BetterPlayer
from AI.HumanPlayer import HumanPlayer
from GUI.GUI import GUI


if __name__ == "__main__":
    logging.debug('Starting main')
    logging.getLogger().setLevel(logging.INFO)

    betty = BetterPlayer
    randy = RandomPlayer
    human = HumanPlayer

    player1 = human()
    # player1 = randy()
    player2 = betty()
    player1_wins = 0
    player2_wins = 0

    game = Game(player1, player2)

    human = None
    if type(player2) is HumanPlayer:
        human = player2
    if type(player1) is HumanPlayer:
        human = player1
    if human is not None:
        human.UI = GUI(game, human)
        human.UI.mainloop()

    else:
        number_of_ai_games = 1000

        for i in range(number_of_ai_games):
            game.play_AI()

            if game.match_winner is player1:
                player1_wins += 1
            else:
                player2_wins += 1

            logging.debug('{a} vs {b}, winner is {c}. Running Total: {d}:{e}'.format(
                a=player1.name, b=player2.name, c=game.match_winner.name,
                d=player1_wins, e=player2_wins))

        logging.info('{a} vs {b}: {d}:{e}'.format(
            a=player1.name, b=player2.name, c=game.match_winner.name,
            d=player1_wins, e=player2_wins))
