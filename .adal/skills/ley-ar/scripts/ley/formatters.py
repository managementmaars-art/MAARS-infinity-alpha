from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()


def print_json(results: list[dict[str, Any]]) -> None:
    console.print_json(json.dumps(results, ensure_ascii=False))


def print_table(results: list[dict[str, Any]]) -> None:
    if not results:
        console.print("[yellow]Sin resultados.[/yellow]")
        return
    table = Table(title="Resultados ley-ar")
    table.add_column("DB", style="cyan", no_wrap=True)
    table.add_column("ID", style="magenta")
    table.add_column("Título")
    table.add_column("Fecha", style="green")
    table.add_column("Snippet")
    for r in results:
        table.add_row(
            str(r.get("db", "")),
            str(r.get("id", "")),
            str(r.get("title", ""))[:80],
            str(r.get("date", "")),
            str(r.get("snippet", ""))[:120],
        )
    console.print(table)


def print_text(results: list[dict[str, Any]]) -> None:
    if not results:
        console.print("Sin resultados.")
        return
    for i, r in enumerate(results, 1):
        console.print(f"[{i}] ({r.get('db')}) {r.get('title')}\n    id={r.get('id')} fecha={r.get('date')}\n    {r.get('snippet')}\n    {r.get('url')}\n")
