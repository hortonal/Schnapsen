from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from Game.Card import Card

class GUICard:

    def __init__(self):

        self.parent_frame = None
        self.file_open = None
        self.card_image = None
        self.card_canvas = None
        self.card_image_on_canvas = None
        self.card = None
        self.play_button = None
        self.play_marriage_button = None

    def make_card_frame(self, parent_frame, pack_side=LEFT, play_command=None,
                        play_marriage_command=None, enable_play_buttons=False):

        self.parent_frame = Frame(parent_frame)
        self.parent_frame.pack(side=pack_side)

        self.initialise_card()

        self.card_canvas = Canvas(self.parent_frame, width=self.card_image.width(), height= self.card_image.height())
        self.card_canvas.create_image((self.card_image.width()/2 + 2, self.card_image.height()/2 + 3), image=self.card_image)
        self.card_image_on_canvas = self.card_canvas.create_image(
            (self.card_image.width() / 2 + 2, self.card_image.height() / 2 + 3),
            image=self.card_image)

        self.card_canvas.pack(side=TOP, padx=2, pady=2)

        if enable_play_buttons:
            self.play_button = ttk.Button(self.parent_frame, text='P', width=0, command=play_command)
            self.play_marriage_button = ttk.Button(self.parent_frame, text='M', width=0, command=play_marriage_command)
            self.play_button.pack(side=BOTTOM)
            self.play_marriage_button.pack(side=BOTTOM)
        return self.parent_frame

    def initialise_card(self):
        self.file_open = Image.open(self.create_image_path(Card.Back, 0))
        self.card_image = ImageTk.PhotoImage(self.file_open)

    def update_card(self, card):
        self.card = card

        if card is None:
            suit = Card.Empty
            value = 0
        else:
            suit = card.suit
            value = card.value

        self.file_open = Image.open(self.create_image_path(suit, value))
        self.card_image = ImageTk.PhotoImage(self.file_open)
        self.card_canvas.itemconfig(self.card_image_on_canvas, image=self.card_image)

    def create_image_path(self, suit, value):

        root_str = '../GUI/Decks/StandardDeck/{suit}{value}.bmp'
        suit_str = ''
        value_str = ''

        if suit == Card.Clubs:
            suit_str = 'c'
        elif suit == Card.Diamonds:
            suit_str = 'd'
        elif suit == Card.Spades:
            suit_str = 's'
        elif suit == Card.Hearts:
            suit_str = 'h'
        elif suit == Card.Back:
            suit_str = 'back'
        elif suit == Card.Empty:
            suit_str = 'blank'

        if value == Card.Ace:
            value_str = '01'
        elif value == Card.Ten:
            value_str = '10'
        elif value == Card.King:
            value_str = '13'
        elif value == Card.Queen:
            value_str = '12'
        elif value == Card.Jack:
            value_str = '11'

        return root_str.format(suit=suit_str, value=value_str)
