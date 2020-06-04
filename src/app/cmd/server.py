import asyncio
import logging
import signal

from app.registry import AppRegistry

from .core import cli

logger = logging.getLogger(__name__)


async def shutdown(signal: signal.Signals, app_registry: AppRegistry, loop: asyncio.AbstractEventLoop) -> None:
    """Cleanup tasks tied to the service's shutdown."""
    logger.info(f'Received exit signal {signal.name}...')
    logger.info("=========Shutdown=========")

    await app_registry.shutdown(signal)

    logger.info('Try to stop event loop')
    loop.stop()


@cli.command()
def run_server() -> None:

    # init loop
    loop = asyncio.get_event_loop()

    # init app
    app_registry = AppRegistry()

    # May want to catch other signals too
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s, app_registry, loop)))

    # init asyncio tasks
    tasks = [app_registry.run_grpc_server(), app_registry.run_debug_http_server(), app_registry.setup_db()]
    try:
        logger.info('=========Start=========')
        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION))
    except Exception as exp:
        logger.exception(exp)
    finally:
        logger.info('=========Exit=========')
        loop.close()
        logging.info("=========SuccessfullyExit=========")


@cli.command()
def check_server() -> None:
    # init app
    AppRegistry()
