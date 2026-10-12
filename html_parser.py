from __future__ import annotations

import json
from html.parser import HTMLParser
from typing import Any


class _HtmlResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: list[str] = []
        self.text: list[str] = []
        self.links: list[dict[str, str]] = []
        self.tables: list[list[list[str]]] = []
        self.json_ld: list[Any] = []
        self._current_link: dict[str, str] | None = None
        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._cell_text: list[str] | None = None
        self._in_title = False
        self._in_json_ld = False
        self._script_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "a":
            self._current_link = {"text": "", "href": attributes.get("href", "")}
        elif tag == "table":
            self._current_table = []
        elif tag == "tr" and self._current_table is not None:
            self._current_row = []
        elif tag in {"th", "td"} and self._current_row is not None:
            self._cell_text = []
        elif tag == "script" and attributes.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._script_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "a" and self._current_link is not None:
            self.links.append(self._current_link)
            self._current_link = None
        elif tag in {"th", "td"} and self._cell_text is not None and self._current_row is not None:
            self._current_row.append(" ".join("".join(self._cell_text).split()))
            self._cell_text = None
        elif tag == "tr" and self._current_row is not None and self._current_table is not None:
            self._current_table.append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._current_table is not None:
            self.tables.append(self._current_table)
            self._current_table = None
        elif tag == "script" and self._in_json_ld:
            try:
                self.json_ld.append(json.loads("".join(self._script_text)))
            except json.JSONDecodeError:
                pass
            self._in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title.append(data)
        if self._in_json_ld:
            self._script_text.append(data)
        elif self._cell_text is not None:
            self._cell_text.append(data)
        elif self._current_link is not None:
            self._current_link["text"] += data
        else:
            self.text.append(data)


def parse_html(html: str) -> dict[str, Any]:
    """Convert common HTML result structures into JSON-serializable data."""

    parser = _HtmlResultParser()
    parser.feed(html)
    return {
        "title": " ".join("".join(parser.title).split()),
        "text": " ".join("".join(parser.text).split()),
        "links": [
            {"text": " ".join(link["text"].split()), "href": link["href"]}
            for link in parser.links
        ],
        "tables": parser.tables,
        "json_ld": parser.json_ld,
    }
