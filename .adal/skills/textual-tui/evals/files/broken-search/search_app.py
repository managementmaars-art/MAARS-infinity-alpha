from __future__ import annotations

import time

from rich.table import Table
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, Static


FAKE_DOCS = [
    ("Guide", "Getting started with Textual"),
    ("Workers", "How to move slow work off the UI thread"),
    ("Screens", "Using screens and modes for navigation"),
    ("DataTable", "A better fit than a static Rich table for interactive results"),
    ("Testing", "Pilot and snapshot testing basics"),
]


class SearchApp(App):
    TITLE = "Broken Search"
    BINDINGS = [
        ("ctrl+f", "focus_search", "Search"),
        ("f1", "show_help", "Help"),
        ("f2", "toggle_theme", "Theme"),
        ("f3", "refresh_now", "Refresh"),
        ("f4", "export_report", "Export"),
        ("f5", "clear_search", "Clear"),
        ("f6", "show_about", "About"),
    ]
    CSS = """
    Screen {
        layout: vertical;
    }

    #search {
        margin: 1 2;
    }

    #results {
        margin: 1 2;
        height: 1fr;
        border: round green;
    }
    """

    query = reactive("")
    results = reactive(list)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Type to search docs", id="search")
        yield Static("No results yet", id="results")
        yield Footer()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.query = event.value
        time.sleep(0.5)
        lowered = event.value.lower()
        self.results = [
            (title, summary)
            for title, summary in FAKE_DOCS
            if lowered in title.lower() or lowered in summary.lower()
        ]
        self.refresh_results()

    def refresh_results(self) -> None:
        table = Table(title="Search results")
        table.add_column("Title")
        table.add_column("Summary")
        for title, summary in self.results:
            table.add_row(title, summary)
        self.query_one("#results", Static).update(table)

    def action_focus_search(self) -> None:
        self.query_one("#search", Input).focus()

    def action_show_help(self) -> None:
        self.notify("No help yet")

    def action_toggle_theme(self) -> None:
        self.notify("Theme toggle not implemented")

    def action_refresh_now(self) -> None:
        self.refresh_results()

    def action_export_report(self) -> None:
        self.notify("Export not implemented")

    def action_clear_search(self) -> None:
        self.query_one("#search", Input).value = ""
        self.results = []
        self.refresh_results()

    def action_show_about(self) -> None:
        self.notify("Broken Search demo")


if __name__ == "__main__":
    SearchApp().run()
