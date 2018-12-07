import asyncio
import logging
import sys

from aiohttp import web

from utils.signals import SigTermHandler
from tartiflette_aiohttp import register_graphql_handlers
import starwars.resolvers

logger = logging.getLogger(__name__)


def gracefull_stop(loop):
    """Force loop to end by stopping it.
    """
    loop.stop()


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

    # Add gracefull stop to SIGTERM Handler
    sth = SigTermHandler()
    sth.add_callback(gracefull_stop, loop=loop)

    # Init aiohttp
    app = web.Application()

    # Suscribe on_shutdown to the SHUTDOWN event of the app
    app.on_shutdown.append(on_shutdown)

    register_graphql_handlers(app, engine_sdl="starwars/sdl/starwars.sdl")

    # Bind aiohttp to asyncio
    app_handler = app.make_handler()
    srv = loop.run_until_complete(
        loop.create_server(app_handler, "0.0.0.0", "8089")
    )

    try:
        loop.run_forever()
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(e)
    except KeyboardInterrupt:  # CTRL+C (SIGINT) Here
        logger.info("Why did you CTRL+C me ?")
    finally:
        logger.info("Closing Server ...")
        srv.close()
        logger.info("Stopping Accepting Connections ...")
        loop.run_until_complete(srv.wait_closed())
        logger.info("Sending Application SHUTDOWN Event ...")
        loop.run_until_complete(app.shutdown())
        logger.info("Closing Accepted Connections (60s) ...")
        loop.run_until_complete(
            # 60 is the value recommended by aiohttp doc
            app_handler.shutdown(60.0)
        )
        logger.info("Calling Registered Application Finalizer ...")
        loop.run_until_complete(app.cleanup())
        logger.info("Seeya")

    loop.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
