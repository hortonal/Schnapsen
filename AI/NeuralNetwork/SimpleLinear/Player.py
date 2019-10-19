import torch
from Game.Player import Player
from AI.NeuralNetwork.SimpleLinear.LinearModule import LinearModule
import sys
from AI.NeuralNetwork.IOHelpers import IOHelpers


class NNSimple(Player):

    def __init__(self, name='Nanny_1'):
        super().__init__(name)
        self.Module = LinearModule
        self._file = self.Module.file_path()

    def select_action(self):

        # Set inputs from game state
        # Run NN
        # Convert output to action

        raise Exception('not implemented yet')
        #return random.choice(self.legal_actions)

    def __load_model(self):
        torch.load(self._file)
        pass

    def __save_model(self):
        torch.save(self.__file)
        pass
