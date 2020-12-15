import asyncio

from asyncio import Task
from typing import Optional

from tartiflette_aiohttp._constants import GQL_CONNECTION_KEEP_ALIVE

__all__ = ("KeepAliveHandler",)


class KeepAliveHandler:
    def __init__(
        self,
        connection_context: "AIOHTTPConnectionContext",
        interval: Optional[int],
    ) -> None:
        self._connection_context = connection_context
        self._interval = interval
        self._sleeping_task: Optional[Task] = None

    async def _routine(self) -> None:
        while not self._connection_context.closed:
            self._sleeping_task = asyncio.ensure_future(
                asyncio.sleep(self._interval)
            )
            await self._connection_context.send_message(
                op_type=GQL_CONNECTION_KEEP_ALIVE
            )
            await self._sleeping_task

    async def start(self) -> None:
        asyncio.ensure_future(self._routine())
