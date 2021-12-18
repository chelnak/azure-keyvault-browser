from __future__ import annotations

from rich.align import Align
from rich.console import Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from textual.reactive import Reactive
from textual.widget import Widget

from .. import styles


class HeaderWidget(Widget):
    """A custom header widget."""

    title: Reactive[str | Text] = Reactive("Azure Key Vault 🔑")

    def __init__(self) -> None:
        """A custom header widget."""

        self.keys: list[tuple[str, str]] = []
        super().__init__()
        self.layout_size = 1
        self._key_text: RenderableType | None = None

    def make_key_text(self) -> RenderableType:
        """Create text containing all the keys.

        Returns:
            RenderableType: A renderable object containing all the keys.
        """

        text = Text(
            style=f"{styles.GREY} dim",
            no_wrap=True,
            overflow="ellipsis",
            justify="right",
            end="",
        )

        bindings = self.app.bindings.shown_keys

        for binding in bindings:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            key_text = Text.assemble(
                f" {binding.description} ",
                (f"[{key_display}]"),
            )
            text.append_text(key_text)

        return Align.right(text, vertical="bottom", pad=False, height=2)

    def render(self) -> RenderableType:
        """Render the widget.

        Returns:
            RenderableType: Object to be rendered
        """

        if self._key_text is None:
            self._key_text = self.make_key_text()

        title = Align.center(
            renderable=Text(
                self.title,
                style=Style(color=styles.GREY, bold=True),
            ),
            vertical="bottom",
            height=3,
            pad=False,
        )

        head = Panel(
            Group(title, self._key_text),
            box=styles.BOX,
            height=7,
            border_style=Style(color=styles.PURPLE),
            padding=(0, 1, 0, 1),
        )

        return Padding(head, pad=(0, 0))
