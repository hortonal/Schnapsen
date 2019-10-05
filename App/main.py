"""Main file (test for now)"""
from Game.Game import Game
from AI.SimplePlayer import SimplerPlayer

if __name__ == "__main__":

    player1 = SimplerPlayer('Dave')
    player2 = SimplerPlayer('Fred')

    game = Game(player1, player2)
    game.play()
