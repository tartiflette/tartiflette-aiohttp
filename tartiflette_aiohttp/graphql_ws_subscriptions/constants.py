from enum import Enum

__all__ = ("GRAPHQL_WS_PROTOCOL", "OperationMessageType")


GRAPHQL_WS_PROTOCOL = "graphql-ws"


class OperationMessageType(Enum):
    """
    TODO:
    """

    COMPLETE = "complete"
    CONNECTION_ACK = "connection_ack"
    CONNECTION_ERROR = "connection_error"
    CONNECTION_INIT = "connection_init"
    CONNECTION_KEEP_ALIVE = "ka"
    CONNECTION_TERMINATE = "connection_terminate"
    DATA = "data"
    ERROR = "error"
    START = "start"
    STOP = "stop"
