from string import Template

import pkg_resources

from aiohttp import web


_GRAPHIQL_TEMPLATE = pkg_resources.resource_string(
    __name__, "_graphiql.html"
).decode("utf-8")


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
