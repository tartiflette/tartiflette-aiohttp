import asyncio

import sys

from aiohttp import web

from tartiflette_aiohttp import register_graphql_handlers
import starwars.resolvers

async def on_shutdown(app):
    """app SHUTDOWN event handler
    """
    for method in app.get("close_methods", []):
        logger.debug("Calling < %s >", method)
        if asyncio.iscoroutinefunction(method):
            await method()
        else:
            method()


def main():
    loop = asyncio.get_event_loop()

    # Init aiohttp
    app = web.Application()

    # Suscribe on_shutdown to the SHUTDOWN event of the app
    app.on_shutdown.append(on_shutdown)

    register_graphql_handlers(app, engine_sdl="starwars/sdl/starwars.sdl")

    # Bind aiohttp to asyncio
    web.run_app(app, host="0.0.0.0", port="8089")
    return 0


if __name__ == "__main__":
    sys.exit(main())
