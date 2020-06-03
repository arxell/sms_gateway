import logging

import uvicorn
from grpclib.server import Server

from app.conf.settings import settings
from app.grpc_server.server import get_grpc_server
from app.http_server.server import get_debug_http_server

logger = logging.getLogger(__name__)


class AppRegistry:
    def __init__(self) -> None:
        self.grpc_server: Server = get_grpc_server()
        self.debug_http_server: uvicorn.Server = get_debug_http_server()

    # public
    async def run_grpc_server(self) -> None:
        await self._run_grpc_server(self.grpc_server, settings.grpc_host, settings.grpc_port)

    async def run_debug_http_server(self) -> None:
        await self._run_http_server(self.debug_http_server, settings.debug_http_host, settings.debug_http_port)

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
