from __future__ import annotations

import os

from whoosh.analysis import NgramWordAnalyzer
from whoosh.fields import TEXT, Schema
from whoosh.index import FileIndex, create_in
from whoosh.qparser import QueryParser

from .config import INDEX_DIR


class NoSchemaException(Exception):
    """Exception raised when no schema is found."""

    pass


class NoIndexException(Exception):
    """Exception raised when no index is found."""

    pass


class Search(object):
    """A wrapper class for Whoosh."""

    def __init__(self):
        self.__index: FileIndex | None = None
        self.__schema: Schema | None = None

    @property
    def schema(self) -> Schema:
        """Schema for the index.

        Returns:
            Schema: The configured schema.
        """

        return self.__schema

    def build_schema(self) -> None:
        """Build the schema for the index."""

        analyzer = NgramWordAnalyzer(minsize=2, maxsize=50)
        title = TEXT(analyzer=analyzer, phrase=False, stored=True)
        content = TEXT(phrase=False, stored=True)
        self.__schema = Schema(title=title, content=content)

    @property
    def index(self) -> FileIndex | None:
        """Index for the search instance.

        Returns:
            FileIndex: The configured index.
        """

        return self.__index

    @index.setter
    def index(self, nodes: list[str]) -> None:
        """Index the nodes. This will overwrite the existing index.

        Args:
            nodes (list[str]): A list of nodes to index.
        """

        if not os.path.exists(INDEX_DIR):
            os.mkdir(INDEX_DIR)

        self.build_schema()

        self.__index = create_in(INDEX_DIR, self.schema)

        with self.__index.writer() as w:
            for word in nodes:
                w.add_document(title=word, content=word)

    def search(self, query_string: str, top: int | None = None) -> list[str]:
        """Search for a query string.

        Args:
            query_string (str): The query string to search for.
            top (int): The number of results to return. Defaults to 5.

        Returns:
            list[str]: The results of the search.

        Raises:
            NoIndexException: If the index is not set.
        """

        if not self.__index:
            raise NoIndexException(
                "Index found. Ensure that you have indexed your nodes."
            )

        query_parser = QueryParser("title", self.__index.schema)
        query = query_parser.parse(query_string)

        with self.__index.searcher() as s:
            results = s.search(query, limit=top)
            return [x["title"] for x in results]
