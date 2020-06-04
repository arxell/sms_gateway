from enum import Enum, unique


@unique
class SmsProvider(str, Enum):
    IQSMS = 'IQSMS'
    STREAM_TELECOM = 'STREAM_TELECOM'
    SMSC = 'SMSC'
