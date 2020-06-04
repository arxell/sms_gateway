from typing import Optional

from pydantic import AnyUrl, BaseSettings, Field


class StreamTelecomSettings(BaseSettings):
    host: str = Field('http://gateway.api.sc', env='STREAM_TELECOM_API_HOST')
    port: int = Field(80, env='STREAM_TELECOM_API_PORT')
    timeout: int = Field(3, env='STREAM_TELECOM_API_TIMEOUT')
    username: str = Field('SMS Info', env='STREAM_TELECOM_API_USERNAME')
    login: str = Field('79636351616', env='STREAM_TELECOM_API_LOGIN')
    password: str = Field('oCcOwbecOK', env='STREAM_TELECOM_API_PASSWORD')


class SmscSettings(BaseSettings):
    host: str = Field('http://smsc.ru', env='SMSC_API_HOST')
    port: int = Field(80, env='SMSC_API_PORT')
    timeout: int = Field(3, env='SMSC_API_TIMEOUT')
    login: str = Field('arxell', env='SMSC_API_LOGIN')
    password: str = Field('a56f8fee-a978-419f-87c2-91cbfc084a4d', env='SMSC_API_PASSWORD')


class IQSmsSettings(BaseSettings):
    host: str = Field('http://api.iqsms.ru', env='IQSMS_API_HOST')
    port: int = Field(80, env='IQSMS_API_PORT')
    timeout: int = Field(3, env='IQSMS_API_TIMEOUT')
    login: str = Field('z1591267756939', env='IQSMS_API_LOGIN')
    password: str = Field('130994', env='IQSMS_API_PASSWORD')


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

    # stream_telecom
    stream_telecom: StreamTelecomSettings = StreamTelecomSettings()
    smsc: SmscSettings = SmscSettings()
    iqsms: IQSmsSettings = IQSmsSettings()

    class Config:
        env_prefix = ''
        allow_mutation = False


settings = Settings()
