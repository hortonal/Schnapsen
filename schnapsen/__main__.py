"""Main file (test for now)."""
from schnapsen.ai.better_player import BetterPlayer
from schnapsen.ai.mcts.mcts import MctsPlayer
from schnapsen.ai.neural_network.simple_linear.nn_linear_player import NNSimpleLinearPlayer
from schnapsen.ai.random_player import RandomPlayer
from schnapsen.core.human_player import HumanPlayer
from schnapsen.gui.gui import GUI
from schnapsen.logs import basic_logger


def main() -> None:
    """Run game. Currently configured manually."""
    logger = basic_logger()
    logger.debug('Starting main')

    human_player = HumanPlayer()
    player_2 = BetterPlayer(name="Betty")    # Only the last player is actually used. A bit of a linting hack..
    player_2 = RandomPlayer(name="Randy")
    player_2 = NNSimpleLinearPlayer("Simple Neural Net")
    player_2 = MctsPlayer(number_of_searches_per_move=80)

    if player_2.requires_model_load:
        player_2.load_model()

    ui = GUI(human_player=human_player, opponent=player_2)
    ui.window.mainloop()


if __name__ == "__main__":
    main()
