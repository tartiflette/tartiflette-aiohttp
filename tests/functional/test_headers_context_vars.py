import contextvars
import json

import pytest

from aiohttp import web

from tartiflette import Engine, Resolver, create_engine
from tartiflette_aiohttp import register_graphql_handlers, set_response_headers


async def test_header_context_var(aiohttp_client, loop):
    @Resolver("Query.bob", schema_name="test_header_context_var")
    async def resolver_lol(*args, **kwargs):
        set_response_headers({"X-Test": "Lol", "Z-Test": "Ninja"})
        return {"name": "a", "surname": "b"}

    class myEngine(Engine):
        def __init__(self):
            super().__init__()

        async def cook(self, *args, **kwargs):
            await super().cook(*args, **kwargs)

    app = register_graphql_handlers(
        app=web.Application(),
        engine=myEngine(),
        engine_sdl="""type Query { bob: Ninja } type Ninja { name: String surname: String }""",
        engine_schema_name="test_header_context_var",
    )

    client = await aiohttp_client(app)
    resp = await client.post(
        "/graphql",
        data=json.dumps({"query": "query lol { bob { name surname } }"}),
        headers={"content-type": "application/json"},
    )
    assert resp.status == 200
    result = await resp.json()
    assert result == {"data": {"bob": {"name": "a", "surname": "b"}}}
    assert resp.headers["X-Test"] == "Lol"
    assert resp.headers["Z-Test"] == "Ninja"
