#!/usr/bin/env python

"""
A simple RSS parser/aggregator

"""

import webbrowser
import logging
import sys
from typing import List


from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Label,
    ListItem,
    ListView,
    Placeholder,
    Footer,
    ContentSwitcher,
)

from config import Config
from feed import Feed


class Header(Placeholder):
    DEFAULT_CSS = """
    Header {
        height: 1;
        dock: top;
    }
    """


class FeedItem(ListItem):
    """New Widget based on ListItem to represent the Feeds"""

    def __init__(self, title: str, url: str, id: str | None) -> None:
        super().__init__(id=id)
        self.title = title
        self.url = url

    def compose(self) -> ComposeResult:
        yield Label(self.title)


class EntryItem(ListItem):
    """New Widget based on ListItem to represent the feeds entries"""

    def __init__(self, title: str, url: str, id: str | None) -> None:
        super().__init__(id=id)
        self.title = title
        self.url = url

    def compose(self) -> ComposeResult:
        yield Label(self.title)


class Pyress(App):
    """A textual RSS reader"""

    CSS_PATH = "pyress.tcss"
    BINDINGS = [("q", "quit_app", "Quit")]
    TITLE = "Pyress"

    config = None

    def compose(self) -> ComposeResult:
        """Create the widgets for the app"""

        yield Header("RSS reader")
        with Horizontal():
            with Vertical(id="listfeeds"):
                listitems = self.get_list_of_feeds_menu()
                yield ListView(*listitems)
            with ContentSwitcher():
                for feed in self.config.list_of_feeds:
                    with Vertical(id=f"{feed.index}", classes="entries"):
                        listentries = self.get_list_of_entries_menu(feed)
                        yield ListView(*listentries)
            yield Footer()

    def on_mount(self) -> None:
        try:
            self.query_one("#listfeeds").focus()
        except NoMatches:
            pass

    @on(ListView.Selected)
    def switch(self, event: ListView.Selected) -> None:
        self.notify(f"Opening feed {event.item.title}")
        if event.item.id and event.item.id.startswith("feed"):
            self.query_one(ContentSwitcher).current = event.item.id
        elif event.item.id and event.item.id.startswith("entry"):
            wblog = logging.getLogger("webbrowser")
            wblog.setLevel(level=logging.DEBUG)
            logging.disable(logging.CRITICAL)
            webbrowser.open(event.item.url)

    def on_list_item_selected(self, event: ListItem) -> None:
        self.notify(f"Opening item {event}")

    def action_quit_app(self) -> None:
        """Bind \"q\" to exiting the app"""
        self.exit(return_code=0)

    def load_config(self, config: Config) -> None:
        self.config = config

    def get_list_of_feeds_menu(self) -> List[ListItem]:
        """Builds the list of Feeds"""

        for link in self.config.list_of_links:
            feed = Feed(index=f"feed{hex(hash(link))}", title="", link=link)
            self.config.list_of_feeds.append(feed)
        return [
            FeedItem(title=f"{x.title}", url=f"{x.link}", id=f"{x.index}")
            for x in self.config.list_of_feeds
        ]

    def get_list_of_entries_menu(self, feed: Feed) -> List[ListItem]:
        """Builds the list of Feeds"""
        return [
            EntryItem(title=f"{x.title}", url=f"{x.guid}", id=f"entry{x.index}")
            for x in feed.entries
        ]

    def action_link(self, href: str) -> None:
        webbrowser.open(href)


def main():
    conf = Config(config_file="config.example")
    if not conf:
        print("Could not find any configuration file")
        sys.exit(1)
    conf.load()
    app = Pyress()
    app.load_config(conf)
    app.run()
    sys.exit(app.return_code or 0)


if __name__ == "__main__":
    main()
