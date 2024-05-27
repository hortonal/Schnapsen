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
from typing import List

from schnapsen.core.action import Action
from schnapsen.core.card import Card
from schnapsen.core.card import Suit_string_map
from schnapsen.core.match_controller import MatchController
from schnapsen.core.player import Player
from schnapsen.gui.gui_card import CARD_BACK
from schnapsen.gui.gui_card import GUICard


class GUI:
    """Simple game user interface."""

    def __init__(self, human_player: Player, opponent: Player) -> None:
        """Create GUI object.

        Args:
            human_player (Player): The human player object interacting with the UI
            opponent (Player): The opponent to the human player, assumed a bot.
        """
        self.match_controller = MatchController()
        self.match_state = None
        self.player = human_player
        self.opponent = opponent
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
        self._player_info_label = None
        self._opponent_info_label = None
        self._trump_suit_label = None
        self._card_back = Card(CARD_BACK, 0)
        self._actions_history: List[Action] = []
        self._build_play_space()
        # This feels hacky:
        self.match_controller.action_callback = self._handle_match_controller_action
        self._cheat_mode = False

    def _build_play_space(self) -> None:
        info_label_width = 25
        # Handle button styles
        style = ttk.Style()
        style.configure('TButton', background='green', focuscolor='none')
        # style.map('TButton', background=[('active', 'red')])

        self.window.option_add("*Background", "green")
        self.window.configure(bg="green")
        # High level UI Frames
        self._play_button = ttk.Button(
            self.window, text='Start Match', command=self._play_match, takefocus=False)
        self._play_button.pack(side=TOP)
        # Actions Frame
        action_frame = Frame(self.window)
        action_frame.pack(side=BOTTOM)
        action_frame_label = Label(action_frame, height=7)
        action_frame_label.pack(side=BOTTOM)
        self._action_frame_label = action_frame_label
        # Area for all players
        players_frame = Frame(self.window)
        players_frame.pack(side=LEFT)
        # Area common deck
        deck_frame = Frame(self.window)
        deck_frame.pack(side=RIGHT)
        # Area for player 1
        player_frame = Frame(players_frame)
        player_frame.pack(side=TOP)
        # Area for laying down cards
        common_space_frame = Frame(players_frame, height=200)
        common_space_frame.pack(side=TOP, pady=50)
        common_space_frame_padding = Label(common_space_frame, width=info_label_width)
        common_space_frame_padding.pack(side=LEFT)
        # Area for player 2
        opponent_frame = Frame(players_frame)
        opponent_frame.pack(side=TOP)
        # Player info frames
        player_info_frame = Frame(player_frame)
        player_info_frame.pack(side=LEFT)
        opponent_info_frame = Frame(opponent_frame)
        opponent_info_frame.pack(side=LEFT)
        deck_info_frame = Frame(deck_frame)
        deck_info_frame.pack(side=BOTTOM)
        self._player_info_label = Label(player_info_frame, width=info_label_width)
        self._player_info_label.pack(side=RIGHT)
        self._opponent_info_label = Label(opponent_info_frame, width=info_label_width)
        self._opponent_info_label.pack(side=RIGHT)
        # Deck related sub frames
        cheat_mode_button = ttk.Button(
            deck_frame, text='Cheat Mode', command=self._toggle_cheat_mode, takefocus=False)
        cheat_mode_button.pack(side=TOP)
        self._close_deck_button = ttk.Button(
            deck_frame, text='Close Deck', command=self._close_deck, takefocus=False)
        self._close_deck_button.pack(side=TOP)
        deck_cards_frame = Frame(deck_frame)
        deck_cards_frame.pack(side=TOP)
        self._deck.make_card_frame(deck_cards_frame, RIGHT)
        self._trump_card.make_card_frame(deck_cards_frame, LEFT)
        self._player_swap_trump_button = ttk.Button(deck_frame, text='Swap Trump',
                                                    command=self._swap_trump, takefocus=False)
        self._player_swap_trump_button.pack(side=BOTTOM)
        self._trump_suit_label = Label(deck_info_frame, width=10)
        self._trump_suit_label.pack(side=TOP)

        for i in self._player_cards.keys():
            self._player_cards[i].make_card_frame(player_frame,
                                                  play_command=partial(
                                                      self._play_card, i),
                                                  play_marriage_command=partial(
                                                      self._play_marriage, i),
                                                  enable_play_buttons=True)
        for i in self._opponent_cards.keys():
            self._opponent_cards[i].make_card_frame(opponent_frame)
        self._leader_card.make_card_frame(common_space_frame, pack_side=LEFT)
        self._leader_card.update_card(None)
        self._follower_card.make_card_frame(common_space_frame, pack_side=LEFT)
        self._follower_card.update_card(None)

    def _update_screen(self) -> None:
        # When human action re-evaluate legal choices some UI can update accordingly
        self._update_cards()  # Handle swap trump and close deck buttons
        self._update_deck()
        self._update_labels()

    def _update_actions_history(self, action: Action, reset: bool = False) -> None:
        if reset:
            self._actions_history = []
            self._action_frame_label['text'] = "Action history:\n\n\n\n\n"
        else:
            self._actions_history.append(action)
            while len(self._actions_history) > 5:
                self._actions_history.pop(0)
            self._action_frame_label['text'] = "Action history:\n" + \
                "\n".join([str(action_item) for action_item in self._actions_history])

    def _handle_match_controller_action(self, action: Action) -> None:
        self._update_actions_history(action=action)
        self._leader_card.update_card(self.match_state.leading_card)
        self._follower_card.update_card(
            self.match_state.following_card)
        if self.match_state.following_card is not None:
            self.window.update_idletasks()
            self.window.update()
            time.sleep(.5)  # This isn't very nice but works just fine
            self._clear_played_cards()

    def _clear_played_cards(self) -> None:
        self._leader_card.update_card(None)
        self._follower_card.update_card(None)

    def _update_labels(self) -> None:
        player_state = self.match_state.player_states[self.player]
        opponent_state = self.match_state.player_states[self.opponent]
        self._player_info_label['text'] = self._points_string(
            self.player.name, player_state.round_points, player_state.match_points)
        self._opponent_info_label['text'] = self._points_string(
            self.opponent.name, opponent_state.round_points, opponent_state.match_points)
        if self.match_state.trump_card is not None:
            self._trump_suit_label['text'] = Suit_string_map[self.match_state.trump_card.suit]

    def _update_deck(self) -> None:
        can_swamp_trump = False
        can_close_deck = False
        for action in self.match_controller.get_valid_moves(self.match_state):
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
        if self.match_state.deck_closed:
            self._trump_card.update_card(None)
            self._deck.update_card(None)
        else:
            self._trump_card.update_card(
                self.match_state.trump_card)
            self._deck.update_card(self._card_back)

    def _update_cards(self) -> None:
        # Update player cards
        hand = self.match_state.player_states[self.player].hand
        hand_size = len(hand)
        for i in range(5):
            if i < hand_size:
                card = hand[i]
                self._player_cards[i].update_card(card)
                self._player_cards[i].play_button['state'] = 'disable'
                self._player_cards[i].play_marriage_button['state'] = 'disable'
                for action in self.match_controller.get_valid_moves(self.match_state):
                    if action.card == card:
                        self._player_cards[i].play_button['state'] = 'normal'
                        if action.marriage is not None:
                            self._player_cards[i].play_marriage_button['state'] = 'normal'

            else:
                self._player_cards[i].update_card(None)
                self._player_cards[i].play_button['state'] = 'disable'
                self._player_cards[i].play_marriage_button['state'] = 'disable'

        # Update opponents cards
        opponent_hand = self.match_state.player_states[self.opponent].hand
        hand_size = len(opponent_hand)
        for i in range(5):
            card = None
            if i < hand_size:
                if self._cheat_mode:
                    card = opponent_hand[i]
                else:
                    card = self._card_back
            self._opponent_cards[i].update_card(card)

    def _points_string(self, player_name: str, round_points: int, match_points: int) -> str:
        return f"Player: {player_name}\nGame: {round_points} \nMatch: {match_points}"

    def _play_match(self) -> None:
        self._deck.update_card(self._card_back)
        self.match_state = self.match_controller.get_new_match_state(self.player, self.opponent)
        self._new_game()

    def _new_game(self) -> None:
        self._update_actions_history(None, reset=True)
        self._clear_played_cards()
        self.match_controller.reset_round_state(self.match_state)
        self._handle_ai_actions()
        self._update_screen()

    def _handle_ai_actions(self) -> None:
        self.match_controller.progress_automated_actions(state=self.match_state)

    def _play_marriage(self, index: int) -> None:
        ui_card = self._player_cards[index]

        next_action = None
        for action in self.match_controller.get_valid_moves(self.match_state):
            if action.card == ui_card.card and action.marriage is not None:
                next_action = action
                break

        self._apply_action(next_action)

    def _play_card(self, index: int) -> None:
        ui_card = self._player_cards[index]
        next_action = None
        for action in self.match_controller.get_valid_moves(self.match_state):
            if action.card == ui_card.card and action.marriage is None:
                next_action = action
                break
        self._apply_action(next_action)

    def _close_deck(self) -> None:
        next_action = None
        for action in self.match_controller.get_valid_moves(self.match_state):
            if action.close_deck:
                next_action = action
                break

        self._apply_action(next_action)

    def _swap_trump(self) -> None:
        next_action = None
        for action in self.match_controller.get_valid_moves(self.match_state):
            if action.swap_trump:
                next_action = action
                break

        self._apply_action(next_action)

    def _apply_action(self, action: Action) -> None:

        if action is None:
            messagebox.showwarning(
                'Title', 'Action is not valid - try something else...')
        else:

            self.match_controller.update_state_with_action(state=self.match_state, action=action)
            self._handle_ai_actions()
            self._update_screen()

            if self.match_state.round_winner:
                messagebox.showinfo(title='Round Winner!',
                                    message=f'Winner is: {self.match_state.round_winner.name}')
                self._new_game()

            if self.match_state.match_winner:
                messagebox.showinfo(
                    title='Match Winner!!!',
                    message=(f'Match winner is: {self.match_state.match_winner.name}.'
                             ' Starting new game'))
                self._play_match()

    def _toggle_cheat_mode(self) -> None:
        self._cheat_mode = not self._cheat_mode
        self._update_screen()
