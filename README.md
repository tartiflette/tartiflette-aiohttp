![Tartiflette aiohttp](docs/github-landing.png)

**tartiflette-aiohttp** is a wrapper of [aiohttp](https://github.com/aio-libs/aiohttp/) which includes the [Tartiflette GraphQL Engine](https://github.com/dailymotion/tartiflette), do not hesitate to take a look of the [Tartiflette project](https://github.com/dailymotion/tartiflette). 

**Summary**

- [Usage](#usage)
- [Installation](#installation)
    - [Installation dependencies](#installation-dependencies)

## Usage

```python
# main.py
from aiohttp import web
from tartiflette import Resolver
from tartiflette_aiohttp import Application

@Resolver("Query.hello")
async def resolver_hello(parent, args, ctx, info):
    return "hello " + args["name"]

sdl = """
    type Query {
        hello(name: String): String
    }
"""

app = Application(
    engine_sdl=sdl
)

web.run_app(app)
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