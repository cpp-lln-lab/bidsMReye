"""Console script for bidsmreye."""
import sys

import click


@click.command()
def main(args=None):
    """Console script for bidsmreye."""
    click.echo("Replace this message by putting your code into " "bidsmreye.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
