from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

import typer
from rich.console import Console

from ley import __version__
from ley.databases import DATABASES
from ley.formatters import print_json, print_table, print_text

app = typer.Typer(help="CLI para búsqueda jurídica argentina")
console = Console()


@app.command()
def search(
    query: str = typer.Argument(..., help="Consulta de búsqueda"),
    db: str = typer.Option("all", "--db", help="Bases: saij,juba,csjn,juscaba"),
    limit: int = typer.Option(10, "--limit", min=1, help="Máximo de resultados"),
    as_json: bool = typer.Option(False, "--json", help="Salida JSON"),
    text: bool = typer.Option(False, "--text", help="Salida texto plano"),
):
    dbs = list(DATABASES.keys()) if db == "all" else [d.strip().lower() for d in db.split(",") if d.strip()]
    invalid = [d for d in dbs if d not in DATABASES]
    if invalid:
        raise typer.BadParameter(f"Base(s) inválida(s): {', '.join(invalid)}")

    results = []
    errors = []
    with ThreadPoolExecutor(max_workers=len(dbs)) as ex:
        futures = {ex.submit(DATABASES[d], query, limit): d for d in dbs}
        for fut in as_completed(futures):
            d = futures[fut]
            try:
                results.extend(fut.result())
            except Exception as e:
                errors.append((d, str(e)))

    results = results[:limit] if db != "all" and len(dbs) == 1 else results

    if as_json:
        print_json(results)
    elif text:
        print_text(results)
    else:
        print_table(results)

    if errors:
        console.print("\n[red]Errores:[/red]")
        for d, err in errors:
            console.print(f"- {d}: {err}")


@app.command()
def status():
    console.print(f"ley-ar v{__version__}")
    console.print("Bases disponibles: " + ", ".join(DATABASES.keys()))


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Mostrar versión"),
):
    if version:
        console.print(__version__)
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()
