"""Module for UI representation of card."""
import os
from tkinter import BOTTOM
from tkinter import Canvas
from tkinter import Frame
from tkinter import LEFT
from tkinter import TOP
from tkinter import ttk
from tkinter import Widget
from typing import Callable

from PIL import Image
from PIL import ImageTk

from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value

# A couple of special keys for UI representation of cards
CARD_BACK = 4
CARD_EMPTY = 5

SUIT_STR_MAP = {
    Suit.CLUB: 'c',
    Suit.DIAMOND: 'd',
    Suit.SPADE: 's',
    Suit.HEART: 'h',
    CARD_BACK: 'back',
    CARD_EMPTY: 'blank'
}

VALUE_STR_MAP = {
    Value.ACE: '01',
    Value.TEN: '10',
    Value.KING: '13',
    Value.QUEEN: '12',
    Value.JACK: '11'
}


class GUICard:
    """UI container for a playing card and its actions."""

    def __init__(self) -> None:
        """Create GUI Card instance."""
        self.parent_frame = None
        self.file_open = None
        self.card_image = None
        self.card_canvas = None
        self.card_image_on_canvas = None
        self.card = None
        self.play_button = None
        self.play_marriage_button = None

    def make_card_frame(self, parent_frame: Widget, pack_side: str = LEFT, play_command: Callable = None,
                        play_marriage_command: Callable = None, enable_play_buttons: bool = False) -> Frame:
        """Create frame for card object.

        Parameters
        ----------
        parent_frame : Widget
            Parent Frame.
        pack_side : str, optional
            Where to place the card within the parent frame, by default LEFT
        play_command : Callable, optional
            Action to perform upon click, by default None
        play_marriage_command : Callable, optional
            Action to perform upon marriage click, by default None
        enable_play_buttons : bool, optional
            Enable play buttons, by default False

        Returns
        -------
        Frame
            The built Frame.
        """
        self.parent_frame = Frame(parent_frame)
        self.parent_frame.pack(side=pack_side)

        # Load the appropriate image.
        self.file_open = Image.open(self._image_path(CARD_BACK, 0))
        self.card_image = ImageTk.PhotoImage(self.file_open)

        self.card_canvas = Canvas(self.parent_frame, width=self.card_image.width(), height=self.card_image.height())
        self.card_canvas.create_image((self.card_image.width() / 2 + 2,
                                      self.card_image.height() / 2 + 3), image=self.card_image)
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

    def update_card(self, card: Card) -> None:
        """Update with new card.

        Parameters
        ----------
        card : Card
            The new card. If None, it's treated as a blank/missing card.
        """
        self.card = card

        if card is None:
            suit = CARD_EMPTY
            value = 0
        else:
            suit = card.suit
            value = card.value

        self.file_open = Image.open(self._image_path(suit, value))
        self.card_image = ImageTk.PhotoImage(self.file_open)
        self.card_canvas.itemconfig(self.card_image_on_canvas, image=self.card_image)

    def _image_path(self, suit: int | Suit, value: int | Value) -> str:
        """Return the local file image path.

        Parameters
        ----------
        suit : int | Suits
            The suit of the card. Some special values for the card back and blank values are accommodated here.
        value : int | Values
            The value of the card when appropriate.

        Returns
        -------
        str
            The absolute file path for the requested card.
        """
        this_root_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(this_root_path, 'card_images',
                            f'{SUIT_STR_MAP.get(suit, '')}{VALUE_STR_MAP.get(value, '')}.bmp')
