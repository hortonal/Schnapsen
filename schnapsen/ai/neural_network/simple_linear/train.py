"""Entry point for NN training."""
from schnapsen.ai.better_player import BetterPlayer
from schnapsen.ai.neural_network.simple_linear.nn_linear_player import NNSimpleLinearPlayer
from schnapsen.ai.neural_network.simple_linear.trainer import Trainer
from schnapsen.ai.neural_network.simple_linear.trainer import TrainConfig
from schnapsen.logs import basic_logger


def train(train_config: TrainConfig) -> None:
    """Training script for the simple neural network model.

    Parameters
    ----------
    train_config : TrainConfig
        Configuration for the training scenario
    """
    logger = basic_logger()
    logger.debug('Starting training alogorithm.')

    opponents = [
        BetterPlayer(name="Betty"),
        # RandomPlayer(name="Randy")
    ]

    try:
        # Training against the existing NN player on an evolving basis
        neural_network_player = NNSimpleLinearPlayer(name="NN_Reference")
        neural_network_player.load_model()
        opponents.append(neural_network_player)
        logger.info('Valid existing neural network model loaded and added to opponents')
    except (ModuleNotFoundError, FileNotFoundError):
        pass

    nn_player = NNSimpleLinearPlayer(name="NN_Learner")

    trainer = Trainer(nn_player, opponents)

    # If an existing model exists on file store, we'll load it up and continue training it.
    # This lets us break training into multiple sessions.
    try:
        nn_player.load_model()
        trainer.initialise_with_players_model()
        logger.info('Continuing to train existing model')
    except (ModuleNotFoundError, FileNotFoundError):
        pass

    trainer.train(train_config)


if __name__ == "__main__":
    train(TrainConfig(number_actions=100000000,
                      batch_size=1000,
                      memory_size=20000,
                      nb_training_loops_before_reference_model_update=5000))
