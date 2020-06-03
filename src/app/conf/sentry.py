import logging
from typing import Any, Dict, Optional

import sentry_sdk
from sentry_sdk import HttpTransport
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.conf.settings import settings

logger = logging.getLogger(__name__)


class _Transport(HttpTransport):
    def __init__(self, options: Dict[str, Any]) -> None:
        super().__init__(options)

    def _get_pool_options(self, ca_certs: Optional[Any]) -> Dict[str, Any]:
        return {"num_pools": 2, "cert_reqs": 'CERT_NONE', "retries": False}


def configure_sentry() -> None:
    if settings.sentry_dsn:
        logger.info(f'Configure Sentry by {settings.sentry_dsn} for {settings.environment_name}')
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR,  # Capture info and above as breadcrumbs  # Send errors as events
        )
        sentry_sdk.init(
            environment=settings.environment_name,
            release=f'{settings.git_branch_name}-{settings.build_number}',
            dsn=settings.sentry_dsn,
            transport=_Transport,
            integrations=[AioHttpIntegration(), sentry_logging],
        )
