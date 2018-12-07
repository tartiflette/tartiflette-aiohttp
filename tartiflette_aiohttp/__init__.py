from functools import partial
from typing import List

from tartiflette import Engine
from tartiflette_aiohttp._handler import Handlers


def register_graphql_handlers(
    app,
    engine_sdl: str = None,
    engine_schema_name: str = "default",
    executor_context: dict = None,
    executor_http_endpoint: str = "/graphql",
    executor_http_methods: List[str] = None,
    engine: Engine = None,
):
    """register a Tartiflette Engine to an app

    Pass a SDL or an already initialized Engine, not both, not neither.

    Keyword Arguments:
        app {aiohttp.web.Application} -- The application to register to.
        engine_sdl {str} -- The SDL defining your API (default: {None})
        engine_schema_name {str} -- The name of your sdl (default: {"default"})
        executor_context {dict} -- Context dict that will be passed to the resolvers (default: {None})
        executor_http_endpoint {str} -- Path part of the URL the graphql endpoint will listen on (default: {"/graphql"})
        executor_http_methods {list[str]} -- List of HTTP methods allowed on the endpoint (only GET and POST are supported) (default: {None})
        engine {Engine} -- An already initialized Engine (default: {None})

    Raises:
        Exception -- On bad sdl/engine parameter combinaison.
        Exception -- On unsupported HTTP Method.

    Return:
        The app object.
    """

    if (not engine_sdl and not engine) or (engine and engine_sdl):
        raise Exception(
            "an engine OR an engine_sdl should be passed here, not both, not none"
        )

    if not executor_context:
        executor_context = {}

    executor_context["app"] = app

    if not executor_http_methods:
        executor_http_methods = ["GET", "POST"]

    if not engine:
        engine = Engine(engine_sdl, engine_schema_name)

    app["ttftt_engine"] = engine

    for method in executor_http_methods:
        try:
            app.router.add_route(
                method,
                executor_http_endpoint,
                partial(
                    getattr(Handlers, "handle_%s" % method.lower()),
                    executor_context,
                ),
            )
        except AttributeError:
            raise Exception("Unsupported < %s > http method" % method)

    return app


__all__ = ["register_graphql_handlers"]
