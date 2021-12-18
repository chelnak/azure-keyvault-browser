from __future__ import annotations

import string
from typing import Any

from azure.keyvault.secrets import SecretProperties

# from fast_autocomplete import AutoComplete
from rich.console import RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from textual import events
from textual.keys import Keys
from textual.reactive import Reactive, watch
from textual.widget import Widget
from textual_inputs.events import InputOnChange, InputOnFocus

from .. import styles
from ..search import Search
from .flash import FlashMessageType, ShowFlashNotification


# https://whoosh.readthedocs.io/en/latest/indexing.html
class FilterWidget(Widget):
    """
    A simple text input widget.

    Args:
        name (Optional[str]): The unique name of the widget. If None, the
            widget will be automatically named.
        value (str, optional): Defaults to "". The starting text value.
        placeholder (str, optional): Defaults to "". Text that appears
            in the widget when value is "" and the widget is not focused.
        title (str, optional): Defaults to "". A title on the top left
            of the widget's border.
        password (bool, optional): Defaults to False. Hides the text
            input, replacing it with bullets.

    Attributes:
        value (str): the value of the text field
        placeholder (str): The placeholder message.
        title (str): The displayed title of the widget.
        has_password (bool): True if the text field masks the input.
        has_focus (bool): True if the widget is focused.
        cursor (Tuple[str, Style]): The character used for the cursor
            and a rich Style object defining its appearance.

    Messages:
        InputOnChange: Emitted when the contents of the input changes.
        InputOnFocus: Emitted when the widget becomes focused.

    Examples:

    .. code-block:: python

        from textual_inputs import TextInput

        email_input = TextInput(
            name="email",
            placeholder="enter your email address...",
            title="Email",
        )

    """

    value: Reactive[str] = Reactive("")
    valid: Reactive[bool] = Reactive(True)
    cursor: tuple[str, Style] = (
        "|",
        Style(
            color="white",
            blink=True,
            bold=True,
        ),
    )
    _cursor_position: Reactive[int] = Reactive(0)
    _has_focus: Reactive[bool] = Reactive(False)

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        self.name = "search"
        super().__init__(self.name, **kwargs)
        self.placeholder = ""
        self.title = f"🔍 [{styles.GREY}]filter[/]"
        self.visible = True
        self.has_password = False
        self._cursor_position = len(self.value)

        self.search_engine: Search = Search()

    def __rich_repr__(self):
        yield "name", self.name
        yield "title", self.title
        if self.has_password:
            value = "".join("•" for _ in self.value)
        else:
            value = self.value
        yield "value", value

    @property
    def has_focus(self) -> bool:
        """
        Produces True if widget is focused.

        Returns:
            bool: True if widget is focused
        """

        return self._has_focus

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""
        watch(self.app, "searchable_nodes", self.index)

    def render(self) -> RenderableType:
        """Render the widget.

        Returns:
            RenderableType: Object to be rendered
        """

        if self.has_focus:
            segments = self._render_text_with_cursor()
        else:
            if len(self.value) == 0:
                segments = [self.placeholder]
            else:
                segments = [self._conceal_or_reveal(self.value)]

        text = Text.assemble(*segments)

        border_style = (
            Style(color=styles.LIGHT_PURPLE if self.has_focus else styles.PURPLE)
            if self.valid
            else Style(color=styles.RED)
        )

        return Padding(
            Panel(
                text,
                title=self.title,
                title_align="left",
                height=3,
                border_style=border_style,
                box=styles.BOX,
            ),
            pad=(0, 0),
        )

    def _conceal_or_reveal(self, segment: str) -> str:
        """
        Produce the segment either concealed like a password or as it
        was passed.

        Args:
            segment (str): The segment to conceal or reveal

        Returns:
            str: The concealed or revealed segment
        """
        if self.has_password:
            return "".join("•" for _ in segment)
        return segment

    def _render_text_with_cursor(self) -> list[str | tuple[str, Style]]:
        """
        Produces the renderable Text object combining value and cursor

        Returns:
            list[str | tuple[str, Style]] - The renderable text
        """

        segments: list[str | tuple[str, Style]] = []

        if len(self.value) == 0:
            segments = [self.cursor]
        elif self._cursor_position == 0:
            segments = [self.cursor, self._conceal_or_reveal(self.value)]
        elif self._cursor_position == len(self.value):
            segments = [self._conceal_or_reveal(self.value), self.cursor]
        else:
            segments = [
                self._conceal_or_reveal(self.value[: self._cursor_position]),
                self.cursor,
                self._conceal_or_reveal(self.value[self._cursor_position :]),
            ]

        return segments

    async def on_focus(self, event: events.Focus) -> None:
        self._has_focus = True
        await self._emit_on_focus()

    async def on_blur(self, event: events.Blur) -> None:
        self._has_focus = False

    async def on_key(self, event: events.Key) -> None:

        if event.key == "left":
            if self._cursor_position == 0:
                self._cursor_position = 0
            else:
                self._cursor_position -= 1

        elif event.key == "right":
            if self._cursor_position != len(self.value):
                self._cursor_position = self._cursor_position + 1

        elif event.key == "home":
            self._cursor_position = 0

        elif event.key == "end":
            self._cursor_position = len(self.value)

        elif event.key == "ctrl+h":  # Backspace
            if self._cursor_position == 0:
                return
            elif len(self.value) == 1:
                self.value = ""
                self._cursor_position = 0
                await self.toggle_field_status()

            elif len(self.value) == 2:
                if self._cursor_position == 1:
                    self.value = self.value[1]
                    self._cursor_position = 0
                else:
                    self.value = self.value[0]
                    self._cursor_position = 1
            else:
                if self._cursor_position == 1:
                    self.value = self.value[1:]
                    self._cursor_position = 0
                elif self._cursor_position == len(self.value):
                    self.value = self.value[:-1]
                    self._cursor_position -= 1
                else:
                    self.value = (
                        self.value[: self._cursor_position - 1]
                        + self.value[self._cursor_position :]
                    )
                    self._cursor_position -= 1

            if len(self.value) == 1:
                self.app.search_result = []

            if len(self.value) > 1:
                await self.search(search_string=self.value)

            await self._emit_on_change(event)

        elif event.key == "delete":
            if self._cursor_position == len(self.value):
                return
            elif len(self.value) == 1:
                self.value = ""
            elif len(self.value) == 2:
                if self._cursor_position == 1:
                    self.value = self.value[0]
                else:
                    self.value = self.value[1]
            else:
                if self._cursor_position == 0:
                    self.value = self.value[1:]
                else:
                    self.value = (
                        self.value[: self._cursor_position]
                        + self.value[self._cursor_position + 1 :]
                    )
            await self._emit_on_change(event)

        elif event.key == Keys.Enter:

            if len(self.value) == 0:
                await self.post_message_from_child(
                    ShowFlashNotification(
                        self,
                        type=FlashMessageType.WARNING,
                        value="No search term specified. Please enter a search term.",
                    )
                )

            elif self.app.search_result and self.app.search_result[0] == "none":
                await self.post_message_from_child(
                    ShowFlashNotification(
                        self,
                        type=FlashMessageType.ERROR,
                        value=f'No results found for "{self.value}".',
                    )
                )
            else:
                await self.app.set_focus(self.app.secrets)

        elif event.key in string.printable:
            if self._cursor_position == 0:
                self.value = event.key + self.value
            elif self._cursor_position == len(self.value):
                self.value = self.value + event.key
            else:
                self.value = (
                    self.value[: self._cursor_position]
                    + event.key
                    + self.value[self._cursor_position :]
                )

            if not self._cursor_position > len(self.value):
                self._cursor_position += 1

            search_string = self.value or event.key
            await self.search(search_string=search_string)

            await self._emit_on_change(event)

    async def _emit_on_change(self, event: events.Key) -> None:
        event.stop()
        await self.emit(InputOnChange(self))

    async def _emit_on_focus(self) -> None:
        await self.emit(InputOnFocus(self))

    # AKV additional methods

    async def toggle_field_status(self, valid=True) -> None:
        """Toggles field status.

        Args:
            valid (bool): Whether the field is valid or not.
        """

        self.valid = valid

    async def index(self, nodes: list[SecretProperties]) -> None:
        """Create an index from a list of searchable nodes.

        Args:
            nodes (list[SecretProperties]): A list of secret properties.
        """

        if len(nodes) == 0:
            self.log("Nothing to index yet")
            return

        words = [x.name.lower() for x in nodes]
        self.search_engine.index = words
        self.log(f"{len(words)} searchable nodes have been indexed")

    async def search(self, search_string: str) -> None:
        """Search for a string.

        Args:
            search_string (str): The string to search for.
        """

        if not self.search_engine.index:
            return

        result = self.search_engine.search(search_string)
        self.app.search_result = result if len(result) > 0 else ["none"]
        await self.toggle_field_status(valid=(len(result) > 0))

    async def clear(self) -> None:
        """Clear the search field."""

        self.value = ""
        self.refresh(layout=True)
