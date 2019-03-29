import pytest
from unittest.mock import Mock


@pytest.mark.asyncio
async def test_handler__handle_query__context_unicity():
    from tartiflette_aiohttp._handler import _handle_query
    from tartiflette import Engine, Resolver

    @Resolver("Query.hello", schema_name="test_handler__handle_query__context_unicity")
    async def resolver_hello(parent, args, ctx, info):
        try:
            ctx["counter"] += 1
        except:
            ctx["counter"] = 1
        return "hello " + str(ctx["counter"])
    
    tftt_engine = Engine(
        """
        type Query {
            hello(name: String): String
        }
        """,
        schema_name="test_handler__handle_query__context_unicity"
    )

    a_req = Mock()
    a_req.app = {"ttftt_engine": tftt_engine}

    ctx = {}

    await _handle_query(
        a_req, 'query { hello(name: "Chuck") }', None, None, ctx
    )

    await _handle_query(
        a_req, 'query { hello(name: "Chuck") }', None, None, ctx
    )

    b_response = await _handle_query(
        a_req, 'query { hello(name: "Chuck") }', None, None, ctx
    )

    assert b_response == {'data': {'hello': 'hello 1'}}


@pytest.mark.asyncio
async def test_handler__handle_query__operation_name():
    from tartiflette_aiohttp._handler import _handle_query
    from tartiflette import Engine, Resolver

    @Resolver("Query.hello", schema_name="test_handler__handle_query__operation_name")
    async def resolver_hello(parent, args, ctx, info):
        return "hello " + args["name"]
    
    tftt_engine = Engine(
        """
        type Query {
            hello(name: String): String
        }
        """,
        schema_name="test_handler__handle_query__operation_name"
    )

    a_req = Mock()
    a_req.app = {"ttftt_engine": tftt_engine}

    ctx = {}

    result = await _handle_query(
        a_req,
        """
        query A { hello(name: "Foo") }
        query B { hello(name: "Bar") }
        query C { hello(name: "Baz") }
        """,
        None,
        "B",
        ctx
    )

    assert result == {'data': {'hello': 'hello Bar'}}
