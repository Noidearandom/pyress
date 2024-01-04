from dataclasses import dataclass, field
from typing import Type

import requests
from bs4 import BeautifulSoup


@dataclass
class Entry:
    """RSS feed entry"""

    index: int
    title: str
    link: str
    guid: str
    description: str
    pubdate: str
    read: bool = False


@dataclass
class Feed:
    """RSS feed.
    Each RSS link is described by this class"""

    index: str
    title: str
    link: str
    ttl: int = 600
    entries: list[Type[Entry]] = field(default_factory=list)

    def _set_soup(self) -> None:
        self._soup = BeautifulSoup(self._response, features="xml")

    def _set_title(self) -> None:
        header = self._soup.find("channel")
        if header:
            self.title = header.title.text

    def _set_entries(self) -> None:
        index = 0
        for tag in self._soup.find_all("item"):
            entry = Entry(
                index=index,
                title=tag.title.string,
                link=tag.link.string,
                guid=tag.guid.string,
                description=tag.description.string,
                pubdate=tag.pubDate.string,
                read=False,
            )
            self.entries.append(entry)
            index += 1

    def _set_ttl(self) -> None:
        header = self._soup.find("channel")
        if header and header.ttl.text:
            self.ttl = int(header.ttl.text)

    def __post_init__(self):
        self._response = requests.get(self.link, timeout=30).text
        self._set_soup()
        self._set_title()
        self._set_entries()
