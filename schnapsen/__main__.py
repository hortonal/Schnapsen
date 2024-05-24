"""Main file (test for now)."""
from schnapsen.ai.better_player import BetterPlayer
from schnapsen.ai.neural_network.simple_linear.nn_linear_player import NNSimpleLinearPlayer
from schnapsen.ai.random_player import RandomPlayer
from schnapsen.core import match_helpers
from schnapsen.core.human_player import HumanPlayer
from schnapsen.core.match_controller import MatchController
from schnapsen.gui.gui import GUI
from schnapsen.logs import basic_logger


def main() -> None:
    """Run game. Currently configured manually."""
    logger = basic_logger()
    logger.debug('Starting main')

    player1 = HumanPlayer()
    player2 = BetterPlayer(name="Betty")    # Only the last player is actually used. A bit of a linting hack..
    player2 = RandomPlayer(name="Randy")
    player2 = NNSimpleLinearPlayer("Simple Neural Net")

    human = None
    for player in [player1, player2]:
        if isinstance(player, HumanPlayer):
            human = player
        if player.requires_model_load:
            player.load_model()

    match_controller = MatchController(player1, player2)

    if human is not None:
        human.UI = GUI(match_controller=match_controller, human_player=human)
        human.UI.window.mainloop()

    else:
        match_helpers.play_automated_matches(match_controller=match_controller, number_of_matches=1000)


if __name__ == "__main__":
    main()
