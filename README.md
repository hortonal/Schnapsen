# Schnapsen

A python implementation of the classic Austrian card game Schnapsen.

This repo implements the game controller logic, a number of bot/AI opponents and a simple UI to play against the bots.
The real intention of the repo is to focus on opponent/AI methods (see "Building your own Player/Bot" below). The
best opponent at present is the Monte Carlo Tree Search player.

For more info on the game itself and the rules, see wikipedia: <https://en.wikipedia.org/wiki/Schnapsen>

## Basic setup / installation

### Docker Dev Container

This repo includes has a VSCode dev container that can be used to get a quickly working dev environment running. This
requires a Docker daemon like Docker Desktop to be available/running.

### Local installation

To run/develop locally, your're strongly encouraged to use an environment manager. E.g. [mini]conda, [mini]mamba, venv or similar. We'll assume a conda variant is being used:

``` bash
conda env create -n schnapsen
conda activate schnapsen
# Basic application requirements
pip install -r requirements.txt
# Dev requirements
pip install -r requirements-dev.txt
# Install current package for development
pip install -e .
```

## Play the game

Once the installation steps are complete (i.e. you have a working environment), you should be able to play the game
against the latest AI using:

``` bash
python -m schnapsen
```

Basic UI:

- Deal the cards by hitting the "Start Match" button.
- Play a card via the "P" button underneath it
- Play part of a Marriage, if applicable, via the "M" button beneath a Queen/King
- The other buttons should be self explanatory

## Development

### Building your own Player/Bot

All players must inherit from the Player class and implement the select action method. For example see the
RandomPlayer, BetterPlayer or NNSimpleLinearPlayer implementations. As discovered with the Monte Carlo Tree Search, you
need to be careful not to give your bot too much game knowledge (see shuffle_imperfect_information in MatchController!).

### Test your bot against the competition

If you add your player to the list of players in schnapsen/tournament.py, you can run a tournament and check your bot's
skill with:

``` bash
python -m schnapsen.tournament
```

### Update the existing AI model

There is one quite naive neural network implementation whose model is saved in this repo. Further training (starting
with the existing model) can be performed with the following. This will load the existing model and continue training
and saving out updated versions of the model.

``` bash
python -m schnapsen.ai.neural_network.simple_linear.train
```

### Unit Tests

Assuming the installation instructions have been followed, you can run the tests with

``` bash
pytest
```

### Linting

Likewise, linting can be checked with

``` bash
flake8
```

## TODO

Here's a non-exhaustive laundry list of things to work on next:

- Add a simple CI chain with automated test/linting
- Improve existing BetterPlayer bot (there should be some very easy wins)
- Improve/rewrite simple NN AI. Perhaps try LTSM?
- Compare to a monte carlo type AI?
