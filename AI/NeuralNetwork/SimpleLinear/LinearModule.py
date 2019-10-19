import os
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


class LinearModule(nn.Module):

    @staticmethod
    def file_path():
        root = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(root, 'AI', 'NeuralNetwork', 'TrainedModels', LinearModule.__name__)

    def __init__(self, inputs, hidden, outputs):
        super(LinearModule, self).__init__()

        self.layer1 = nn.Linear(inputs, hidden)
        self.layer2 = nn.Linear(hidden, outputs)

    def forward(self, inputs):
        x = F.relu(self.layer1(inputs))
        x = F.relu(self.layer2(x))
        return x


def get_model():
    model = LinearModule()
    return model, optim.SGD(model.parameters(), lr=lr)