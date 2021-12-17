import os

from whoosh.fields import TEXT, Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

from .config import INDEX_DIR


def index(nodes: list[str]):

    schema = Schema(title=TEXT(stored=True), content=TEXT)

    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)

    ix = create_in(INDEX_DIR, schema)
    writer = ix.writer()

    for word in nodes:
        writer.add_document(title=word, content=word)

    writer.commit()


def search(query_string, top=5) -> list[str]:
    ix = open_dir(INDEX_DIR)

    with ix.searcher() as s:
        query = QueryParser("content", ix.schema).parse(query_string)
        results = s.search(query, limit=top)

        return [x["title"] for x in results]
