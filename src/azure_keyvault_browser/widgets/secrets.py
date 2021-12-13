from __future__ import annotations

from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from textual import events
from textual.keys import Keys
from textual.reactive import Reactive, watch
from textual.widget import Widget

from .. import styles
from ..azure import KeyVault, SecretProperties
from ..renderables import SecretsTableRenderable


class SecretsWidget(Widget):
    """A secrets details widget. Used to display secrets."""

    has_focus: Reactive[bool] = Reactive(False)

    page: int = 1
    row: int = 0

    def __init__(self) -> None:
        """A job details widget. Used to display builds within a job."""

        name = self.__class__.__name__
        super().__init__(name=name)
        self.secrets: list[SecretProperties] = []
        self.renderable: SecretsTableRenderable | None = None
        self.client: KeyVault = self.app.client

    def on_focus(self) -> None:
        """Sets has_focus to true when the item is clicked."""

        self.has_focus = True

    def on_blur(self) -> None:
        """Sets has_focus to false when an item no longer has focus."""

        self.has_focus = False

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        self.secrets = await self.client.get_secrets()
        self.app.searchable_nodes = self.secrets

        watch(self.app, "search_result", self.update)

    async def update(self, search_result: list[str]) -> None:
        """Update the widget with the search result.

        Args:
            search_result (list[str]): A list of secret names that match the search.
        """

        if len(search_result) > 0:
            if search_result[0] == "none":
                self.secrets = self.app.searchable_nodes
            else:
                self.secrets = [
                    x for x in self.secrets if x.name.lower() in search_result
                ]
        else:
            self.secrets = self.app.searchable_nodes
        self.refresh(layout=True)

    def on_key(self, event: events.Key) -> None:
        """Handle a key press.

        Args:
            event (events.Key): The event containing the pressed key.
        """

        if self.renderable is None:
            return

        key = event.key

        if key == Keys.Enter:

            row = self.renderable.get_cell_value(0, self.row)
            self.app.selected_secret = row
            self.app.selected_version = ""

        if key == Keys.Left:
            self.renderable.previous_page()
        elif key == Keys.Right:
            self.renderable.next_page()
        elif key == "f":
            self.renderable.first_page()
        elif key == "l":
            self.renderable.last_page()
        elif key == Keys.Up:
            self.renderable.previous_row()
        elif key == Keys.Down:
            self.renderable.next_row()

        self.refresh(layout=True)

    def render_table(self) -> None:
        """Renders the build history table."""

        self.renderable = SecretsTableRenderable(
            items=self.secrets,
            title="secrets",
            page_size=self.size.height - 5,
            page=self.page,
            row=self.row,
        )

    def render(self) -> RenderableType:
        """Render the widget.

        Returns:
            RenderableType: Object to be rendered
        """

        if self.renderable is not None:
            self.page = self.renderable.page
            self.row = self.renderable.row

        self.render_table()
        assert isinstance(self.renderable, SecretsTableRenderable)
        return Panel(
            renderable=self.renderable,
            title=f"[{styles.GREY}]( {self.renderable.title} )[/]",
            border_style=Style(
                color=styles.LIGHT_PURPLE if self.has_focus else styles.PURPLE
            ),
            expand=True,
            box=styles.BOX,
        )
