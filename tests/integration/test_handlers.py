try:
    from contextlib import asynccontextmanager  # Python 3.7+
except ImportError:
    from async_generator import asynccontextmanager  # Python 3.6

from functools import partial
from unittest.mock import Mock

import pytest

from tartiflette_aiohttp import default_context_factory


def prepare_response(_, data, __):
    return data


@pytest.mark.asyncio
async def test_handler__handle_query__context_unicity():
    from tartiflette import Resolver, create_engine
    from tartiflette_aiohttp._handler import Handlers

    @Resolver(
        "Query.hello",
        schema_name="test_handler__handle_query__context_unicity",
    )
    async def resolver_hello(parent, args, ctx, info):
        try:
            ctx["counter"] += 1
        except:
            ctx["counter"] = 1
        return "hello " + str(ctx["counter"])

    tftt_engine = await create_engine(
        """
        type Query {
            hello(name: String): String
        }
        """,
        schema_name="test_handler__handle_query__context_unicity",
    )

    a_req = Mock()
    a_req.app = {
        "ttftt_engine": tftt_engine,
        "response_formatter": prepare_response,
    }

    context_factory = partial(default_context_factory, {})

    async def _get_param(*_, **__):
        return ('query { hello(name: "Chuck") }', None, None)

    await Handlers._handle(_get_param, a_req, context_factory)

    await Handlers._handle(_get_param, a_req, context_factory)

    b_response = await Handlers._handle(_get_param, a_req, context_factory)

    assert b_response == {"data": {"hello": "hello 1"}}


@pytest.mark.asyncio
async def test_handler__handle_query__context_manager_as_factory():
    from tartiflette import Resolver, create_engine
    from tartiflette_aiohttp._handler import Handlers

    @Resolver(
        "Query.hello",
        schema_name="test_handler__handle_query__context_manager_as_factory",
    )
    async def resolver_hello(parent, args, ctx, info):
        return "hello " + ", ".join(ctx.keys())

    tftt_engine = await create_engine(
        """
        type Query {
            hello(name: String): String
        }
        """,
        schema_name="test_handler__handle_query__context_manager_as_factory",
    )

    req = Mock()
    req.app = {
        "ttftt_engine": tftt_engine,
        "response_formatter": prepare_response,
    }

    @asynccontextmanager
    async def custom_context_factory(context, req):
        context["entered"] = True
        yield context
        context["exited"] = True

    context = {}
    context_factory = partial(custom_context_factory, context)

    async def _get_param(*_, **__):
        return ('query { hello(name: "Chuck") }', None, None)

    response = await Handlers._handle(_get_param, req, context_factory)
    assert context.get("entered")
    assert context.get("exited")
    assert response == {"data": {"hello": "hello entered"}}


@pytest.mark.asyncio
async def test_handler__handle_query__operation_name():
    from tartiflette import Resolver, create_engine
    from tartiflette_aiohttp._handler import Handlers

    @Resolver(
        "Query.hello", schema_name="test_handler__handle_query__operation_name"
    )
    async def resolver_hello(parent, args, ctx, info):
        return "hello " + args["name"]

    tftt_engine = await create_engine(
        """
        type Query {
            hello(name: String): String
        }
        """,
        schema_name="test_handler__handle_query__operation_name",
    )

    a_req = Mock()
    a_req.app = {
        "ttftt_engine": tftt_engine,
        "response_formatter": prepare_response,
    }

    context_factory = partial(default_context_factory, {})

    async def _get_param(*_, **__):
        return (
            """
            query A { hello(name: "Foo") }
            query B { hello(name: "Bar") }
            query C { hello(name: "Baz") }
            """,
            None,
            "B",
        )

    result = await Handlers._handle(
        _get_param,
        a_req,
        context_factory,
    )

    assert result == {"data": {"hello": "hello Bar"}}


@pytest.mark.asyncio
async def test_handler__handle_query__prepare_response_is_called():
    from tartiflette import Resolver, create_engine
    from tartiflette_aiohttp._handler import Handlers

    @Resolver(
        "Query.hello",
        schema_name="test_handler__handle_query__prepare_response_is_called",
    )
    async def resolver_hello(parent, args, ctx, info):
        return "hello " + ", ".join(ctx.keys())

    tftt_engine = await create_engine(
        """
        type Query {
            hello(name: String): String
        }
        """,
        schema_name="test_handler__handle_query__prepare_response_is_called",
    )

    req = Mock()
    req.app = {
        "ttftt_engine": tftt_engine,
        "response_formatter": Mock(side_effect=prepare_response),
    }

    @asynccontextmanager
    async def custom_context_factory(context, req):
        yield context

    context = {}
    context_factory = partial(custom_context_factory, context)

    async def _get_param(*_, **__):
        return ('query { hello(name: "Chuck") }', None, None)

    response = await Handlers._handle(_get_param, req, context_factory)
    assert req.app["response_formatter"].called
