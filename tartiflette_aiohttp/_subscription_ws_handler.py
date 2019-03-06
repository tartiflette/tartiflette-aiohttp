import json

from asyncio import wait, ensure_future, shield
from typing import Dict, Any, AsyncIterator, Optional, Set

from aiohttp import web, WSMsgType

from tartiflette_aiohttp._constants import (
    WS_PROTOCOL,
    GQL_CONNECTION_INIT,
    GQL_CONNECTION_ACK,
    GQL_CONNECTION_ERROR,
    GQL_CONNECTION_TERMINATE,
    GQL_START,
    GQL_DATA,
    GQL_ERROR,
    GQL_COMPLETE,
    GQL_STOP,
)

_ALLOWED_ERROR_TYPES = [GQL_CONNECTION_ERROR, GQL_ERROR]


def _get_graphql_params(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "query": payload.get("query"),
        "variables": payload.get("variables"),
        "operation_name": payload.get("operationName"),
        "context": payload.get("context"),
    }


class ConnectionClosedException(Exception):
    pass


class AIOHTTPConnectionContext:
    def __init__(self, socket: "WebSocketResponse") -> None:
        self._socket: "WebSocketResponse" = socket
        self._operations: Dict[str, AsyncIterator] = {}

    @property
    def operations(self) -> Dict[str, AsyncIterator]:
        return self._operations

    @property
    def closed(self) -> bool:
        return self._socket.closed

    def has_operation(self, operation_id: str) -> bool:
        return operation_id in self._operations

    def register_operation(
        self, operation_id: str, async_iterator: AsyncIterator
    ) -> None:
        self._operations[operation_id] = async_iterator

    def get_operation(self, operation_id: str) -> AsyncIterator:
        return self._operations[operation_id]

    def remove_operation(self, operation_id: str) -> None:
        del self._operations[operation_id]

    async def receive(self) -> str:
        msg = await self._socket.receive()
        if msg.type == WSMsgType.TEXT:
            return msg.data
        raise ConnectionClosedException()

    async def send(self, data: str) -> None:
        if self.closed:
            return
        await self._socket.send_str(data)

    async def close(self, code: int) -> None:
        await self._socket.close(code=code)


class AIOHTTPSubscriptionHandler:
    def __init__(self, engine: "Engine") -> None:
        self._engine: "Engine" = engine

    async def _send_message(
        self,
        connection_context: "AIOHTTPConnectionContext",
        operation_id: Optional[str] = None,
        op_type: Optional[str] = None,
        payload: Optional[Any] = None,
    ) -> None:
        message = {}
        if operation_id is not None:
            message["id"] = operation_id
        if op_type is not None:
            message["type"] = op_type
        if payload is not None:
            message["payload"] = payload
        await connection_context.send(json.dumps(message))

    async def _send_error(
        self,
        connection_context: "AIOHTTPConnectionContext",
        operation_id: Optional[str],
        error: Exception,
        error_type: Optional[str] = None,
    ) -> None:
        await self._send_message(
            connection_context,
            operation_id,
            error_type if error_type in _ALLOWED_ERROR_TYPES else GQL_ERROR,
            {"message": str(error)},
        )

    async def _on_connection_init(
        self, connection_context: "AIOHTTPConnectionContext", operation_id: str
    ) -> None:
        try:
            return await self._send_message(
                connection_context, op_type=GQL_CONNECTION_ACK
            )
        except Exception as e:  # pylint: disable=broad-except
            await self._send_error(
                connection_context, operation_id, e, GQL_CONNECTION_ERROR
            )
            return await connection_context.close(1011)

    async def _on_connection_terminate(
        self, connection_context: "AIOHTTPConnectionContext"
    ) -> None:
        await connection_context.close(1011)

    async def _unsubscribe(
        self, connection_context: "AIOHTTPConnectionContext", operation_id: str
    ) -> None:
        try:
            await connection_context.get_operation(operation_id).aclose()
            connection_context.remove_operation(operation_id)
        except KeyError:
            pass

    async def _on_start(
        self,
        connection_context: "AIOHTTPConnectionContext",
        operation_id: str,
        payload: Dict[str, Any],
    ) -> None:
        params = _get_graphql_params(payload)
        if not isinstance(params, dict):
            return await self._send_error(
                connection_context,
                operation_id,
                Exception("Received invalid params."),
            )

        if connection_context.has_operation(operation_id):
            await self._unsubscribe(connection_context, operation_id)

        iterator = self._engine.subscribe(**params)

        connection_context.register_operation(operation_id, iterator)

        try:
            async for result in iterator:
                if not connection_context.has_operation(operation_id):
                    break
                await self._send_message(
                    connection_context, operation_id, GQL_DATA, result
                )
        except Exception:  # pylint: disable=broad-except
            await self._send_error(
                connection_context, operation_id, Exception("Internal Error")
            )

        await self._send_message(
            connection_context, operation_id, GQL_COMPLETE
        )

    async def _on_stop(
        self, connection_context: "AIOHTTPConnectionContext", operation_id: str
    ) -> None:
        await self._unsubscribe(connection_context, operation_id)

    async def _process_message(
        self,
        connection_context: "AIOHTTPConnectionContext",
        parsed_message: Dict[str, Any],
    ) -> None:
        op_type = parsed_message.get("type")
        operation_id = parsed_message.get("id")
        payload = parsed_message.get("payload")

        if op_type == GQL_CONNECTION_INIT:
            return await self._on_connection_init(
                connection_context, operation_id
            )
        if op_type == GQL_START:
            return await self._on_start(
                connection_context, operation_id, payload
            )
        if op_type == GQL_STOP:
            return await self._on_stop(connection_context, operation_id)
        if op_type == GQL_CONNECTION_TERMINATE:
            return await self._on_connection_terminate(connection_context)
        return await self._send_error(
            connection_context,
            operation_id,
            Exception(f"Unhandled message type < {op_type} >."),
        )

    async def _on_message(
        self, connection_context: "AIOHTTPConnectionContext", message: str
    ) -> None:
        try:
            if not isinstance(message, dict):
                parsed_message = json.loads(message)
                if not isinstance(parsed_message, dict):
                    raise TypeError("Payload must be an object.")
            else:
                parsed_message = message
        except Exception as e:  # pylint: disable=broad-except
            return await self._send_error(connection_context, None, e)
        return await self._process_message(connection_context, parsed_message)

    async def _on_close(
        self,
        connection_context: "AIOHTTPConnectionContext",
        tasks: Set["Task"],
    ) -> None:
        for operation_id in connection_context.operations:
            await self._unsubscribe(connection_context, operation_id)

        for task in tasks:
            task.cancel()

    async def _handle_request(self) -> None:
        connection_context = AIOHTTPConnectionContext(self._socket)

        tasks: Set["Task"] = set()
        while True:
            try:
                if connection_context.closed:
                    raise ConnectionClosedException()
                message = await connection_context.receive()
            except ConnectionClosedException:
                break
            finally:
                if tasks:
                    _, tasks = await wait(tasks, timeout=0)

            tasks.add(
                ensure_future(self._on_message(connection_context, message))
            )

        await self._on_close(connection_context, tasks)

    async def __call__(self, request: "Request") -> "WebSocketResponse":
        self._socket = web.WebSocketResponse(  # pylint: disable=attribute-defined-outside-init
            protocols=(WS_PROTOCOL,)
        )
        await self._socket.prepare(request)
        await shield(self._handle_request())
        return self._socket
