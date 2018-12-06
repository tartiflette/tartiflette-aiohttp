import pytest
from unittest.mock import Mock


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
    pass
