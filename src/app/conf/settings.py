from typing import Optional

from pydantic import AnyUrl, BaseSettings, Field


class Settings(BaseSettings):
    grpc_host: str = Field('127.0.0.1', env='GRPC_HOST')
    grpc_port: int = Field(50051, env='GRPC_PORT')

    http_host: str = Field('127.0.0.1', env='HTTP_HOST')
    http_port: int = Field(8081, env='HTTP_PORT')
    debug_http_host: str = Field('127.0.0.1', env='DEBUG_HTTP_HOST')
    debug_http_port: int = Field(8082, env='DEBUG_HTTP_PORT')

    kafka_topic_name: str = Field('gg.wsMessages', env='KAFKA_TOPIC_NAME')
    kafka_bootstrap_servers: str = Field('localhost:9092', env='KAFKA_BOOTSTRAP_SERVERS')

    environment_name: str = Field('unknown', env='ENVIRONMENT_NAME')
    sentry_dsn: Optional[AnyUrl] = Field(None, env='SENTRY_DSN')
    enable_json_logging: bool = Field(False, env='ENABLE_JSON_LOGGING')

    # version
    git_branch_name: str = Field('git_branch_name', env='GIT_BRANCH_NAME')
    bamboo_build_date: str = Field('bamboo_build_date', env='BAMBOO_BUILD_DATE')
    build_number: str = Field('build_number', env='BAMBOO_BUILD_NUMBER')
    git_short_hash: str = Field('git_short_hash', env='GIT_COMMIT_HASH')

    class Config:
        env_prefix = ''
        allow_mutation = False


settings = Settings()
