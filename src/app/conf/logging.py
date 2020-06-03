import logging.config
from logging import Formatter, LogRecord
from typing import Any, Dict

from app.conf.settings import settings


class ExtraFormatter(Formatter):
    """
    небольшой хак, чтобы поддерать %(props)s в форметтере логов и для json и для обычного форматтера
    """

    def formatMessage(self, record: LogRecord) -> str:
        if not hasattr(record, 'props'):
            record.props = ''  # type: ignore[attr-defined]
        return super().formatMessage(record)


def _get_configure_logging() -> Dict[str, Any]:
    if settings.enable_json_logging:
        formatter = 'pythonjsonlogger.jsonlogger.JsonFormatter'
    else:
        formatter = 'app.conf.logging.ExtraFormatter'

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {'format': '%(asctime)s %(levelname)s %(name)s %(message)s %(props)s', 'class': formatter}
        },
        'handlers': {'default': {'class': 'logging.StreamHandler', 'formatter': 'default'}},
        'loggers': {'': {'handlers': ['default'], 'level': logging.INFO}},
    }


def configure_logging() -> None:
    logging.config.dictConfig(_get_configure_logging())
