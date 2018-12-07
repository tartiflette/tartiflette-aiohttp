![Tartiflette aiohttp](docs/github-landing.png)

**tartiflette-aiohttp** is a wrapper of [aiohttp](https://github.com/aio-libs/aiohttp/) which includes the [Tartiflette GraphQL Engine](https://github.com/dailymotion/tartiflette), do not hesitate to take a look of the [Tartiflette project](https://github.com/dailymotion/tartiflette).

**Summary**

- [Usage](#usage)
- [Installation](#installation)
    - [Installation dependencies](#installation-dependencies)
- [How to use](#how-to-use)
    - [Use with built-in Tartiflette Engine](#use-with-built-in-tartiflette-engine)
    - [Use with custom Tartiflette engine](#use-with-custom-tartiflette-engine)

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

Execute a request to your server
```
curl -v -d '{"query": "query { hello(name: "Chuck") }"}' -H "Content-Type: application/json" http://localhost:8080/graphql
```

## Installation

`tartiflette-aiohttp` is available on [pypi.org](https://pypi.org/project/tartiflette-aiohttp/).

```bash
pip install tartiflette-aiohttp
```

### Installation dependencies

As [Tartiflette](https://github.com/dailymotion/tartiflette) based its Executor engine on *[libgraphqlparser](https://github.com/graphql/libgraphqlparser)*. You'll need these following commands on your environment to use the library. `cmake`, `bison` and `flex`.

*MacOSX*
```bash
brew install cmake flex bison
```

*Ubuntu*
```bash
apt-get install cmake flex bison
```

## How to use

### Use with built-in Tartiflette Engine

The basic and common way to use Tartiflette with aiohttp, is to create an aiohttp `web.Application` and use the `register_graphql_handlers` helper to bind Tartiflette and aiohttp together. `engine_*` parameters will be forwarded to the built-in [tartiflette](https://github.com/dailymotion/tartiflette) engine instance.

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
  - Could be a string which contains the SDL
  - Could be an array of string, which contain the SDLs
  - Could be a path of an SDL
  - Could be an array of paths which contain the SDLs
* **engine_schema_name**: Name of the schema used the built-in engine.
* **executor_context**: Context which will be passed to each resolver. Be default, the context passed to each resolvers, will contain these properties.
  - **req**: Request object from aiohttp
  - **app**: Application object from aiohttp
* **executor_http_endpoint**: Endpoint where the GraphQL Engine will be attached, by default on `/graphql`
* **executor_http_methods**: HTTP Method where the GraphQL Engine will be attached, by default on **POST** and **GET**.

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

* **engine**: Tartiflette Engine instance
* **executor_context**: Context which will be passed to each resolver. Be default, the context passed to each resolvers, will contain these properties.
  - **req**: Request object from aiohttp
  - **app**: Application object from aiohttp
* **executor_http_endpoint**: Endpoint where the GraphQL Engine will be attached, by default on `/graphql`
* **executor_http_methods**: HTTP Method where the GraphQL Engine will be attached, by default on **POST** and **GET**.
