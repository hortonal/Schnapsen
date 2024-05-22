"""Module for game UI controller."""
from functools import partial
import time
from tkinter import BOTTOM
from tkinter import Frame
from tkinter import Label
from tkinter import LEFT
from tkinter import messagebox
from tkinter import RIGHT
from tkinter import Tk
from tkinter import TOP
from tkinter import ttk

from schnapsen.core.action import Action
from schnapsen.core.card import Card
from schnapsen.core.card import Suit_string_map
from schnapsen.core.match_controller import MatchController
from schnapsen.core.player import Player
from schnapsen.gui.gui_card import CARD_BACK
from schnapsen.gui.gui_card import GUICard


class GUI:
    """Simple game user interface."""

    def __init__(self, game_controller: MatchController, human_player: Player) -> None:
        """Create GUI object.

        Parameters
        ----------
        game_controller : Game
            The underlying game controller in use.
        human_player : Player
            The human player object interacting with the UI.
        """
        self.game = game_controller
        self.player = human_player
        self.opponent = self.game.get_other_player(self.player)
        self.window = Tk()
        self._player_cards = {}
        self._opponent_cards = {}
        for i in range(5):
            self._player_cards[i] = GUICard()
            self._opponent_cards[i] = GUICard()
        self._trump_card = GUICard()
        self._deck = GUICard()
        self._leader_card = GUICard()
        self._follower_card = GUICard()
        self._close_deck_button = None
        self._player_swap_trump_button = None
        self._player_points_label = None
        self._opponent_points_label = None
        self._trump_suit_label = None
        self._card_back = Card(CARD_BACK, 0)
        self._build_play_space()
        # This feels hacky:
        self.game.on_event_callback_card_played = self._callback_cards_played
        self._cheat_mode = False

    def _build_play_space(self) -> None:
        self._play_button = ttk.Button(self.window, text='Play', command=self._play_match)
        self._play_button.pack(side=TOP)
        players_frame = Frame(self.window)
        deck_frame = Frame(self.window)
        players_frame.pack(side=LEFT)
        deck_frame.pack(side=RIGHT)
        player_frame = Frame(players_frame)
        opponent_frame = Frame(players_frame)
        common_space_frame = Frame(players_frame, height=200)
        player_frame.pack(side=TOP)
        common_space_frame.pack(side=TOP)
        opponent_frame.pack(side=BOTTOM)
        player_info_frame = Frame(player_frame)
        opponent_info_frame = Frame(opponent_frame)
        deck_info_frame = Frame(deck_frame)
        player_info_frame.pack(side=LEFT)
        opponent_info_frame.pack(side=LEFT)
        deck_info_frame.pack(side=BOTTOM)
        cheat_mode_button = ttk.Button(deck_frame, text='Cheat Mode', command=self._togle_cheat_mode)
        cheat_mode_button.pack(side=TOP)
        self._close_deck_button = ttk.Button(deck_frame, text='Close_deck', command=self._close_deck)
        self._close_deck_button.pack(side=TOP)
        deck_cards_frame = Frame(deck_frame)
        deck_cards_frame.pack(side=TOP)
        self._deck.make_card_frame(deck_cards_frame, RIGHT)
        self._trump_card.make_card_frame(deck_cards_frame, LEFT)
        self._player_swap_trump_button = ttk.Button(deck_frame, text='Swap Trump', command=self._swap_trump)
        self._player_swap_trump_button.pack(side=BOTTOM)
        self._player_points_label = Label(player_info_frame, width=10)
        self._opponent_points_label = Label(opponent_info_frame, width=10)
        self._trump_suit_label = Label(deck_info_frame, width=10)
        self._player_points_label.pack(side=RIGHT)
        self._opponent_points_label.pack(side=RIGHT)
        self._trump_suit_label.pack(side=TOP)
        for i in self._player_cards.keys():
            self._player_cards[i].make_card_frame(player_frame,
                                                  play_command=partial(self._play_card, i),
                                                  play_marriage_command=partial(self._play_marriage, i),
                                                  enable_play_buttons=True)
        for i in self._opponent_cards.keys():
            self._opponent_cards[i].make_card_frame(opponent_frame)
        self._leader_card.make_card_frame(common_space_frame, pack_side=LEFT)
        self._leader_card.update_card(None)
        self._follower_card.make_card_frame(common_space_frame, pack_side=LEFT)
        self._follower_card.update_card(None)

    def _update_screen(self) -> None:
        # When human action re-evaluate legal choices some UI can update accordingly
        self.game.evaluate_active_player_actions()
        self._update_cards()  # Handle swamp trump and close deck buttons
        self._update_deck()
        self._update_labels()

    def _callback_cards_played(self) -> None:
        self._leader_card.update_card(self.game.leading_card)
        self._follower_card.update_card(self.game.following_card)
        if self.game.following_card is not None:
            self.window.update_idletasks()
            self.window.update()
            time.sleep(.5)  # This isn't very nice but works just fine
            self._clear_played_cards()

    def _clear_played_cards(self) -> None:
        self._leader_card.update_card(None)
        self._follower_card.update_card(None)

    def _update_labels(self) -> None:
        self._player_points_label['text'] = self._points_string(self.player.game_points, self.player.match_points)
        self._opponent_points_label['text'] = self._points_string(self.player.opponent_game_points,
                                                                  self.player.opponent_match_points)
        if self.game.trump_card is not None:
            self._trump_suit_label['text'] = Suit_string_map[self.game.trump_card.suit]

    def _update_deck(self) -> None:
        can_swamp_trump = False
        can_close_deck = False
        for action in self.player.legal_actions:
            if action.swap_trump:
                can_swamp_trump = True
            if action.close_deck:
                can_close_deck = True
        if can_swamp_trump:
            self._player_swap_trump_button['state'] = 'normal'
        else:
            self._player_swap_trump_button['state'] = 'disable'
        if can_close_deck:
            self._close_deck_button['state'] = 'normal'
        else:
            self._close_deck_button['state'] = 'disable'

        # Handle close deck
        if self.game.deck_closed:
            self._trump_card.update_card(None)
            self._deck.update_card(None)
        else:
            self._trump_card.update_card(self.game.trump_card)
            self._deck.update_card(self._card_back)

    def _update_cards(self) -> None:
        # Update player cards
        hand_size = len(self.player.hand)
        for i in range(5):
            if i < hand_size:
                card = self.player.hand[i]
                self._player_cards[i].update_card(card)
                self._player_cards[i].play_button['state'] = 'disable'
                self._player_cards[i].play_marriage_button['state'] = 'disable'
                for action in self.player.legal_actions:
                    if action.card == card:
                        self._player_cards[i].play_button['state'] = 'normal'
                        if action.marriage is not None:
                            self._player_cards[i].play_marriage_button['state'] = 'normal'

            else:
                self._player_cards[i].update_card(None)
                self._player_cards[i].play_button['state'] = 'disable'
                self._player_cards[i].play_marriage_button['state'] = 'disable'

        # Update opponents cards
        hand_size = len(self.opponent.hand)
        for i in range(5):
            card = None
            if i < hand_size:
                if self._cheat_mode:
                    card = self.opponent.hand[i]
                else:
                    card = self._card_back
            self._opponent_cards[i].update_card(card)

    def _points_string(self, game_points: int, match_points: int) -> str:
        return """Game: {a} \nMatch: {b}""".format(a=game_points, b=match_points)

    def _play_match(self) -> None:
        self._deck.update_card(self._card_back)
        self.game.new_match()
        self._new_game()

    def _new_game(self) -> None:
        self._clear_played_cards()
        self.game.new_game()
        self._handle_ai_actions()
        self._update_screen()

    def _handle_ai_actions(self) -> None:
        self.game.progress_automated_actions()

    def _play_marriage(self, index: int) -> None:
        ui_card = self._player_cards[index]

        next_action = None
        for action in self.player.legal_actions:
            if action.card == ui_card.card and action.marriage is not None:
                next_action = action
                break

        self._apply_action(next_action)

    def _play_card(self, index: int) -> None:
        ui_card = self._player_cards[index]
        next_action = None
        for action in self.player.legal_actions:
            if action.card == ui_card.card and action.marriage is None:
                next_action = action
                break
        self._apply_action(next_action)

    def _close_deck(self) -> None:
        next_action = None
        for action in self.player.legal_actions:
            if action.close_deck:
                next_action = action
                break

        self._apply_action(next_action)

    def _swap_trump(self) -> None:
        next_action = None
        for action in self.player.legal_actions:
            if action.swap_trump:
                next_action = action
                break

        self._apply_action(next_action)

    def _apply_action(self, next_action: Action) -> None:

        if next_action is None:
            messagebox.showwarning('Title', 'Action is not valid - try something else...')
        else:
            self.game.do_next_action(self.player, next_action)
            self._handle_ai_actions()
            self._update_screen()

            if self.game.have_game_winner:
                messagebox.showinfo(title='Game Winner!!!', message='Winner is: ' + self.game.game_winner.name)
                self._new_game()

            if self.game.have_match_winner:
                messagebox.showinfo(title='Match Winner!!!',
                                    message='Winner is: ' + self.game.match_winner.name + '. Starting new game')
                self._play_match()

    def _togle_cheat_mode(self) -> None:
        self._cheat_mode = not self._cheat_mode
        self._update_screen()
