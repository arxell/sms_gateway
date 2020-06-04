import logging

from grpclib.server import Stream

from app.domain.sms.service import SendSmsService
from app.server.grpc.protos.sms.sms_grpc import SmsBase
from app.server.grpc.protos.sms.sms_pb2 import SmsRequest, SmsResponse

logger = logging.getLogger(__name__)


class SMSService(SmsBase):
    async def Send(self, stream: Stream[SmsResponse, SmsResponse]) -> None:
        request: SmsRequest = await stream.recv_message()
        logger.info(request)
        code = await SendSmsService.send(request.phone, request.text)
        await stream.send_message(SmsResponse(code=code))
