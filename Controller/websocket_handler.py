"""Websockets handling code for the Meffec controller."""

from __future__ import annotations

import json

import data_structures
import models
from PySide6 import QtCore, QtNetwork, QtWebSockets


class WebsocketHandler(QtCore.QObject):
    """Class that handles all websocket communication."""

    connection_status_changed = QtCore.Signal(bool)
    connected_clients_received = QtCore.Signal(list)
    play_effect_received = QtCore.Signal(str, str)

    def __init__(self, log_model: models.LogModel, parent=None) -> None:
        """Initializes the websocket handler."""
        super().__init__(parent)
        self.log_model = log_model
        self.create_websocket()

    def create_websocket(self) -> None:
        """Creates the websocket object and connects the signals."""
        self.websocket = QtWebSockets.QWebSocket()
        self.websocket.connected.connect(self.on_server_connected)
        self.websocket.disconnected.connect(self.on_server_disconnected)
        self.websocket.textMessageReceived.connect(self.on_message_received)

    def connect_to_server(self) -> None:
        """Connects to the websocket server using the stored server URL."""
        settings = QtCore.QSettings()
        server_url = settings.value(
            data_structures.SettingsKey.MEFFEC_SERVER_URL.value
        )
        token = settings.value(
            data_structures.SettingsKey.AUTHENTICATION_TOKEN.value
        )
        final_address = f"{server_url}/?token=${token}"
        self.log_model.log(f"Connecting to websocket URL {server_url}.")
        self.websocket.open(final_address)

    def on_server_connected(self) -> None:
        """Runs when the websocket is connected to authenticate."""
        self.log_model.log("Successfully connected to websocket server.")
        self.connection_status_changed.emit(True)
        self.websocket.sendTextMessage(
            json.dumps(
                {
                    "type": "authentication",
                    "data": {
                        "type": "controller",
                        "name": "Controller",
                    },
                }
            )
        )

    def on_server_disconnected(self) -> None:
        """Runs when we disconnect from the server.
        Tries reconnecting after 3 seconds."""
        self.connection_status_changed.emit(False)
        self.log_model.log(
            "Disconnected from websocket server. Attempting reconnect in 3 seconds."
        )
        QtCore.QTimer.singleShot(3000, self.connect_to_server)

    def on_message_received(self, message: str) -> None:
        """Runs whenever we receive a message from the server.

        Args:
            message: The server JSON message in string format.
        """
        message = json.loads(message)

        match message["type"]:
            case "information":
                self.process_information_data(message["data"])

            case "play_effect":
                self.play_effect_received.emit(
                    message["data"]["category"], message["data"]["name"]
                )

    def process_information_data(self, information: dict) -> None:
        """Processes information data received from the server.

        Args:
            information: The info to process.
        """
        match information["type"]:
            case "connected_clients":
                self.parse_connected_clients(information["data"])

    def parse_connected_clients(self, connected_clients: dict) -> None:
        """Parses the dict data of connected clients into our nice and cozy dataclass.

        Args:
            connected_clients: Clients data in dict format.
        """
        parsed_connected_clients = [
            data_structures.ConnectedMeffecClient(
                client["type"], client["name"]
            )
            for client in connected_clients
        ]
        self.log_model.log(
            f"Received connected clients: {', '.join([client.name for client in parsed_connected_clients])}."
        )
        self.connected_clients_received.emit(parsed_connected_clients)

    def send_effects_to_server(
        self, effect_categories: list[data_structures.EffectsCategory]
    ) -> None:
        """Reformats the given effects and sends them to the server.

        Args:
            effect_categories: The categories and their effects to send to server.
        """
        if (
            self.websocket.state()
            != QtNetwork.QAbstractSocket.SocketState.ConnectedState
        ):
            self.log_model.log(
                "Skipped sending effects to server as we're not connected."
            )
            return

        self.log_model.log("Sending effects to server.")
        data_to_send = [
            effect_category.get_app_data()
            for effect_category in effect_categories
        ]
        self.websocket.sendTextMessage(
            json.dumps(
                {
                    "type": "information",
                    "data": {
                        "type": "available_effects",
                        "data": data_to_send,
                    },
                }
            )
        )

    def send_device_action(
        self, device_action: data_structures.DeviceAction
    ) -> None:
        """Sends the given device action to the server.

        Args:
            device_action: Device action to send.
        """
        if (
            self.websocket.state()
            != QtNetwork.QAbstractSocket.SocketState.ConnectedState
        ):
            self.log_model.log(
                "Skipped sending device action to server as we're not connected."
            )
            return

        self.log_model.log(f"Sending device action to {device_action.device}.")
        self.websocket.sendTextMessage(
            json.dumps(
                {
                    "type": "device_action",
                    "data": {
                        "device": device_action.device,
                        "data": device_action.data,
                    },
                }
            )
        )
