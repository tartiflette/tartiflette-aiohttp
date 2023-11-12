![Tartiflette aiohttp](github-landing.png)

**tartiflette-aiohttp** is a wrapper of `aiohttp` which includes the Tartiflette GraphQL Engine. You can take a look at the [Tartiflette API documentation](https://tartiflette.io/docs/welcome/what-is-tartiflette).

## Usage

```python
# main.py
from aiohttp import web
from tartiflette import Resolver
from tartiflette_aiohttp import register_graphql_handlers

@Resolver("Query.hello")
async def resolver_hello(parent, args, ctx, info):
    return "hello " + args["name"]

sdl = """
    type Query {
        hello(name: String): String
    }
"""

web.run_app(
    register_graphql_handlers(
        web.Application(),
        engine_sdl=sdl
    )
)
```

Save the file and start the server.

```bash
$ python main.py
======== Running on http://0.0.0.0:8080 ========
(Press CTRL+C to quit)
```

> Note: The server will be listening on the `/graphql` path by default.

Send a request to your server
```bash
curl -v -d '{"query": "query { hello(name: \"Chuck\") }"}' -H "Content-Type: application/json" http://localhost:8080/graphql
```

## Installation

`tartiflette-aiohttp` is available on [pypi.org](https://pypi.org/project/tartiflette-aiohttp/).

**WARNING**: Do not forget to install the [tartiflette dependencies beforehand as explained in the tutorial](https://tartiflette.io/docs/tutorial/install-tartiflette/).

```bash
pip install tartiflette-aiohttp
```

## How to use

### Use with built-in Tartiflette Engine

The basic and common way to use Tartiflette with `aiohttp`, is to create an `aiohttp` `web.Application` and use the `register_graphql_handlers` helper to bind Tartiflette and `aiohttp` together. `engine_*` parameters will be forwarded to the built-in [tartiflette](https://github.com/tartiflette/tartiflette) engine instance.

```python
from aiohttp import web
from tartiflette_aiohttp import register_graphql_handlers

sdl = """
    type Query {
        hello(name: String): String
    }
"""

ctx = {
    'user_service': user_service
}

web.run_app(
    register_graphql_handlers(
        app=web.Application(),
        engine_sdl=sdl,
        engine_schema_name="default",
        executor_context=ctx,
        executor_http_endpoint='/graphql',
        executor_http_methods=['POST', 'GET']
    )
)
```

**Parameters**:

* **engine_sdl**: Contains the [Schema Definition Language](https://graphql.org/learn/schema/)
  - Can be a string which contains the SDL
  - Can be an array of strings, which contain the SDLs
  - Can be a path to an SDL
  - Can be an array of paths which contain the SDLs
* **engine_schema_name**: Name of the schema used by the built-in engine. Useful for advanced use-cases, see [Schema Registry API](https://tartiflette.io/docs/api/schema-registry).
* **executor_context**: Context which will be passed to each resolver (as a dict). Very useful for passing handlers to services, functions or data that you want to use in your resolvers. The context reference is **unique** per request, a shallow copy is created based on the context passed.
  - **req**: Request object from `aiohttp`
  - **app**: Application object from `aiohttp`
* **executor_http_endpoint**: Endpoint where the GraphQL Engine will be attached, by default on `/graphql`
* **executor_http_methods**: HTTP Methods where the GraphQL Engine will be attached, by default on **POST** and **GET**.

### Use with custom Tartiflette engine

In the case you already have a Tartiflette Engine instance, or, you do not want to use the built-in instance. You can pass an existing instance to the `register_graphql_handlers` helper.

```python
# main.py
from aiohttp import web
from tartiflette import Resolver, Engine
from tartiflette_aiohttp import register_graphql_handlers

@Resolver("Query.hello")
async def resolver_hello(parent, args, ctx, info):
    return "hello " + args["name"]

sdl = """
    type Query {
        hello(name: String): String
    }
"""

engine = Engine(sdl)

ctx = {
    'user_service': user_service
}

web.run_app(
    register_graphql_handlers(
        app=web.Application(),
        engine=engine,
        executor_context=ctx,
        executor_http_endpoint='/graphql',
        executor_http_methods=['POST', 'GET']
    )
)
```

**Parameters**:

* **engine**: an instance of the Tartiflette Engine
* **executor_context**: Context which will be passed to each resolver (as a dict). Very useful for passing handlers to services, functions or data that you want to use in your resolvers.
  - **req**: Request object from `aiohttp`
  - **app**: Application object from `aiohttp`
* **executor_http_endpoint**: Endpoint where the GraphQL Engine will be attached, by default on `/graphql`
* **executor_http_methods**: HTTP Methods where the GraphQL Engine will be attached, by default on **POST** and **GET**

### Tartiflette with subscriptions

Tartiflette embeds an easy way to deal with subscriptions. The only thing to do is
to fill in the `subscription_ws_endpoint` parameter and everything will work out
of the box with `aiohttp` WebSockets. You can see a full example
[here](examples/aiohttp/dogs).

### Enable GraphiQL handler

Tartiflette allows you to set up an instance of GraphiQL easily to quickly test
your queries. The easiest way to do that is to set the `graphiql_enabled`
parameter to `True`. Then, you can customize your GraphiQL instance by filling
the `graphiql_options` parameter as bellow:

```python
from aiohttp import web

from tartiflette_aiohttp import register_graphql_handlers


_SDL = """
    type Query {
        hello(name: String): String
    }
"""

web.run_app(
    register_graphql_handlers(
        app=web.Application(),
        engine_sdl=_SDL,
        graphiql_enabled=True,
        graphiql_options={  # This is optional
            "endpoint": "/explorer",  # Default: `/graphiql`,
            "default_query": """
                query Hello($name: String) {
                  hello(name: $name)
                }
            """,
            "default_variables": {
                "name": "Bob",
            },
            "default_headers": {
                "Authorization": "Bearer <default_token>",
            },
        },
    )
)
```

**Parameters**:

* **engine_sdl**: Contains the [Schema Definition Language](https://graphql.org/learn/schema/)
  - Can be a string which contains the SDL
  - Can be an array of strings, which contain the SDLs
  - Can be a path to an SDL
  - Can be an array of paths which contain the SDLs
* **graphiql_enabled** *(Optional[bool] = False)*: Determines whether or not we should include a GraphiQL interface
* **graphiql_options** *(Optional[dict] = None)*: Customization options for the GraphiQL instance:
  - **endpoint** *(Optional[str] = "/graphiql")*: allows to customize the GraphiQL interface endpoint path
  - **default_query** *(Optional[str] = None)*: allows you to pre-fill the GraphiQL interface with a default query
  - **default_variables** *(Optional[dict] = None)*: allows you to pre-fill the GraphiQL interface with default variables
  - **default_headers** *(Optional[dict] = None)*: allows you to add default headers to each request sent through the GraphiQL instance


## Advance Use Case

### Response header manipulation from resolver

It is possible to set header to the response directly from the resolver using `set_response_headers` method like:

```python
from tartiflette_aiohttp import set_response_headers

@Resolver("Query.X")
async def resolver_x(parent_result, args, ctx, info):
    # do things
    set_response_headers({"Header": "Value", "AnotherHeader": "AnotherValue"})
    return result
```

> Note that this feature uses ContextVar and will only works for python 3.7.1 and later.

OR it is also possible to do, if you do not have ContextVar, or don't want to use them:

```python
from aiohttp import web

def a_callable(req, data, ctx):
    return web.json_response(data, headers=ctx["_any_custom_key"])

web.run_app(
    register_graphql_handlers(
        app=web.Application(),
        engine_sdl=_SDL,
        response_formatter=a_callable
    )
)


@Resolver("Type.field_name")
async def fiel_name_resolver(pr, args, ctx, info):
    ctx["_any_custom_key"] = {"X-Header": "What a wonderfull value"}
    return something
```
