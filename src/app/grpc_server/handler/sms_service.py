import logging

from grpclib.server import Stream

from app.protos.sms.sms_grpc import SmsBase
from app.protos.sms.sms_pb2 import SmsRequest, SmsResponse
from app.sms.client import sms_client

logger = logging.getLogger(__name__)


class SMSService(SmsBase):
    async def Send(self, stream: Stream[SmsResponse, SmsResponse]) -> None:
        request: SmsRequest = await stream.recv_message()
        logger.info(request)
        code = await sms_client.send(request.phone, request.text)
        await stream.send_message(SmsResponse(code=code))
