import os

from string import Template

from aiohttp import web


try:
    _TTFTT_AIOHTTP_DIR = os.path.dirname(__file__)

    with open(os.path.join(_TTFTT_AIOHTTP_DIR, "_graphiql.html")) as tpl_file:
        _GRAPHIQL_TEMPLATE = tpl_file.read()
except Exception as e:  # pylint: disable=broad-except
    _GRAPHIQL_TEMPLATE = ""


async def graphiql_handler(
    request, executor_http_endpoint, executor_http_methods
):
    # pylint: disable=unused-argument
    return web.Response(
        text=_render_graphiql(executor_http_endpoint, executor_http_methods),
        headers={"Content-Type": "text/html"},
    )


def _render_graphiql(executor_http_endpoint, executor_http_methods):
    return Template(_GRAPHIQL_TEMPLATE).substitute(
        endpoint_url=executor_http_endpoint,
        http_method=("POST" if "POST" in executor_http_methods else "GET"),
    )
