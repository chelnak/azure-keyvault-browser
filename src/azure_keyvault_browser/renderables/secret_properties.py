from __future__ import annotations

from azure.keyvault.secrets import SecretProperties
from rich.console import Console, ConsoleOptions, RenderResult
from rich.table import Table
from rich.text import Text

from .. import styles
from ..util import format_datetime


class SecretPropertiesRenderable:
    """A secret properties renderable"""

    def __init__(self, properties: SecretProperties | None, value: str) -> None:
        self.title = f"{properties.name} @ {properties.version}" if properties else ""
        self.properties = (
            {
                "created on": format_datetime(properties.created_on)
                if properties.created_on
                else "",
                "updated on": format_datetime(properties.updated_on)
                if properties.updated_on
                else "",
                "expires on": format_datetime(properties.expires_on)
                if properties.expires_on
                else "",
                "not before": format_datetime(properties.not_before)
                if properties.not_before
                else "",
                "content type": properties.content_type
                if properties.content_type
                else "",
                "enabled": properties.enabled if properties.enabled else "",
                "key id": properties.key_id if properties.key_id else "",
                "recoverable days": properties.recoverable_days
                if properties.recoverable_days
                else "",
                "recovery level": properties.recovery_level
                if properties.recovery_level
                else "",
                "tags": properties.tags if properties.tags else "",
            }
            if properties
            else None
        )
        self.value = value if value else ""

    def __str__(self) -> str:
        return str(self.properties)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:

        table = Table(box=None, expand=True, show_footer=False, show_header=False)
        table.add_column(style=styles.GREY, no_wrap=True)
        table.add_column(style=f"{styles.ORANGE} bold", no_wrap=True)

        if self.properties:

            table.title = Text(self.title, no_wrap=True, style=styles.GREEN)
            table.title_justify = "left"
            table.add_row()
            for property, value in self.properties.items():
                table.add_row(property, str(value))

            table.add_row("value", "🔒" if self.value == "" else "🔓")
            table.add_row()

        yield table
