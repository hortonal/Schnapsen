import os
import torch.nn as nn
import torch as torch

class LinearModule(nn.Module):

    @staticmethod
    def file_path():
        root = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(root, 'AI', 'NeuralNetwork', 'TrainedModels', LinearModule.__name__)

    def __init__(self, inputs, hidden, outputs):
        super(LinearModule, self).__init__()

        self.layer1 = nn.Linear(inputs, hidden)
        self.layer2 = nn.Linear(hidden, hidden)
        self.layer3 = nn.Linear(hidden, outputs)

    def forward(self, inputs):
        x = torch.tanh(self.layer1(inputs))
        x = torch.tanh(self.layer2(x))
        x = torch.tanh(self.layer3(x))
        return x
