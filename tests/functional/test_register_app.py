import json

import pytest

from aiohttp import web

from tartiflette import Resolver, create_engine
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


# async def test_child_class(aiohttp_client, loop):
#     app = register_graphql_handlers(
#         app=web.Application(),
#         engine=create_engine(
#             """type Query { bob: Ninja } type Ninja { name: String surname: String }""",
#             schema_name="test_awaitable_engine",
#         ),
#     )

#     client = await aiohttp_client(app)
#     resp = await client.post(
#         "/graphql",
#         data=json.dumps({"query": "query lol { bob { name surname } }"}),
#         headers={"content-type": "application/json"},
#     )
#     assert resp.status == 200
#     result = await resp.json()
#     assert result == {"data": {"bob": {"name": "a", "surname": "b"}}}
