from unittest.mock import MagicMock, Mock

import pytest


def test_register_graphql_handlers_raises():
    from tartiflette_aiohttp import register_graphql_handlers

    app = {}

    with pytest.raises(Exception):
        register_graphql_handlers(app)

    with pytest.raises(Exception):
        register_graphql_handlers(app, engine=Mock())


def test_register_graphql_handlers():
    from tartiflette_aiohttp import register_graphql_handlers
    from functools import partial
    from tartiflette_aiohttp._handler import Handlers

    class app(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.router = Mock()
            self.router.add_route = Mock()
            self.on_startup = []

    a = app()
    an_engine = Mock()

    assert register_graphql_handlers(a, engine=an_engine) == a
    assert a["ttftt_engine"] == an_engine
    assert a.router.add_route.called


def test_register_graphql_handlers():
    from tartiflette_aiohttp import register_graphql_handlers
    from functools import partial
    from tartiflette_aiohttp._handler import Handlers

    class app(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.router = Mock()
            self.router.add_route = Mock()
            self.on_startup = []

    a = app()
    an_engine = Mock()

    assert register_graphql_handlers(a, engine=an_engine) == a
    assert a["ttftt_engine"] == an_engine
    assert a.router.add_route.called
