import asyncio

from typing import Callable

from aiohttp import web

from .actions import on_close, on_message
from .connection_context import ConnectionContext
from .constants import GRAPHQL_WS_PROTOCOL
from .exceptions import WSConnectionClosed

__all__ = ("graphql_ws_handler",)


async def handle(connection_context: "ConnectionContext") -> None:
    """
    TODO:
    :param connection_context: TODO:
    :type connection_context: TODO:
    """
    while True:
        try:
            message = await connection_context.receive()
        except WSConnectionClosed:
            break
        else:
            connection_context.tasks.add(
                asyncio.ensure_future(on_message(connection_context, message))
            )
        finally:
            _, connection_context.tasks = await asyncio.wait(
                connection_context.tasks, timeout=0
            )
            print("-> handle.finally", len(connection_context.tasks))
    await on_close(connection_context)


async def graphql_ws_handler(
    request: "aiohttp.web.Request", context_factory: Callable
) -> "aiohttp.web.WebSocketResponse":
    """
    TODO:
    :param request: TODO:
    :type request: TODO:
    :param context_factory: TODO:
    :type context_factory: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    websocket = web.WebSocketResponse(protocols=(GRAPHQL_WS_PROTOCOL,))
    request.app["websockets"].add(websocket)
    await websocket.prepare(request)
    try:
        connection_context = ConnectionContext(
            websocket,
            request.app["ttftt_engine"],
            await context_factory(request),
        )
        await asyncio.shield(handle(connection_context))
    except Exception as e:
        print("-> graphql_ws_handler.except", type(e))
    finally:
        print("-> graphql_ws_handler.finally")
        if not websocket.closed:
            await websocket.close()
        request.app["websockets"].discard(websocket)
    return websocket
