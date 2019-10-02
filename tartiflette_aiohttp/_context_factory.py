from typing import Any, Dict

__all__ = ("default_context_factory",)


async def default_context_factory(
    req: "aiohttp.web.Request", context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generates a new context.
    :param req: the incoming aiohttp request instance
    :param context: the value filled in through the `executor_context` parameter
    :type req: aiohttp.web.Request
    :type context: Dict[str, Any]
    :return: the context for the incoming request
    :rtype: Dict[str, Any]
    """
    return {**context, "req": req}
