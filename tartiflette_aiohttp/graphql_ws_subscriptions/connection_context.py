from typing import Any, AsyncIterator, Dict, Set, Optional

from aiohttp import WSMsgType

from .exceptions import WSConnectionClosed

__all__ = ("ConnectionContext",)


class ConnectionContext:
    """
    TODO:
    """

    __slots__ = (
        "websocket",
        "graphql_engine",
        "context",
        "tasks",
        "operations",
    )

    def __init__(
        self,
        websocket: "aiohttp.web.WebSocketResponse",
        graphql_engine: "TartifletteEngine",
        context: Dict[str, Any],
    ) -> None:
        """
        TODO:
        :param websocket: TODO:
        :param graphql_engine: TODO:
        :param context: TODO:
        :type websocket: TODO:
        :type graphql_engine: TODO:
        :type context: TODO:
        """
        self.websocket = websocket
        self.graphql_engine = graphql_engine
        self.context = context
        self.tasks: Set["asyncio.Task"] = set()
        self.operations: Dict[str, AsyncIterator] = {}

    @property
    def closed(self) -> bool:
        """
        TODO:
        :return: TODO:
        :rtype: TODO:
        """
        return self.websocket.closed

    async def receive(self) -> Optional[str]:
        """
        TODO:
        :return: TODO:
        :rtype: TODO:
        :raises WSConnectionClosed: TODO:
        """
        print(
            "-> ConnectionContext.receive",
            self.websocket.closed,
        )
        if self.websocket.closed:
            raise WSConnectionClosed()

        message = await self.websocket.receive()
        print("*> ConnectionContext.receive", message)

        if message.type == WSMsgType.TEXT:
            return message.data

        if message.type in (
            WSMsgType.CLOSE,
            WSMsgType.CLOSING,
            WSMsgType.CLOSED,
        ):
            raise WSConnectionClosed()

    async def send(self, data: str) -> None:
        """
        TODO:
        :param data: TODO:
        :type data: TODO:
        """
        if self.websocket.closed:
            return
        await self.websocket.send_json(data)

    async def close(self, code: "aiohttp.WSCloseCode") -> None:
        """
        TODO:
        :param code: TODO:
        :type code: TODO:
        """
        if self.websocket.closed:
            return
        await self.websocket.close(code=code)

    def has_operation(self, operation_id: str) -> bool:
        """
        TODO:
        :param operation_id: TODO:
        :type operation_id: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        return operation_id in self.operations
