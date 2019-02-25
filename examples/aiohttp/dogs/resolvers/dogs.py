import asyncio
import json
import logging

import redis

from tartiflette import Resolver, Subscription

logger = logging.getLogger(__name__)


# Faking storage
_DOGS = {1: {"id": 1, "name": "Dog #1", "nickname": "Doggo #1"}}


# Topic names
DOG_ADDED_TOPIC = "DOG_ADDED"
DOG_UPDATED_TOPIC = "DOG_UPDATED"


# Initialize Redis client
_REDIS = redis.Redis(host="redis", port=6379)


def get_dog_by_id(dog_id):
    try:
        return _DOGS[dog_id]
    except KeyError:
        pass
    return None


@Resolver("Query.dog")
async def query_dog_resolver(parent_result, args, ctx, info):
    logger.error(">> query_dog_resolver")
    dog = get_dog_by_id(args["id"])
    if dog is None:
        raise Exception("Dog < %s > not found." % args["id"])
    return dog


@Resolver("Mutation.addDog")
async def mutation_add_dog_resolver(parent_result, args, ctx, info):
    logger.error(">> mutation_add_dog_resolver")
    inputs = args["input"]

    dog_id = max(list(_DOGS.keys())) + 1

    new_dog = {
        "id": dog_id,
        "name": inputs["name"],
        "nickname": inputs.get("nickname"),
    }

    _DOGS[dog_id] = new_dog

    _REDIS.publish(DOG_ADDED_TOPIC, json.dumps(new_dog))

    return {
        "clientMutationId": inputs.get("clientMutationId"),
        "status": "SUCCESS",
        "dog": new_dog,
    }


@Resolver("Mutation.updateDog")
async def mutation_update_dog_resolver(parent_result, args, ctx, info):
    logger.error(">> mutation_update_dog_resolver")
    inputs = args["input"]

    dog = get_dog_by_id(inputs["id"])
    if dog is None:
        raise Exception("Dog < %s > not found." % inputs["id"])

    dog.update(
        {
            "name": inputs["name"],
            "nickname": (
                inputs["nickname"]
                if inputs.get("nickname") is not None
                else dog["nickname"]
            ),
        }
    )

    _REDIS.publish(DOG_UPDATED_TOPIC, json.dumps(dog))

    return {
        "clientMutationId": inputs.get("clientMutationId"),
        "status": "SUCCESS",
        "dog": dog,
    }


@Subscription("Subscription.dogAdded")
async def subscription_dog_added_subscription(parent_result, args, ctx, info):
    logger.error(">> subscription_dog_added_subscription")
    dog_added_pubsub = _REDIS.pubsub(ignore_subscribe_messages=True)
    dog_added_pubsub.subscribe(DOG_ADDED_TOPIC)
    while True:
        message = dog_added_pubsub.get_message()
        if message:
            payload = json.loads(message["data"])
            logger.error(
                ">> NEW_ADDED_MESSAGE - %s"
                % {"raw": message, "payload": payload}
            )
            yield payload
        await asyncio.sleep(0.001)


@Subscription("Subscription.dogUpdated")
async def subscription_dog_updated_subscription(
    parent_result, args, ctx, info
):
    logger.error(">> subscription_dog_updated_subscription")
    dog_updated_pubsub = _REDIS.pubsub(ignore_subscribe_messages=True)
    dog_updated_pubsub.subscribe(DOG_UPDATED_TOPIC)
    while True:
        message = dog_updated_pubsub.get_message()
        # Returns message only if its related to the wanted dog
        if message:
            payload = json.loads(message["data"])
            logger.error(
                ">> NEW_UPDATED_MESSAGE - %s"
                % {
                    "raw": message,
                    "payload": payload,
                    "arg[id]": args["id"],
                    "payload[id]": payload["id"],
                    "match": args["id"] == payload["id"],
                }
            )
            if payload["id"] == args["id"]:
                yield payload
        await asyncio.sleep(0.001)


@Resolver("Subscription.dogAdded")
async def subscription_dog_added_resolver(payload, args, ctx, info):
    return payload


@Resolver("Subscription.dogUpdated")
async def subscription_dog_updated_resolver(payload, args, ctx, info):
    return {**payload, "nickname": payload.get("nickname") or "Undefined"}
