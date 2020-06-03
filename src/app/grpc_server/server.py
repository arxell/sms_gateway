from grpclib.server import Server

from app.grpc_server.handler.sms_service import SMSService


def get_grpc_server() -> Server:
    return Server([SMSService()])
