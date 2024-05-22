from torch import tanh
from torch import Tensor
from torch.nn import Linear
from torch.nn import Module


class LinearModule(Module):
    """A super simple linear neural network whose input/hidden/output layer sizes can be dynamically defined."""

    def __init__(self, inputs: int, hidden: int, outputs: int) -> None:
        super(LinearModule, self).__init__()
        self.layer1 = Linear(inputs, hidden)
        self.layer2 = Linear(hidden, hidden)
        self.layer3 = Linear(hidden, outputs)

    def forward(self, inputs: Tensor) -> Tensor:
        x = tanh(self.layer1(inputs))
        x = tanh(self.layer2(x))
        return tanh(self.layer3(x))
