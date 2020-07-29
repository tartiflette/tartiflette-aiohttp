from typing import Any, Dict

try:
    from contextlib import asynccontextmanager  # Python 3.7+
except ImportError:
    from async_generator import asynccontextmanager  # Python 3.6

__all__ = ("default_context_factory",)


@asynccontextmanager
async def default_context_factory(
    context: Dict[str, Any], req: "aiohttp.web.Request"
) -> Dict[str, Any]:
    """
    Generates a new context.
    :param context: the value filled in through the `executor_context`
    parameter
    :param req: the incoming aiohttp request instance
    :type context: Dict[str, Any]
    :type req: aiohttp.web.Request
    :return: the context for the incoming request
    :rtype: Dict[str, Any]
    """
    yield {**context, "req": req}
