import asyncio

import logging.config
import sys

from aiohttp import web
from tartiflette_aiohttp import register_graphql_handlers

import resolvers.dogs

logger = logging.getLogger(__name__)

async def _on_shutdown(app):
    """
    app SHUTDOWN event handler
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
    app.on_shutdown.append(_on_shutdown)

    register_graphql_handlers(
        app,
        "schema.graphql",
        subscription_ws_endpoint="/ws",
        graphiql_enabled=True,
        graphiql_options={
            "default_query": """fragment DogFields on Dog {
  id
  name
  nickname
}

query Dog($dogId: Int!) {
  dog(id: $dogId) {
    ...DogFields
  }
}

mutation AddDog($addInput: AddDogInput!) {
  addDog(input: $addInput) {
    clientMutationId
    status
    dog {
      ...DogFields
    }
  }
}

mutation UpdateDog($updateInput: UpdateDogInput!) {
  updateDog(input: $updateInput) {
    clientMutationId
    status
    dog {
      ...DogFields
    }
  }
}

subscription DogAdded {
  dogAdded {
    ...DogFields
  }
}

subscription DogUpdated($dogId: Int!) {
  dogUpdated(id: $dogId) {
    ...DogFields
  }
}""",
            "default_variables": {
                "dogId": 1,
                "addInput": {
                    "clientMutationId": "addDog",
                    "name": "Dog #2",
                    "nickname": None,
                },
                "updateInput": {
                    "clientMutationId": "updateDog",
                    "id": 2,
                    "name": "Dog #2.1",
                    "nickname": None,
                },
            },
        },
    )

    # Bind aiohttp to asyncio
    logger.error("Let's go.")

    web.run_app(app, host="0.0.0.0", port="8090")

    return 0


if __name__ == "__main__":
    sys.exit(main())
