"""Dataclasses for the Meffec server."""

from dataclasses import dataclass
from enum import Enum
from typing import List

import websockets


class MeffecClientType(Enum):
    """Class that stores available client types."""

    APP = "app"
    CONTROLLER = "controller"
    DEVICE = "device"

    @classmethod
    def get_client_type(cls, type_name: str) -> "MeffecClientType":
        """Goes through our client types and returns the right type based on given name.

        Args:
            type_name: The type name to match.
        """
        for client_type in cls:
            if client_type.value == type_name:
                return client_type

        return None


class CommunicationTypes(Enum):
    """Class that stores types of communcation used in Meffec."""

    AUTHENTICATION = "authentication"
    DEVICE_ACTION = "device_action"
    HEARTBEAT = "heartbeat"
    INFORMATION = "information"
    PLAY_EFFECT = "play_effect"


class InformationTypes(Enum):
    """Class that stores types of information used in Meffec."""

    AVAILABLE_EFFECTS = "available_effects"
    CONNECTED_CLIENTS = "connected_clients"


@dataclass
class ConnectedMeffecClient:
    """Dataclass for storing information about a connected client."""

    websocket: websockets.WebSocketServerProtocol
    type: MeffecClientType
    name: str

    def get_controller_information(self) -> dict:
        """Returns only the type and name information in dict format to send to the controller.

        Returns:
            Dict containing type and name information.
        """
        return {"type": self.type.value, "name": self.name}


@dataclass
class ServerInformation:
    """Dataclass for storing information that should be available throughout the server code."""

    connected_clients: List[ConnectedMeffecClient]
    available_effects: dict
    controller_client: ConnectedMeffecClient
