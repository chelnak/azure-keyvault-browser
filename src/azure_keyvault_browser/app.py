from __future__ import annotations

from itertools import cycle
from typing import Any, MutableMapping

import click
from azure.keyvault.secrets import SecretProperties
from click import Path
from textual.app import App
from textual.keys import Keys
from textual.reactive import Reactive
from textual.widget import Widget

from . import __version__
from .azure import KeyVault
from .config import CLI_HELP, get_config
from .widgets import (
    FilterWidget,
    FlashWidget,
    HeaderWidget,
    HelpWidget,
    SecretPropertiesWidget,
    SecretsWidget,
    SecretVersionsWidget,
    ShowFlashNotification,
)


class KeyVaultBrowser(App):

    config_path: str | None = None
    config: MutableMapping[str, Any]
    client: KeyVault
    reveal_secret_value: Reactive[bool] = Reactive(False)
    show_help: Reactive[bool] = Reactive(False)
    selected_version: Reactive[SecretProperties] = Reactive(None)
    selected_secret: Reactive[str] = Reactive("")
    searchable_nodes: Reactive[list[SecretProperties]] = Reactive([])
    search_result: Reactive[list[str]] = Reactive([])
    widget_list: cycle[Widget] = cycle([])

    async def on_load(self) -> None:
        """Overrides on_load from App()"""

        self.config = get_config(self.config_path)
        keyvault = self.config["keyvault"]
        self.client = KeyVault(vault_name=keyvault)

        await self.bind("?", "toggle_help", "show help")
        await self.bind("ctrl+i", "cycle_widget", show=False)
        await self.bind(Keys.Escape, "refocus", show=False)
        await self.bind(Keys.ControlK, "toggle_search", show=False)

    async def on_mount(self) -> None:
        """Overrides on_mount from App()"""

        await self.view.dock(HeaderWidget(), size=7)

        self.search = FilterWidget()
        await self.view.dock(self.search, size=3)

        grid = await self.view.dock_grid()
        grid.add_column(name="secrets")
        grid.add_column(name="versions")
        grid.add_column(name="properties")
        grid.add_row(name="content")

        self.secrets = SecretsWidget()
        grid.place(self.secrets)

        self.versions = SecretVersionsWidget()
        grid.place(self.versions)

        self.properties = SecretPropertiesWidget()
        grid.place(self.properties)

        self.flash = FlashWidget()
        await self.view.dock(self.flash, edge="bottom", z=1)

        self.help = HelpWidget()
        await self.view.dock(self.help, z=1)

        self.widget_list = cycle(
            [self.search, self.secrets, self.versions, self.properties]
        )

        await self.app.set_focus(self.search)

    async def watch_show_help(self, show_help: bool) -> None:
        """Watch show_help and update widget visibility.

        Args:
            show_help (bool): Widget is shown if True and not shown if False.
        """
        self.help.visible = show_help

        if self.show_help:
            await self.app.set_focus(self.help)

        self.refresh(layout=True)

    async def action_toggle_help(self) -> None:
        """Toggle the help widget."""

        self.show_help = not self.show_help

    async def handle_show_flash_notification(
        self, message: ShowFlashNotification
    ) -> None:
        """Handle a ShowFlashNotification message.

        Args:
            message (ShowFlashNotification): The message to handle.
        """

        self.log("Handling ShowFlashNotification message")
        await self.flash.update_flash_message(value=message.value, type=message.type)

    async def action_cycle_widget(self) -> None:
        """Cycle through the widgets."""

        current_widget = next(self.widget_list)

        if current_widget.has_focus:
            current_widget = next(self.widget_list)

        await self.set_focus(current_widget)
        self.refresh(layout=True)

    async def action_refocus(self) -> None:
        """Refocus the app."""

        if self.search.has_focus:
            await self.versions.clear()
            await self.properties.clear()
            await self.search.clear()
        else:
            await self.set_focus(self.search)
            self.show_help = False


@click.command(help=CLI_HELP)
@click.option(
    "--config",
    default=None,
    envvar="AZURE_KEYVAULT_BROWSER_CONFIG",
    type=Path(file_okay=True, dir_okay=False, exists=False, resolve_path=True),
    help="Explicitly override the config that will be used by azure-keyvault-browser.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode.",
)
@click.version_option(__version__)
def run(config: str | None, debug: bool) -> None:
    """The entry point.

    Args:
        config (str | None): The config file to use.
        debug (bool): Enable debug mode.
    """

    title = "Azure Key Vault Browser"
    app = KeyVaultBrowser
    app.config_path = config
    if debug:
        app.run(log="azure-keyvault-browser.log", title=title)
    else:
        try:
            app.run()
        except Exception:
            from rich.console import Console

            console = Console()
            console.print(
                "💥 It looks like there has been an error. For more information use the --debug option!"
            )
