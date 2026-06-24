import typer

from macrodata_norway.pipelines.fred import backfill_fred, update_fred
from macrodata_norway.repository.series import list_series

app = typer.Typer(
    help="Macrodata Norway: local macroeconomic and financial data warehouse"
)


@app.command("list-series")
def list_series_command() -> None:
    """
    List all registered timeseries.
    """

    df = list_series()

    if df.empty:
        typer.echo("No series found")
        return

    typer.echo(df.to_string(index=False))


@app.command("backfill-fred")
def backfill_fred_command() -> None:
    """
    Fetch full available history for all configured FRED series.
    """

    summary = backfill_fred()
    typer.echo("FRED backfill complete.")
    typer.echo(f"Status: {summary['status']}")
    typer.echo(f"Rows fetched: {summary['rows_fetched']}")
    typer.echo(f"Rows inserted or updated: {summary['rows_changed']}")
    typer.echo(f"Rows skipped: {summary['rows_skipped']}")

    if summary["errors"]:
        typer.echo("")
        typer.echo("Errors:")
        for error in summary["errors"]:
            typer.echo(f"- {error}")


@app.command("update-fred")
def update_fred_command() -> None:
    """
    Incrementally update all configured FRED series.
    """
    summary = update_fred()

    typer.echo("FRED update complete.")
    typer.echo(f"Status: {summary['status']}")
    typer.echo(f"Rows fetched: {summary['rows_fetched']}")
    typer.echo(f"Rows inserted or updated: {summary['rows_changed']}")
    typer.echo(f"Rows skipped: {summary['rows_skipped']}")

    if summary["errors"]:
        typer.echo("")
        typer.echo("Errors:")
        for error in summary["errors"]:
            typer.echo(f"- {error}")


if __name__ == "__main__":
    app()
