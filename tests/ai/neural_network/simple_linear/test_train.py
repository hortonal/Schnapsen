from schnapsen.ai.neural_network.simple_linear import train
from schnapsen.ai.neural_network.simple_linear.trainer import TrainConfig


def test_train_integration():
    """For now, we'll simply test that training runs without throwing exceptions."""
    train.train(
        TrainConfig(
            number_actions=100,
            memory_size=10,
            batch_size=10,
            nb_training_loops_before_reference_model_update=50,
            update_model_on_disk=False   # Don't override local model file!
        )
    )
