from typing import Any, Dict

__all__ = ("default_context_factory",)


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
    return {**context, "req": req}
