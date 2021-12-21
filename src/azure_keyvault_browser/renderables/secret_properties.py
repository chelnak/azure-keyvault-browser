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
                "created on": properties.content_type,
                "updated on": format_datetime(properties.updated_on)
                if properties.updated_on
                else None,
                "expires on": format_datetime(properties.expires_on)
                if properties.expires_on
                else None,
                "not before": format_datetime(properties.not_before)
                if properties.not_before
                else None,
                "content type": properties.content_type,
                "enabled": properties.enabled,
                "key id": properties.key_id,
                "recoverable days": properties.recoverable_days,
                "recovery level": properties.recovery_level,
                "tags": properties.tags,
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
