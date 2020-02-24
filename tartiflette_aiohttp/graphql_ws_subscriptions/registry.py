import asyncio
import weakref

from functools import partial
from typing import Callable

from aiohttp import WSCloseCode

from .handler import graphql_ws_handler

__all__ = ("register_graphql_ws_subscriptions",)


async def close_websockets(app: "aiohttp.web.Application") -> None:
    """
    TODO:
    :param app: TODO:
    :type app: TODO:
    """
    websocket_closers = [
        websocket.close(
            code=WSCloseCode.GOING_AWAY, message="Server shutdown."
        )
        for websocket in app["websockets"] if not websocket.closed
    ]
    print("-> close_websockets", len(websocket_closers))
    if websocket_closers:
        await asyncio.wait(websocket_closers)


def register_graphql_ws_subscriptions(
    app: "aiohttp.web.Application",
    context_factory: Callable,
    subscription_ws_endpoint: str,
) -> None:
    """
    TODO:
    :param app: TODO:
    :param context_factory: TODO:
    :param subscription_ws_endpoint: TODO:
    :type app: TODO:
    :type context_factory: TODO:
    :type subscription_ws_endpoint: TODO:
    """
    app["websockets"] = weakref.WeakSet()
    app.router.add_get(
        subscription_ws_endpoint,
        partial(graphql_ws_handler, context_factory=context_factory),
    )
    app.on_shutdown.append(close_websockets)
