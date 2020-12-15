import json

from functools import partial
from inspect import iscoroutine
from typing import (
    Any,
    AsyncContextManager,
    Callable,
    Dict,
    List,
    Optional,
    Union,
)

from tartiflette import Engine
from tartiflette_aiohttp._context_factory import default_context_factory
from tartiflette_aiohttp._graphiql import graphiql_handler
from tartiflette_aiohttp._handler import Handlers, prepare_response
from tartiflette_aiohttp._reponse_headers import set_response_headers
from tartiflette_aiohttp._subscription_ws_handler import (
    AIOHTTPSubscriptionHandler,
)


def validate_and_compute_graphiql_option(
    raw_value: Any, option_name: str, default_value: str, indent: int = 0
) -> str:
    if not raw_value:
        return default_value

    if not isinstance(raw_value, dict):
        raise TypeError(
            f"< graphiql_options.{option_name} > parameter should be a dict."
        )

    try:
        return json.dumps(raw_value, indent=indent)
    except Exception as e:  # pylint: disable=broad-except
        raise ValueError(
            f"Unable to jsonify < graphiql_options.{option_name} value. "
            f"Error: {e}."
        )


def _set_subscription_ws_handler(
    app: "Application",
    subscription_ws_endpoint: Optional[str],
    subscription_keep_alive_interval: Optional[int],
    context_factory: "AbstractAsyncContextManager",
) -> None:
    if not subscription_ws_endpoint:
        return

    app["subscription_keep_alive_interval"] = subscription_keep_alive_interval

    app.router.add_route(
        "GET",
        subscription_ws_endpoint,
        AIOHTTPSubscriptionHandler(app, context_factory),
    )


def _set_graphiql_handler(
    app: "Application",
    graphiql_enabled: bool,
    graphiql_options: Optional[Dict[str, Any]],
    executor_http_endpoint: str,
    executor_http_methods: List[str],
    subscription_ws_endpoint: Optional[str],
) -> None:
    if not graphiql_enabled:
        return

    if graphiql_options is None:
        graphiql_options = {}

    app.router.add_route(
        "GET",
        graphiql_options.get("endpoint", "/graphiql"),
        partial(
            graphiql_handler,
            graphiql_options={
                "endpoint": executor_http_endpoint,
                "is_subscription_enabled": json.dumps(
                    bool(subscription_ws_endpoint)
                ),
                "subscription_ws_endpoint": subscription_ws_endpoint,
                "query": graphiql_options.get("default_query") or "",
                "variables": validate_and_compute_graphiql_option(
                    graphiql_options.get("default_variables"),
                    "default_variables",
                    "",
                    2,
                ),
                "headers": validate_and_compute_graphiql_option(
                    graphiql_options.get("default_headers"),
                    "default_headers",
                    "{}",
                ),
                "http_method": "POST"
                if "POST" in executor_http_methods
                else "GET",
            },
        ),
    )


async def _cook_on_startup(sdl, schema_name, modules, app):
    await app["ttftt_engine"].cook(
        sdl=sdl, schema_name=schema_name, modules=modules
    )


async def _await_on_startup(app):
    app["ttftt_engine"] = await app["ttftt_engine"]


def register_graphql_handlers(
    app: "aiohttp.web.Application",
    engine_sdl: str = None,
    engine_schema_name: str = "default",
    executor_context: Optional[Dict[str, Any]] = None,
    executor_http_endpoint: str = "/graphql",
    executor_http_methods: List[str] = None,
    engine: Engine = None,
    subscription_ws_endpoint: Optional[str] = None,
    subscription_keep_alive_interval: Optional[int] = None,
    graphiql_enabled: bool = False,
    graphiql_options: Optional[Dict[str, Any]] = None,
    engine_modules: Optional[
        List[Union[str, Dict[str, Union[str, Dict[str, str]]]]]
    ] = None,
    context_factory: Optional[AsyncContextManager] = None,
    response_formatter: Optional[
        Callable[
            ["aiohttp.web.Request", Dict[str, Any], Dict[str, Any]],
            "aiohttp.web.Response",
        ]
    ] = None,
) -> "aiohttp.web.Application":
    """Register a Tartiflette Engine to an app

    Pass a SDL or an already initialized Engine, not both, not neither.

    Keyword Arguments:
        app {aiohttp.web.Application} -- The application to register to.
        engine_sdl {str} -- The SDL defining your API (default: {None})
        engine_schema_name {str} -- The name of your sdl (default: {"default"})
        executor_context {Optional[Dict[str, Any]]} -- Context dict that will be passed to the resolvers (default: {None})
        executor_http_endpoint {str} -- Path part of the URL the graphql endpoint will listen on (default: {"/graphql"})
        executor_http_methods {list[str]} -- List of HTTP methods allowed on the endpoint (only GET and POST are supported) (default: {None})
        engine {Engine} -- An uncooked engine, or a create_engine coroutines (default: {None})
        subscription_ws_endpoint {Optional[str]} -- Path part of the URL the WebSocket GraphQL subscription endpoint will listen on (default: {None})
        subscription_keep_alive_interval {Optional[int]} -- Number of seconds before each Keep Alive messages (default: {None})
        graphiql_enabled {bool} -- Determines whether or not we should handle a GraphiQL endpoint (default: {False})
        graphiql_options {dict} -- Customization options for the GraphiQL instance (default: {None})
        engine_modules: {Optional[List[Union[str, Dict[str, Union[str, Dict[str, str]]]]]]} -- Module to import (default:{None})
        context_factory: {Optional[AsyncContextManager]} -- asynccontextmanager in charge of generating the context for each request (default: {None})
        response_formatter: {Optional[Callable[[aiohttp.web.Request, Dict[str, Any], Dict[str, Any]], aiohttp.web.Response]]} -- In charger of the transformation of the resulting data into an aiohttp.web.Response (default: {None})
    Raises:
        Exception -- On bad sdl/engine parameter combinaison.
        Exception -- On unsupported HTTP Method.

    Return:
        The app object.
    """
    # pylint: disable=too-many-arguments,too-many-locals
    if not executor_context:
        executor_context = {}

    executor_context["app"] = app

    if not executor_http_methods:
        executor_http_methods = ["GET", "POST"]

    if context_factory is None:
        context_factory = default_context_factory

    context_factory = partial(context_factory, executor_context)

    if not engine:
        engine = Engine()

    if iscoroutine(engine):
        app.on_startup.append(_await_on_startup)
    else:
        app.on_startup.append(
            partial(
                _cook_on_startup,
                engine_sdl,
                engine_schema_name,
                engine_modules,
            )
        )

    app["ttftt_engine"] = engine
    app["response_formatter"] = response_formatter or prepare_response

    for method in executor_http_methods:
        try:
            app.router.add_route(
                method,
                executor_http_endpoint,
                partial(
                    getattr(Handlers, "handle_%s" % method.lower()),
                    context_factory=context_factory,
                ),
            )
        except AttributeError:
            raise Exception("Unsupported < %s > http method" % method)

    _set_subscription_ws_handler(
        app,
        subscription_ws_endpoint,
        subscription_keep_alive_interval,
        context_factory,
    )

    _set_graphiql_handler(
        app,
        graphiql_enabled,
        graphiql_options,
        executor_http_endpoint,
        executor_http_methods,
        subscription_ws_endpoint,
    )

    return app


__all__ = ["register_graphql_handlers", "set_response_headers"]
