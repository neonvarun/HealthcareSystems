"""Console script for care_odoo."""

import typer
from rich.console import Console

from care_odoo import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for care_odoo."""
    console.print("Replace this message by putting your code into "
               "care_odoo.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
