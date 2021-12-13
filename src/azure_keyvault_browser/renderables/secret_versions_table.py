from __future__ import annotations

from azure.keyvault.secrets import SecretProperties
from rich.table import Table

from .. import styles
from .paginated_table import PaginatedTableRenderable


class SecretVersionsTableRenderable(PaginatedTableRenderable):
    """A secret versions table renderable."""

    def __init__(
        self,
        items: list[SecretProperties],
        title: str,
        page_size: int = -1,
        page: int = 1,
        row: int = 0,
    ) -> None:
        """A renderable that displays build history.

        Args:
            items (list[str]): A list of items to display.
            title (str): Title of the table.
            page_size (int): The size of the page before pagination happens. Defaults to -1.
            page (int): The starting page. Defaults to 1.
            row (int): The starting row. Defaults to 0.
        """

        self.items = items
        self.title = title

        super().__init__(
            len(items), page_size=page_size, page=page, row=row, row_size=1
        )

    def renderables(self, start_index: int, end_index: int) -> list[SecretProperties]:
        """Generate a list of renderables.

        Args:
            start_index (int): The starting index.
            end_index (int): The ending index.

        Returns:
            list[str]: A list of renderables.
        """

        return self.items[start_index:end_index]

    def render_rows(self, table: Table, renderables: list[SecretProperties]) -> None:
        """Renders rows for the table.

        Args:
            table (Table): The table to render rows for.
            renderables (list[str): The renderables to render.
        """

        for item in renderables:
            version = item.version

            created_on = item.created_on.strftime("%Y-%m-%d %H:%M:%S")

            table.add_row(version, created_on)

    def render_columns(self, table: Table) -> None:
        """Renders columns for the table.

        Args:
            table (Table): The table to render columns for.
        """

        table.add_column(
            "version", header_style=f"{styles.GREY} bold", no_wrap=True, ratio=40
        )
        table.add_column("created on", header_style=f"{styles.GREY} bold", no_wrap=True)
