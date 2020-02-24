import asyncio

from asyncio import CancelledError
from typing import Any, Dict, Optional

from aiohttp import WSCloseCode

from .constants import OperationMessageType
from .operation_message import parse_message
from .senders import (
    send_error,
    send_error_as_execution_result,
    send_execution_result,
    send_message,
)

__all__ = ("on_message", "on_close")

def extract_graphql_params(
    connection_context: "ConnectionContext", payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    TODO:
    :param connection_context: TODO:
    :param payload: TODO:
    :type connection_context: TODO:
    :type payload: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    return {
        "query": payload.get("query"),
        "variables": payload.get("variables"),
        "operation_name": payload.get("operationName"),
        "context": connection_context.context,
    }


async def unsubscribe(
    connection_context: "ConnectionContext", operation_id: str
) -> None:
    """
    TODO:
    :param connection_context: TODO:
    :param operation_id: TODO:
    :type connection_context: TODO:
    :type operation_id: TODO:
    """
    operation = connection_context.operations.get(operation_id)
    print("-> unsubscribe", bool(operation))
    if operation:
        await operation.aclose()
        print("*> unsubscribe", bool(operation))
        del connection_context.operations[operation_id]


async def on_connection_init(
    connection_context: "ConnectionContext",
    operation_message: "OperationMessage",
) -> None:
    """
    TODO:
    :param connection_context: TODO:
    :param operation_message: TODO:
    :type connection_context: TODO:
    :type operation_message: TODO:
    """
    try:
        await send_message(
            connection_context, OperationMessageType.CONNECTION_ACK
        )
    except Exception as e:
        await send_error(
            connection_context,
            e,
            error_type=OperationMessageType.CONNECTION_ERROR,
            operation_id=operation_message.id,
        )
        await connection_context.close(WSCloseCode.INTERNAL_ERROR)


async def on_start(
    connection_context: "ConnectionContext",
    operation_message: "OperationMessage",
) -> None:
    """
    TODO:
    :param connection_context: TODO:
    :param operation_message: TODO:
    :type connection_context: TODO:
    :type operation_message: TODO:
    """
    operation_id = operation_message.id
    print("-> on_start", connection_context.has_operation(operation_id))
    if connection_context.has_operation(operation_id):
        await unsubscribe(connection_context, operation_id)

    operation = await connection_context.graphql_engine.subscribe(
        **extract_graphql_params(connection_context, operation_message.payload)
    )

    connection_context.operations[operation_id] = operation

    try:
        async for result in operation:
            print(
                "*> on_start.async_iter",
                connection_context.has_operation(operation_id),
            )
            if not connection_context.has_operation(operation_id):
                break
            await send_execution_result(
                connection_context, operation_id, result
            )
        print("*> on_start.async_iter.end")
    except CancelledError:
        print("*> on_start.CancelledError")
        await send_error_as_execution_result(
            connection_context,
            operation_id,
            Exception("Internal server error."),
        )
    except Exception as e:
        print("*> on_start.Exception", type(e))
        await send_error_as_execution_result(
            connection_context, operation_id, e
        )

    print(
        "*> on_start.complete", connection_context.has_operation(operation_id)
    )
    if connection_context.has_operation(operation_id):
        await send_message(
            connection_context,
            OperationMessageType.COMPLETE,
            operation_id=operation_id,
        )

    await unsubscribe(connection_context, operation_id)


async def on_message(
    connection_context: "ConnectionContext", message: Optional[str]
) -> None:
    """
    TODO:
    :param connection_context: TODO:
    :param message: TODO:
    :type connection_context: TODO:
    :type message: TODO:
    """
    try:
        operation_message = parse_message(message)
    except Exception as e:
        await send_error(
            connection_context,
            e,
            error_type=OperationMessageType.CONNECTION_ERROR,
        )
        return

    operation_type = operation_message.type
    if operation_type is OperationMessageType.CONNECTION_INIT:
        await on_connection_init(connection_context, operation_message)
    elif operation_type is OperationMessageType.START:
        await on_start(connection_context, operation_message)
    elif operation_type is OperationMessageType.STOP:
        await unsubscribe(connection_context, operation_message.id)
    elif operation_type is OperationMessageType.CONNECTION_TERMINATE:
        await connection_context.close()
    else:
        await send_error(
            connection_context,
            TypeError(f"Invalid message type < {operation_message.type} >."),
            operation_id=operation_message.id,
        )


async def on_close(connection_context: "ConnectionContext") -> None:
    """
    TODO:
    :param connection_context: TODO:
    :type connection_context: TODO:
    """
    print(
        "-> on_close",
        len(connection_context.operations),
        len(connection_context.tasks),
    )
    if connection_context.operations:
        await asyncio.wait(
            [
                unsubscribe(connection_context, operation_id)
                for operation_id in list(connection_context.operations.keys())
            ],
        )

    # Trick to delay tasks cancellation to let async gens clean themselves
    await asyncio.sleep(0)

    for task in connection_context.tasks:
        task.cancel()
