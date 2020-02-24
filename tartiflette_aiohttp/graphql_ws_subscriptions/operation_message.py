import json
from typing import Any, Union, Dict, Optional

from .constants import OperationMessageType

__all__ = ("parse_message",)


class OperationMessage:
    """
    TODO:
    """

    __slots__ = ("id", "type", "payload")

    def __init__(
        self, id_: str, type_: "OperationMessageType", payload: Any
    ) -> None:
        """
        TODO:
        :param id_: TODO:
        :param type_: TODO:
        :param payload: TODO:
        :type id_: TODO:
        :type type_: TODO:
        :type payload: TODO:
        """
        self.id = id_
        self.type = OperationMessageType(type_)
        self.payload = payload


def parse_message(message: Optional[str]) -> "OperationMessage":
    """
    TODO:
    :param message: TODO:
    :type message: TODO:
    :return: TODO:
    :rtype: TODO:
    :raises TypeError: TODO:
    """
    try:
        json_message = json.loads(message)
    except Exception:
        raise TypeError("Message must be a valid JSON object.")

    if not isinstance(json_message, dict):
        raise TypeError("Message must be a valid JSON object.")

    payload = json_message.get("payload", {})
    if payload is not None and not isinstance(payload, dict):
        raise TypeError("Payload must be a valid JSON object.")

    return OperationMessage(
        json_message.get("id"), json_message.get("type"), payload
    )
