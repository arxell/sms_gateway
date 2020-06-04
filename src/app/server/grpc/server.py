from grpclib.server import Server

from app.server.grpc.handler.sms_service import SMSService


def get_grpc_server() -> Server:
    return Server([SMSService()])
