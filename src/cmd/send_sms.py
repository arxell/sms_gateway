import asyncio
import logging

from app.sms.client import sms_client

from .core import cli

logger = logging.getLogger(__name__)


@cli.command()
def send_sms() -> None:

    # init loop
    loop = asyncio.get_event_loop()

    # init asyncio tasks
    tasks = [sms_client.send('79636351616', '123')]
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except Exception as exp:
        logger.exception(exp)
    finally:
        loop.close()
