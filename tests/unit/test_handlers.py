from functools import partial
from unittest.mock import Mock

import pytest

from asynctest import CoroutineMock

from tartiflette_aiohttp import default_context_factory


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
    a_req.app = {
        "ttftt_engine": an_engine,
        "response_formatter": _prepare_resp,
    }

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
                "operation_name": "a",
            },
        )
    ]


def _prepare_resp(_, data, __):
    return data


@pytest.mark.asyncio
async def test_handler__handle_query_nok():
    from tartiflette_aiohttp._handler import _handle_query

    an_engine = Mock()
    an_engine.execute = CoroutineMock(return_value="T")

    a_req = Mock()
    a_req.app = {"response_formatter": _prepare_resp}

    def _get_params(*_, **__):
        return (
            "query a {}",
            {"B": "C"},
            "a",
        )

    a_response = await _handle_query(
        a_req,
        "query a {}",
        {"B": "C"},
        "a",
        {"D": "E"},
    )

    assert a_response == {
        "data": None,
        "errors": [{"message": "'ttftt_engine'", "type": "internal_error"}],
    }
    assert an_engine.execute.called is False


@pytest.mark.asyncio
async def test_handler__get_params_raises():
    from tartiflette_aiohttp._handler import BadRequestError, _get_params

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
    from tartiflette_aiohttp._handler import BadRequestError, _post_params

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
    a_req.app = {
        "ttftt_engine": an_engine,
        "response_formatter": _prepare_resp,
    }

    a_method = CoroutineMock(return_value=("a", "b", "c"))

    await Handlers._handle(
        a_method, a_req, partial(default_context_factory, {})
    )

    assert a_method.call_args_list == [((a_req,),)]


@pytest.mark.asyncio
async def test_handler__handle_nok():
    from tartiflette_aiohttp._handler import BadRequestError, Handlers

    an_engine = Mock()
    an_engine.execute = CoroutineMock(return_value="T")

    a_req = Mock()
    a_req.app = {"response_formatter": _prepare_resp}

    async def ninja(*args, **kwargs):
        raise BadRequestError("a")

    a_method = ninja

    await Handlers._handle(
        a_method, a_req, partial(default_context_factory, {})
    )


@pytest.mark.asyncio
async def test_handler__handle_get():
    from tartiflette_aiohttp._handler import Handlers, _get_params

    Handlers._handle = CoroutineMock(return_value="T")

    a_req = Mock()

    assert await Handlers.handle_get({"a": "n"}, a_req) == "T"

    assert Handlers._handle.call_args_list == [
        ((_get_params, {"a": "n"}, a_req),)
    ]


@pytest.mark.asyncio
async def test_handler__handle_post():
    from tartiflette_aiohttp._handler import Handlers, _post_params

    Handlers._handle = CoroutineMock(return_value="T")

    a_req = Mock()

    assert await Handlers.handle_post({"a": "n"}, a_req) == "T"

    assert Handlers._handle.call_args_list == [
        ((_post_params, {"a": "n"}, a_req),)
    ]
