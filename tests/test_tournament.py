from schnapsen import tournament


def test_tournament():
    # A poor test, but simply check it runs to completion for now!
    tournament.run_tournament(number_of_matches_per_battle=1)
