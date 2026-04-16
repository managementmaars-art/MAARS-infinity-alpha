from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, Static


class ReportExportApp(App):
    TITLE = "Local Report Export"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Button("Export report", id="export")
        yield Static("Nothing exported yet", id="status")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "export":
            self.action_export_report()

    def action_export_report(self) -> None:
        output = Path("report.csv")
        output.write_text("name,value\nalpha,1\nbeta,2\n", encoding="utf-8")
        self.query_one("#status", Static).update(f"Wrote {output.resolve()}")


if __name__ == "__main__":
    ReportExportApp().run()
