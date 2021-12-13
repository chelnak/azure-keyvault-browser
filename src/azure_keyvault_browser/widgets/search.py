from __future__ import annotations

import string
from typing import Any

from azure.keyvault.secrets import SecretProperties
from fast_autocomplete import AutoComplete
from rich.console import RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from textual import events
from textual.keys import Keys
from textual.reactive import Reactive, watch
from textual_inputs import TextInput
from textual_inputs.events import InputOnChange

from .. import styles
from .flash import FlashMessageType, ShowFlashNotification


class SearchWidget(TextInput):
    """A custom search widget."""

    autocompleter: AutoComplete = None
    value: Reactive[str] = Reactive("")
    valid: Reactive[bool] = Reactive(True)

    def __init__(self) -> None:
        """A custom search widget."""

        super().__init__(name="search")

        self.title = f"🔍 [{styles.GREY}]search[/]"
        self.visible = True

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        async def map(nodes: list[SecretProperties]):
            searchable_words, synonyms = self.map_nodes(nodes=nodes)
            self.autocompleter = AutoComplete(words=searchable_words, synonyms=synonyms)
            self.log("Searchable nodes have been mapped")

        watch(self.app, "searchable_nodes", map)

    async def clear(self) -> None:
        """Clear the search field."""

        self.value = ""
        self.refresh(layout=True)

    async def handle_input_on_change(self) -> None:
        """Handle an InputOnChange message."""

        self.refresh()

    async def on_key(self, event: events.Key) -> None:
        """Handle a key press.

        Args:
            event (events.Key): The event containing the pressed key.
        """

        if event.key == Keys.Enter:

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

        elif event.key == "ctrl+h":  # Backspace
            if len(self.value) == 1:
                self.app.search_result = []

            if len(self.value) > 1:
                await self.search(search_string=self.value)

        elif event.key in string.printable:

            search_string = self.value or event.key
            await self.search(search_string=search_string)

        await self.post_message(InputOnChange(self))

    async def search(self, search_string: str) -> None:
        """Search for a string in the autocompleter.

        Args:
            search_string (str): The string to search for.
        """

        if search_string:
            result = self.autocompleter.get_tokens_flat_list(search_string)
            self.app.search_result = result if len(result) > 0 else ["none"]
            await self.toggle_field_status(valid=len(result) > 0)
        else:
            self.app.search_result = []

    def map_nodes(
        self, nodes: list[SecretProperties]
    ) -> tuple[dict[str, Any], dict[str, list[str]]]:
        """Build a map of nodes and synonyms.

        Args:
            nodes (dict[NodeID, TreeNode]): A dictionary of nodes.

        Returns:
            tuple[dict[str, Any], dict[str, list[str]]]: A tuple containing searchable_words and synonyms.
        """

        searchable_words: dict[str, Any] = {}
        synonyms: dict[str, list[str]] = {}
        for node in nodes:
            name = node.name.lower()
            searchable_words[name] = {}

            # Secret names must can contain Alphanumerics and hyphens (dash).
            # So we can make a niave attempt at synonyms.
            name_words = name.split("-")
            synonyms[name] = name_words if len(name_words) > 1 else []

        return searchable_words, synonyms

    async def toggle_field_status(self, valid=True) -> None:
        """Toggles field status.

        Args:
            valid (bool): Whether the field is valid or not.
        """

        self.valid = valid

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
