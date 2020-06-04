import asyncio
import logging
import signal

import uvicorn
from grpclib.server import Server

from app.conf.settings import settings
from app.database.base import close_db, init_db
from app.server.grpc.server import get_grpc_server
from app.server.http.server import get_debug_http_server

logger = logging.getLogger(__name__)


class AppRegistry:
    def __init__(self) -> None:
        self.grpc_server: Server = get_grpc_server()
        self.debug_http_server: uvicorn.Server = get_debug_http_server()

    # public
    async def setup_db(self) -> None:
        try:
            logger.info('[DB] Connection')
            await init_db()
        except Exception as e:
            logger.exception(e)
            raise e

    async def run_grpc_server(self) -> None:
        await self._run_grpc_server(self.grpc_server, settings.grpc_host, settings.grpc_port)

    async def run_debug_http_server(self) -> None:
        await self._run_http_server(self.debug_http_server, settings.debug_http_host, settings.debug_http_port)

    async def shutdown(self, signal: signal.Signals) -> None:
        logger.info('Try to stop db ...')
        await close_db()

        logger.info('Try to stop grpc_server ...')
        self.grpc_server.close()

        logger.info('Try to stop debug_http_server ...')
        self.debug_http_server.handle_exit(signal, None)
        # need to wait some time for gracefull shutdown uvicorn
        await asyncio.sleep(1)

    # internal
    async def _run_grpc_server(self, server: Server, host: str, port: int) -> None:
        try:
            await self.grpc_server.start(host, port)
            logger.info(f'[GRPC] Serving on {host}:{port}')
            await server.wait_closed()
        except Exception as e:
            logger.exception(e)
            raise e
        finally:
            logger.info(f'[GRPC] Stop')

    async def _run_http_server(self, server: uvicorn.Server, host: str, port: int) -> None:
        try:
            logger.info(f'[HTTP] Serving on {host}:{port}')
            await server.serve()
        except Exception as e:
            logger.exception(e)
            raise e
        finally:
            logger.info(f'[HTTP] Stop')
