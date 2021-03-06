from enum import Enum, unique


@unique
class Status(str, Enum):
    OK = 'OK'
    ERROR = 'ERROR'


@unique
class TokenType(str, Enum):
    REFRESH = 'refresh'
    ACCESS = 'access'


@unique
class SmsProvider(str, Enum):
    IQSMS = 'IQSMS'
    STREAM_TELECOM = 'STREAM_TELECOM'
    SMSC = 'SMSC'
