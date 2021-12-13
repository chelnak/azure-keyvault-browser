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
from ..renderables import SecretVersionsTableRenderable


class SecretVersionsWidget(Widget):
    """A secret versions widget. Used to display versions of a secret."""

    has_focus: Reactive[bool] = Reactive(False)

    page: int = 1
    row: int = 0

    def __init__(self) -> None:
        """A secret versions widget. Used to display versions of a secret."""

        name = self.__class__.__name__
        super().__init__(name=name)
        self.versions: list[SecretProperties] = []
        self.version_map: dict[str, SecretProperties] = {}
        self.renderable: SecretVersionsTableRenderable | None = None
        self.reveal: bool
        self.client: KeyVault = self.app.client

    def on_focus(self) -> None:
        """Sets has_focus to true when the item is clicked."""

        self.has_focus = True

    def on_blur(self) -> None:
        """Sets has_focus to false when an item no longer has focus."""

        self.has_focus = False

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        watch(self.app, "selected_secret", self.update)

    async def clear(self) -> None:
        """Clears the widget."""

        self.versions = []
        self.renderable = None
        self.refresh(layout=True)

    async def update(self, secret_name: str) -> None:
        """Updates the widget with new job info.

        Args:
            secret_name (str): The secret name.
        """

        if secret_name:
            self.versions = await self.client.get_secret_versions(secret_name)
            self.version_map = {v.version: v for v in self.versions}
            await self.app.set_focus(self)

        self.refresh(layout=True)

    def on_key(self, event: events.Key) -> None:
        """Handle a key press.

        Args:
            event (events.Key): The event containing the pressed key.
        """

        if self.renderable is None or len(self.versions) == 0:
            return

        key = event.key
        if key == Keys.Enter:
            row = self.renderable.get_cell_value(0, self.row)
            self.app.selected_version = self.version_map[str(row)]

        elif key == Keys.Left:
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
        """Render the table."""

        self.renderable = SecretVersionsTableRenderable(
            items=self.versions or [],
            title="versions",
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
        assert isinstance(self.renderable, SecretVersionsTableRenderable)
        return Panel(
            renderable=self.renderable,
            title=f"[{styles.GREY}]( {self.renderable.title} )[/]",
            border_style=Style(
                color=styles.LIGHT_PURPLE if self.has_focus else styles.PURPLE
            ),
            expand=True,
            box=styles.BOX,
        )
