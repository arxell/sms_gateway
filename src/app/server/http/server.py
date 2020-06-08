import logging

import uvicorn
from fastapi import FastAPI

from app.conf.logging import _get_configure_logging
from app.conf.settings import settings
from app.server.http.handler.auth.router import router as auth_router
from app.server.http.handler.maintenance import router as maintenance_router
from app.server.http.handler.sms import router as sms_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_debug_http_server() -> uvicorn.Server:
    app = FastAPI()
    config = uvicorn.Config(
        app, host=settings.debug_http_host, port=settings.debug_http_port, log_config=_get_configure_logging()
    )
    fastapi_server = uvicorn.Server(config=config)

    app.include_router(maintenance_router, tags=["Maintenance"])
    app.include_router(sms_router, tags=["SMS"])
    app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

    # skip uvicorn signals handling
    do_nothing = lambda *args: None
    fastapi_server.install_signal_handlers = do_nothing

    return fastapi_server
