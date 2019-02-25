import os

from string import Template
from typing import Dict, Any

from aiohttp import web

try:
    _TTFTT_AIOHTTP_DIR = os.path.dirname(__file__)

    with open(os.path.join(_TTFTT_AIOHTTP_DIR, "_graphiql.html")) as tpl_file:
        _GRAPHIQL_TEMPLATE = tpl_file.read()
except Exception as e:  # pylint: disable=broad-except
    _GRAPHIQL_TEMPLATE = ""


async def graphiql_handler(
    request, graphiql_options: Dict[str, Any]
) -> "Response":
    # pylint: disable=unused-argument
    return web.Response(
        text=_render_graphiql(graphiql_options),
        headers={"Content-Type": "text/html"},
    )


def _render_graphiql(graphiql_options: Dict[str, Any]) -> str:
    return Template(_GRAPHIQL_TEMPLATE).substitute(
        endpoint=graphiql_options["endpoint"],
        is_subscription_enabled=graphiql_options["is_subscription_enabled"],
        subscription_ws_endpoint=graphiql_options["subscription_ws_endpoint"],
        http_method=graphiql_options["http_method"],
        default_query=graphiql_options["query"],
        default_variables=graphiql_options["variables"],
        default_headers=graphiql_options["headers"],
    )
