import logging

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.conf.settings import Settings, settings
from app.database.base import check_db_connection

from .datamodels import ReadyResponse, VersionResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get('/version', response_model=VersionResponse)
async def version() -> VersionResponse:
    return VersionResponse(
        build_date=settings.bamboo_build_date,
        build_number=settings.build_number,
        git_branch_name=settings.git_branch_name,
        git_short_hash=settings.git_short_hash,
        version=f'{settings.git_branch_name}-{settings.build_number}',
    )


@router.get('/alive', response_class=PlainTextResponse)
async def alive() -> PlainTextResponse:
    return PlainTextResponse('OK')


@router.get('/ready', response_model=ReadyResponse)
async def ready() -> ReadyResponse:
    is_postgres_ready, error = await check_db_connection()
    return ReadyResponse(
        is_ready=is_postgres_ready,
        checks=[ReadyResponse._ServiceCheck(service='postgres', is_ready=is_postgres_ready, error=error)],
    )


@router.get('/config', response_model=Settings)
async def config() -> Settings:
    return settings


@router.get('/error')
async def error() -> None:
    logger.error('test exception via logging')
    raise Exception('test exception via raise')
