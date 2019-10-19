import logging


def play_automated_games(game, number_of_ai_games=1000):

    logger = logging.getLogger()

    player1 = game._player_a
    player2 = game._player_b
    player1_wins = 0
    player2_wins = 0

    for i in range(number_of_ai_games):
        game.play_automated()

        if game.match_winner is player1:
            player1_wins += 1
        else:
            player2_wins += 1

        logger.debug('{a} vs {b}, winner is {c}. Running Total: {d}:{e}'.format(
            a=player1.name, b=player2.name, c=game.match_winner.name,
            d=player1_wins, e=player2_wins))

    logger.info('{a} vs {b}: {d}:{e}'.format(
        a=player1.name, b=player2.name, c=game.match_winner.name,
        d=player1_wins, e=player2_wins))
