from typing import Any, Dict, Optional

from tartiflette.utils.errors import to_graphql_error

from .constants import OperationMessageType

__all__ = (
    "send_message",
    "send_error",
    "send_execution_result",
    "send_error_as_execution_result",
)


async def send_message(
    connection_context: "ConnectionContext",
    operation_type: "OperationMessageType",
    operation_id: Optional[str] = None,
    payload: Optional[Any] = None,
) -> None:
    """
    TODO:
    :param connection_context: TODO:
    :param operation_type: TODO:
    :param operation_id: TODO:
    :param payload: TODO:
    :type connection_context: TODO:
    :type operation_type: TODO:
    :type operation_id: TODO:
    :type payload: TODO:
    """
    message = {"type": operation_type.value}
    if operation_id is not None:
        message["id"] = operation_id
    if payload is not None:
        message["payload"] = payload
    await connection_context.send(message)


async def send_error(
    connection_context: "ConnectionContext",
    error: Exception,
    error_type: Optional["OperationMessageType"] = None,
    operation_id: Optional[str] = None,
) -> None:
    """
    TODO:
    :param connection_context: TODO:
    :param error: TODO:
    :param error_type: TODO:
    :param operation_id: TODO:
    :type connection_context: TODO:
    :type error: TODO:
    :type error_type: TODO:
    :type operation_id: TODO:
    """
    await send_message(
        connection_context,
        error_type if error_type is not None else OperationMessageType.ERROR,
        operation_id=operation_id,
        payload={"message": str(error)},
    )


async def send_execution_result(
    connection_context: "ConnectionContext",
    operation_id: Optional[str],
    execution_result: Dict[str, Any],
) -> None:
    """
    TODO:
    :param connection_context: TODO:
    :param operation_id: TODO:
    :param execution_result: TODO:
    :type connection_context: TODO:
    :type operation_id: TODO:
    :type execution_result: TODO:
    """
    await send_message(
        connection_context,
        OperationMessageType.DATA,
        operation_id=operation_id,
        payload=execution_result,
    )


async def send_error_as_execution_result(
    connection_context: "ConnectionContext",
    operation_id: Optional[str],
    error: Exception,
) -> None:
    """
    TODO:
    :param connection_context: TODO:
    :param operation_id: TODO:
    :param error: TODO:
    :type connection_context: TODO:
    :type operation_id: TODO:
    :type error: TODO:
    """
    await send_execution_result(
        connection_context,
        operation_id,
        {"data": None, "errors": [to_graphql_error(error).coerce_value()]},
    )
