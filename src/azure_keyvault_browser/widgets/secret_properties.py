from __future__ import annotations

import click
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from textual import events
from textual.keys import Keys
from textual.reactive import Reactive, watch
from textual.widget import Widget

from .. import styles
from ..azure import KeyVault, SecretProperties
from ..renderables import SecretPropertiesRenderable
from .flash import FlashMessageType, ShowFlashNotification


class SecretPropertiesWidget(Widget):
    """A secret properties widget. Used to display secret properties."""

    has_focus: Reactive[bool] = Reactive(False)

    def __init__(self) -> None:
        """A secret properties widget. Used to display secret properties."""

        name = self.__class__.__name__
        super().__init__(name=name)
        self.selected_version: SecretProperties | None = None
        self.renderable: SecretPropertiesRenderable | None = None
        self.value: str = ""
        self.reveal_secret_value: bool = False
        self.client: KeyVault = self.app.client

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        watch(self.app, "selected_version", self.update)

    def on_focus(self) -> None:
        """Sets has_focus to true when the item is clicked."""

        self.has_focus = True

    def on_blur(self) -> None:
        """Sets has_focus to false when an item no longer has focus."""

        self.has_focus = False
        self.reveal_secret_value = False

    async def clear(self) -> None:
        """Clears the widget."""

        self.selected_version = None
        self.renderable = None
        self.refresh(layout=True)

    async def update(self, selected_version: SecretProperties) -> None:
        """Updates the widget with new secret properties.

        Args:
            selected_version (SecretProperties): A secret properties object.
        """

        if selected_version:
            self.selected_version = selected_version
            self.value = await self.client.get_secret_value(
                self.selected_version.name, selected_version.version
            )
            await self.app.set_focus(self)

        self.refresh(layout=True)

    def on_key(self, event: events.Key) -> None:
        """Handle a key press.

        Args:
            event (events.Key): The event containing the pressed key.
        """

        if self.renderable is None or self.selected_version is None:
            return

        key = event.key

        if key == Keys.ControlS:
            self.reveal_secret_value = not self.reveal_secret_value

        elif key == Keys.ControlK:

            if self.reveal_secret_value:

                try:
                    driver = self.app._driver
                    driver.exit_event.set()
                    click.edit(self.value)
                except Exception as e:
                    self.log(f"Failed to open editor value: {e}")
                    self.post_message_from_child_no_wait(
                        ShowFlashNotification(
                            self,
                            value="Unable to open editor. Please check your editor settings.",
                            type=FlashMessageType.ERROR,
                        )
                    )
                finally:
                    driver.exit_event.clear()
                    driver.start_application_mode()

        self.refresh(layout=True)

    def render_table(self) -> None:
        """Renders the table."""

        self.renderable = SecretPropertiesRenderable(
            properties=self.selected_version,
            value=self.value if self.reveal_secret_value else "",
        )

    def render(self) -> RenderableType:
        """Render the widget.

        Returns:
            RenderableType: Object to be rendered
        """

        self.render_table()
        assert isinstance(self.renderable, SecretPropertiesRenderable)
        return Panel(
            renderable=self.renderable,
            title=f"[{styles.GREY}]( properties )[/]",
            border_style=Style(
                color=styles.LIGHT_PURPLE if self.has_focus else styles.PURPLE
            ),
            expand=True,
            box=styles.BOX,
        )
