import json

import pytest

from aiohttp import web
from tartiflette import Engine, Resolver, create_engine
from tartiflette_aiohttp import register_graphql_handlers


async def test_awaitable_engine(aiohttp_client, loop):
    @Resolver("Query.bob", schema_name="test_awaitable_engine")
    async def resolver_lol(*args, **kwargs):
        return {"name": "a", "surname": "b"}

    app = register_graphql_handlers(
        app=web.Application(),
        engine=create_engine(
            """type Query { bob: Ninja } type Ninja { name: String surname: String }""",
            schema_name="test_awaitable_engine",
        ),
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


async def test_child_class(aiohttp_client, loop):
    @Resolver("Query.bob", schema_name="test_child_class")
    async def resolver_lol(*args, **kwargs):
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
        engine_schema_name="test_child_class",
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


async def test_engine_composition(aiohttp_client, loop):
    @Resolver("Query.bob", schema_name="test_engine_composition")
    async def resolver_lol(*args, **kwargs):
        return {"name": "a", "surname": "b"}

    class myEngine:
        def __init__(self):
            self._engine = Engine()

        async def cook(self, *args, **kwargs):
            await self._engine.cook(*args, **kwargs)

        async def execute(self, *args, **kwargs):
            return await self._engine.execute(*args, **kwargs)

    app = register_graphql_handlers(
        app=web.Application(),
        engine=myEngine(),
        engine_sdl="""type Query { bob: Ninja } type Ninja { name: String surname: String }""",
        engine_schema_name="test_engine_composition",
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
