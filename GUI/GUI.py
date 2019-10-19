from GUI.GUICard import GUICard
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from Game.Card import Card
from functools import partial
import time


class GUI:

    def __init__(self, game_controller, player):

        self.game = game_controller
        self.player = player
        self.opponent = self.game.get_other_player(self.player)
        self.window = Tk()
        self._player_cards = {}
        self._oppenent_cards = {}
        for i in range(5):
            self._player_cards[i] = GUICard()
            self._oppenent_cards[i] = GUICard()
        self._trump_card = GUICard()
        self._deck = GUICard()
        self._leader_card = GUICard()
        self._follower_card = GUICard()
        self._close_deck_button = None
        self._player_swap_trump_button = None
        self._player_points_label = None
        self._opponent_points_label = None
        self._trump_suit_label = None
        self._card_back = Card(Card.Back, 0)
        self.__build_play_space()
        # This feels hacky:
        self.game.on_event_callback_card_played = self.__callback_cards_played

    def __build_play_space(self):
        self._play_button = ttk.Button(self.window, text='Play', command=self.__play_match)
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
        self._close_deck_button = ttk.Button(deck_frame, text='Close_deck', command=self.__close_deck)
        self._close_deck_button.pack(side=TOP)
        deck_cards_frame = Frame(deck_frame)
        deck_cards_frame.pack(side=TOP)
        self._deck.make_card_frame(deck_cards_frame, RIGHT)
        self._trump_card.make_card_frame(deck_cards_frame, LEFT)
        self._player_swap_trump_button = ttk.Button(deck_frame, text='Swap Trump', command=self.__swap_trump)
        self._player_swap_trump_button.pack(side=BOTTOM)
        self._player_points_label = Label(player_info_frame, width=10)
        self._opponent_points_label = Label(opponent_info_frame, width=10)
        self._trump_suit_label = Label(deck_info_frame, width=10)
        self._player_points_label.pack(side=RIGHT)
        self._opponent_points_label.pack(side=RIGHT)
        self._trump_suit_label.pack(side=TOP)
        for i in self._player_cards.keys():
            self._player_cards[i].make_card_frame(player_frame,
                                                  play_command=partial(self.__play_card, i),
                                                  play_marriage_command=partial(self.__play_marriage, i),
                                                  enable_play_buttons=True)
        for i in self._oppenent_cards.keys():
            self._oppenent_cards[i].make_card_frame(opponent_frame)
        self._leader_card.make_card_frame(common_space_frame, pack_side=LEFT)
        self._leader_card.update_card(None)
        self._follower_card.make_card_frame(common_space_frame, pack_side=LEFT)
        self._follower_card.update_card(None)

    def mainloop(self):
        self.window.mainloop()

    def __update_screen(self):
        # When human action re-evaluate legal choices some UI can update accordingly
        self.game.evaluate_active_player_actions()
        self.__update_cards()  # Handle swamp trump and close deck buttons
        self.__update_deck()
        self.__update_labels()

    def __callback_cards_played(self):
        self._leader_card.update_card(self.game.leading_card)
        self._follower_card.update_card(self.game.following_card)
        if self.game.following_card is not None:
            self.window.update_idletasks()
            self.window.update()
            time.sleep(.5)  # This isn't very nice but works just fine
            self.__clear_played_cards()

    def __clear_played_cards(self):
        self._leader_card.update_card(None)
        self._follower_card.update_card(None)

    def __update_labels(self):
        self._player_points_label['text'] = self.__points_string(self.player.game_points, self.player.match_points)
        self._opponent_points_label['text'] = self.__points_string(self.player.opponent_game_points,
                                                                   self.player.opponent_match_points)
        if self.game.trump_card is not None:
            self._trump_suit_label['text'] = Card.Suits[self.game.trump_card.suit]

    def __update_deck(self):
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

    def __update_cards(self):
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
            if i < hand_size:
                self._oppenent_cards[i].update_card(self._card_back)
            else:
                self._oppenent_cards[i].update_card(None)

    def __points_string(self, game_points, match_points):
        return """Game: {a} \nMatch: {b}""".format(a=game_points, b=match_points)

    def __play_match(self):
        self._deck.update_card(self._card_back)
        self.game.new_match()
        self.__new_game()

    def __new_game(self):
        self.__clear_played_cards()
        self.game.new_game()
        self.__handle_AI_actions()
        self.__update_screen()

    def __handle_AI_actions(self):
        self.game.progress_automated_actions()

    def __play_marriage(self, index):
        ui_card = self._player_cards[index]

        next_action = None
        for action in self.player.legal_actions:
            if action.card == ui_card.card and action.marriage is not None:
                next_action = action
                break

        self.__apply_action(next_action)

    def __play_card(self, index):
        ui_card = self._player_cards[index]
        next_action = None
        for action in self.player.legal_actions:
            if action.card == ui_card.card and action.marriage is None:
                next_action = action
                break
        self.__apply_action(next_action)

    def __close_deck(self):
        next_action = None
        for action in self.player.legal_actions:
            if action.close_deck:
                next_action = action
                break

        self.__apply_action(next_action)

    def __swap_trump(self):
        next_action = None
        for action in self.player.legal_actions:
            if action.swap_trump:
                next_action = action
                break

        self.__apply_action(next_action)

    def __apply_action(self, next_action):

        if next_action is None:
            messagebox.showwarning('Title', 'Action is not valid - try something else...')
        else:
            self.game.do_next_action(self.player, next_action)
            self.__handle_AI_actions()
            self.__update_screen()

            if self.game.have_game_winner:
                messagebox.showinfo(title='Game Winner!!!', message='Winner is: ' + self.game.game_winner.name)
                self.__new_game()

            if self.game.have_match_winner:
                messagebox.showinfo(title='Match Winner!!!', message='Winner is: ' +
                                    self.game.match_winner.name + '. Starting new game')
                self.__play_match()
