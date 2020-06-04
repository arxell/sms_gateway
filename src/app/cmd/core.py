import click

from app.conf.logging import configure_logging
from app.conf.sentry import configure_sentry


@click.group()
def cli() -> None:
    configure_logging()
    configure_sentry()
