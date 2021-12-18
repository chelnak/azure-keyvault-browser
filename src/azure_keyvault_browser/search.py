from __future__ import annotations

import os

from whoosh.fields import TEXT, Schema
from whoosh.index import FileIndex, create_in
from whoosh.qparser import QueryParser

from .config import INDEX_DIR


class NoIndexException(Exception):
    """Exception raised when no index is found."""
    pass


class Search(object):
    """A wrapper class for Whoosh."""

    def __init__(self):
        self.__index: FileIndex | None = None
        self.__schema: Schema = Schema(title=TEXT(stored=True), content=TEXT)

    @property
    def schema(self) -> Schema:
        """Schema for the index.

        Returns:
            Schema: The configured schema.
        """

        return self.__schema

    @property
    def index(self) -> FileIndex:
        """Index for the search instance.

        Returns:
            FileIndex: The configured index.
        """

        return self.__index

    @index.setter
    def index(self, nodes: list[str]) -> None:
        """Index the nodes.

        Args:
            nodes (list[str]): A list of nodes to index.
        """

        if not os.path.exists(INDEX_DIR):
            os.mkdir(INDEX_DIR)

        self.__index = create_in(INDEX_DIR, self.schema)

        with self.__index.writer() as w:
            for word in nodes:
                w.add_document(title=word, content=word)

    def search(self, query_string: str, top: int = 5) -> list[str]:
        """Search for a query string.

        Args:
            query_string (str): The query string to search for.
            top (int): The number of results to return. Defaults to 5.

        Returns:
            list[str]: The results of the search.

        Raises:
            NoIndexException: If the index is not set.
        """

        if not self.index:
            raise NoIndexException("Index found. Ensure that you have indexed your nodes.")

        with self.index.searcher() as s:
            query = QueryParser("content", self.index.schema).parse(query_string)
            results = s.search(query, limit=top)

            return [x["title"] for x in results]
