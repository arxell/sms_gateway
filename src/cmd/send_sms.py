import asyncio
import logging

from app.domain.sms.service import SendSmsService

from .core import cli

logger = logging.getLogger(__name__)


@cli.command()
def send_sms() -> None:
    # init loop
    loop = asyncio.get_event_loop()

    # init asyncio tasks
    tasks = [SendSmsService.send('79636351616', '123')]
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except Exception as exp:
        logger.exception(exp)
    finally:
        loop.close()
