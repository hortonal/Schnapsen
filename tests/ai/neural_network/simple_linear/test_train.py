from schnapsen.ai.neural_network.simple_linear import train
from schnapsen.ai.neural_network.simple_linear.trainer import TrainConfig


def test_train():
    train.train(TrainConfig(100, 10, 10, 1000))
