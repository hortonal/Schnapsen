"""Entry point for NN training."""
from schnapsen.ai.better_player import BetterPlayer
from schnapsen.ai.neural_network.simple_linear.nn_linear_player import NNSimpleLinearPlayer
from schnapsen.ai.neural_network.simple_linear.trainer import Trainer
from schnapsen.logs import basic_logger


def train() -> None:
    """Training script for the simple neural network model."""
    logger = basic_logger()
    logger.debug('Starting training alogorithm.')

    opponents = [
        BetterPlayer(name="Betty"),
        # RandomPlayer(name="Randy")
    ]

    try:
        # Training against the existing NN player on an evolving basis
        neural_network_player = NNSimpleLinearPlayer()
        neural_network_player.load_model()
        opponents.append(neural_network_player)
        logger.info('Valid existing neural network model loaded and added to opponents')
    except (ModuleNotFoundError, FileNotFoundError):
        pass

    nn_player = NNSimpleLinearPlayer()

    trainer = Trainer(nn_player, opponents)

    # Try and continue training where we left off if possible.
    try:
        nn_player.load_model()
        trainer.initialise_with_players_model()
        logger.info('Continuing to train existing model')
    except (ModuleNotFoundError, FileNotFoundError):
        pass

    # Model is saved every update_reference_model number of 'insert unit here'
    trainer.train(number_actions=10000000, memory_size=20000, batch_size=300, update_reference_model=1000)


if __name__ == "__main__":
    train()
