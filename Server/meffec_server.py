"""The backend server for the Meffec system.
Stores information about connected clients and available effects.
Handles communication between app, controller and devices."""

from __future__ import annotations

import asyncio
import http
import json
import logging
import os

import data_models
import websockets
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("meffec_server.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("WEBSOCKET_TOKEN")
PORT = os.getenv("PORT")

if TOKEN is None:
    logger.critical("TOKEN is not set. Shutting down the server.")
    error = "TOKEN must be set in the environment or .env file."
    raise ValueError(error)

server_information = data_models.ServerInformation([], {}, None)


class QueryParameterProtocol(websockets.WebSocketServerProtocol):
    """Subclass of the regular server protocol so we can authenticate using the query parameter.
    It's not the most secure/recommended way of doing authentication but it's fine for our needs.
    """

    async def process_request(self, path: str, _) -> None | http.HTTPStatus:
        """Checks if the URL query token matches our stored token.

        Args:
            path: The URL path to check

        Returns:
            None if authenticated, unauthorized status if not.
        """
        token = path.split("?token=$")[1]  # That's one way to do it...
        logger.info("Processing new connection request.")

        if token != TOKEN:
            logger.warning("Unauthorized access attempt with token: %s", token)
            return (
                http.HTTPStatus.UNAUTHORIZED,
                [],
                b"Invalid or missing token\n",
            )

        return None


async def websocket_connection_handler(
    websocket: websockets.WebSocketServerProtocol,
) -> None:
    """Handles websocket communication for a single connection.

    Args:
        websocket: The websocket connection to handle.
    """
    client = data_models.ConnectedMeffecClient(websocket, None, None)
    server_information.connected_clients.append(client)
    logger.info("New client connected: %s", client)

    try:
        while True:
            message = await websocket.recv()
            logger.debug(
                "Received message from client: %s. Message: %s",
                client,
                message,
            )
            await handle_message(client, json.loads(message))

    except websockets.exceptions.ConnectionClosed:
        logger.info("Connection closed for client: %s", client)

    finally:
        if server_information.controller_client == client:
            server_information.controller_client = None
            logger.info("Controller client disconnected.")

        await disconnect_client(client)
        logger.info("Client removed: %s", client)


async def handle_message(
    client: data_models.ConnectedMeffecClient, message: dict
) -> None:
    """Checks the message type and calls the correct handling function.

    Args:
        client: The client to handle.
        message: The message to handle.
    """
    logger.debug(
        "Handling message from client: %s. Message: %s", client, message
    )
    match message["type"]:
        case data_models.CommunicationTypes.AUTHENTICATION.value:
            await authenticate_client(client, message["data"])

        case data_models.CommunicationTypes.INFORMATION.value:
            await process_information(message["data"])

        case data_models.CommunicationTypes.DEVICE_ACTION.value:
            await forward_device_action(message["data"])

        case _:
            await relay_message_to_all_clients(message)


async def authenticate_client(
    client: data_models.ConnectedMeffecClient, message: dict
) -> None:
    """Parses the authentication message sent by the client and
    runs the right functions based on the client type.

    Args:
        client: The client to handle.
        message: The authentication message to handle.
    """
    client.type = data_models.MeffecClientType.get_client_type(message["type"])
    client.name = message["name"]
    logger.info(
        "Authenticating client: %s. Client type: %s", client, client.type
    )

    if client.type == data_models.MeffecClientType.CONTROLLER:
        server_information.controller_client = client

    if client.type == data_models.MeffecClientType.APP:
        await send_effects_to_app_client(client)

    await send_connected_clients_to_controller()


async def disconnect_client(client: data_models.ConnectedMeffecClient) -> None:
    """Runs the function needed to disconnect a client.

    Args:
        client: The client to disconnect.
    """
    server_information.connected_clients.remove(client)
    await send_connected_clients_to_controller()


async def process_information(message: dict) -> None:
    """Handles the given information. Currently only stores
    the available effects.

    Args:
        message: The message with information to process.
    """
    logger.info("Processing information message: %s", message)
    if message["type"] == data_models.InformationTypes.AVAILABLE_EFFECTS.value:
        server_information.available_effects = message["data"]
        await send_effects_to_all_connected_app_clients()
        logger.info("Updated available effects.")


async def send_connected_clients_to_controller() -> None:
    """Sends connected client information to the controller."""
    if server_information.controller_client is None:
        logger.warning("No controller client available to send data.")
        return

    connected_clients = [
        client.get_controller_information()
        for client in server_information.connected_clients
    ]

    logger.info("Sending connected clients to controller.")
    await server_information.controller_client.websocket.send(
        json.dumps(
            {
                "type": data_models.CommunicationTypes.INFORMATION.value,
                "data": {
                    "type": data_models.InformationTypes.CONNECTED_CLIENTS.value,
                    "data": connected_clients,
                },
            }
        )
    )


async def send_effects_to_all_connected_app_clients() -> None:
    """Sends the stored available effects to all connected app clients."""
    for client in server_information.connected_clients:
        if client.type == data_models.MeffecClientType.APP:
            logger.info("Sending effects to app client: %s", client)
            await send_effects_to_app_client(client)


async def send_effects_to_app_client(
    client: data_models.ConnectedMeffecClient,
) -> None:
    """Sends the stored available effects to the given app client.

    Args:
        client: The client to send the effects to.
    """
    logger.info("Sending effects to app client: %s", client)
    await client.websocket.send(
        json.dumps(
            {
                "type": data_models.CommunicationTypes.INFORMATION.value,
                "data": {
                    "type": data_models.InformationTypes.AVAILABLE_EFFECTS.value,
                    "data": server_information.available_effects,
                },
            }
        )
    )


async def forward_device_action(device_action: dict) -> None:
    """Forwards the given device action to the device client.

    Args:
        message: The device action to forward.
    """
    logger.info(
        "Forwarding device action to device client: %s",
        device_action["device"],
    )

    for client in server_information.connected_clients:
        if client.type == data_models.MeffecClientType.DEVICE:
            await client.websocket.send(
                json.dumps(
                    {
                        "type": data_models.CommunicationTypes.DEVICE_ACTION.value,
                        "data": device_action["data"],
                    }
                )
            )


async def relay_message_to_all_clients(message: dict) -> None:
    """Sends the given message to all connected clients.

    Args:
        message: The message to send.
    """
    message_json = json.dumps(message)
    logger.info(
        "Relaying message to all connected clients. Message: %s", message
    )

    for client in server_information.connected_clients:
        try:
            await client.websocket.send(message_json)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Client disconnected during relay: %s", client)
            server_information.connected_clients.remove(client)


async def send_heartbeat_to_all_clients(interval: int = 5) -> None:
    """Sends a heartbeat trigger to all connected clients at the specified interval.

    Args:
        interval: The interval in seconds between each heartbeat.
    """
    while True:
        for client in server_information.connected_clients:
            try:
                await client.websocket.send(
                    json.dumps(
                        {
                            "type": data_models.CommunicationTypes.HEARTBEAT.value,
                            "data": "*imagine a heartbeat sound effect here*",
                        }
                    )
                )
                logger.debug("Sent heartbeat to client: %s", client)
            except websockets.exceptions.ConnectionClosed:
                logger.warning(
                    "Client disconnected during heartbeat: %s", client
                )
                await disconnect_client(client)

        await asyncio.sleep(interval)


async def start_websocket_server() -> None:
    """Starts the websocket server with our handler function
    and our custom query parameter protocol."""
    async with websockets.serve(
        websocket_connection_handler,
        "0.0.0.0",
        PORT,
        create_protocol=QueryParameterProtocol,
    ):

        logger.info("WebSocket server started on port : %s", PORT)
        asyncio.create_task(send_heartbeat_to_all_clients())

        await asyncio.Future()


if __name__ == "__main__":
    logger.info("Starting Meffec server...")
    try:
        asyncio.run(start_websocket_server())
    except Exception as e:
        logger.critical("Server encountered a critical error", exc_info=e)
