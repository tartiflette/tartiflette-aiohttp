import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock


@pytest.mark.parametrize(
    "value,expected",
    [
        (
            Exception("A message"),
            {"type": "internal_error", "message": "A message"},
        ),
        (Mock(), {"type": "internal_error", "message": "Server internal"}),
    ],
)
def test_handler__format_errors(value, expected):
    from tartiflette_aiohttp._handler import _format_errors

    assert _format_errors([value]) == [expected]


@pytest.mark.asyncio
async def test_handler__handle_query():
    from tartiflette_aiohttp._handler import _handle_query

    an_engine = Mock()
    an_engine.execute = CoroutineMock(return_value="T")

    a_req = Mock()
    a_req.app = {"ttftt_engine": an_engine}

    a_response = await _handle_query(
        a_req, "query a {}", {"B": "C"}, "a", {"D": "E"}
    )

    assert a_response == "T"
    assert an_engine.execute.call_args_list == [
        (
            (),
            {
                "query": "query a {}",
                "variables": {"B": "C"},
                "context": {"D": "E"},
            },
        )
    ]


@pytest.mark.asyncio
async def test_handler__handle_query_nok():
    from tartiflette_aiohttp._handler import _handle_query

    an_engine = Mock()
    an_engine.execute = CoroutineMock(return_value="T")

    a_req = Mock()
    a_req.app = {}

    a_response = await _handle_query(
        a_req, "query a {}", {"B": "C"}, "a", {"D": "E"}
    )

    assert a_response == {
        "data": None,
        "errors": [{"message": "'ttftt_engine'", "type": "internal_error"}],
    }
    assert an_engine.execute.called == False


@pytest.mark.asyncio
async def test_handler__get_params_raises():
    from tartiflette_aiohttp._handler import _get_params
    from tartiflette_aiohttp._handler import BadRequestError

    req = Mock()
    req.query = {}

    with pytest.raises(BadRequestError):
        await _get_params(req)

    req = Mock()
    req.query = {"query": "A", "variables": "{"}

    with pytest.raises(BadRequestError):
        await _get_params(req)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "rvalue,expected",
    [
        (
            {"query": "A", "variables": '{"a": "b"}'},
            {"a": "A", "b": {"a": "b"}, "c": None},
        ),
        (
            {"query": "A", "variables": '{"a": "b"}', "operationName": "G"},
            {"a": "A", "b": {"a": "b"}, "c": "G"},
        ),
    ],
)
async def test_handler__get_params(rvalue, expected):
    from tartiflette_aiohttp._handler import _get_params

    req = Mock()
    req.query = rvalue

    a, b, c = await _get_params(req)

    assert a == expected["a"]
    assert b == expected["b"]
    assert c == expected["c"]


@pytest.mark.asyncio
async def test_handler__post_params_raises():
    from tartiflette_aiohttp._handler import _post_params
    from tartiflette_aiohttp._handler import BadRequestError

    async def ninja(*args, **kwargs):
        raise Exception("LOL")

    req = Mock()
    req.json = ninja

    with pytest.raises(BadRequestError):
        await _post_params(req)

    req.json = CoroutineMock(return_value={})

    with pytest.raises(BadRequestError):
        await _post_params(req)

    req.json = CoroutineMock(return_value={"query": "a", "variables": "{"})

    with pytest.raises(BadRequestError):
        await _post_params(req)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "rvalue,expected",
    [
        (
            {"query": "A", "variables": '{"a": "b"}'},
            {"a": "A", "b": {"a": "b"}, "c": None},
        ),
        (
            {"query": "A", "variables": '{"a": "b"}', "operationName": "G"},
            {"a": "A", "b": {"a": "b"}, "c": "G"},
        ),
    ],
)
async def test_handler__post_params(rvalue, expected):
    from tartiflette_aiohttp._handler import _post_params

    req = Mock()
    req.json = CoroutineMock(return_value=rvalue)

    a, b, c = await _post_params(req)

    assert a == expected["a"]
    assert b == expected["b"]
    assert c == expected["c"]


@pytest.mark.asyncio
async def test_handler__handle():
    from tartiflette_aiohttp._handler import Handlers

    an_engine = Mock()
    an_engine.execute = CoroutineMock(return_value="T")

    a_req = Mock()
    a_req.app = {"ttftt_engine": an_engine}

    a_method = CoroutineMock(return_value=("a", "b", "c"))

    await Handlers._handle(a_method, {}, a_req)

    assert a_method.call_args_list == [((a_req,),)]


@pytest.mark.asyncio
async def test_handler__handle_nok():
    from tartiflette_aiohttp._handler import Handlers
    from tartiflette_aiohttp._handler import BadRequestError

    an_engine = Mock()
    an_engine.execute = CoroutineMock(return_value="T")

    a_req = Mock()
    a_req.app = {}

    async def ninja(*args, **kwargs):
        raise BadRequestError("a")

    a_method = ninja

    await Handlers._handle(a_method, {}, a_req)


@pytest.mark.asyncio
async def test_handler__handle_get():
    from tartiflette_aiohttp._handler import _get_params
    from tartiflette_aiohttp._handler import Handlers

    Handlers._handle = CoroutineMock(return_value="T")

    a_req = Mock()

    assert await Handlers.handle_get({"a": "n"}, a_req) == "T"

    assert Handlers._handle.call_args_list == [
        ((_get_params, {"a": "n"}, a_req),)
    ]


@pytest.mark.asyncio
async def test_handler__handle_post():
    from tartiflette_aiohttp._handler import _post_params
    from tartiflette_aiohttp._handler import Handlers

    Handlers._handle = CoroutineMock(return_value="T")

    a_req = Mock()

    assert await Handlers.handle_post({"a": "n"}, a_req) == "T"

    assert Handlers._handle.call_args_list == [
        ((_post_params, {"a": "n"}, a_req),)
    ]


@pytest.mark.asyncio
async def test_handler__handle_query__context_unicity():
    from tartiflette_aiohttp._handler import _handle_query
    from tartiflette import Engine, Resolver

    @Resolver("Query.hello")
    async def resolver_hello(parent, args, ctx, info):
        try:
            ctx["counter"] += 1
        except:
            ctx["counter"] = 1
        finally:
            print("counter", ctx["counter"])
        return "hello " + str(ctx["counter"])
    
    tftt_engine = Engine("""
    type Query {
        hello(name: String): String
    }
    """)

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
