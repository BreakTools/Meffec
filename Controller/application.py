"""The main QApplication that runs the Meffec controller."""

import sys
from pathlib import Path

import data_structures
import effects_handlers
import models
import scripts_handler
import websocket_handler
from PySide6 import QtGui, QtWidgets
from user_interface import MeffecControllerUserInterface


class MeffecController(QtWidgets.QApplication):
    """The main QApplication. Stores all data and facilitates connections
    between the websocket handler, models and views."""

    def __init__(self) -> None:
        super().__init__(sys.argv)
        self.setApplicationName("Meffec Controller")
        self.setApplicationDisplayName("Meffec Controller")
        self.setOrganizationDomain("breaktools.info")
        self.setOrganizationName("BreakTools")

        icon_pixmap = QtGui.QPixmap(
            str(Path(__file__).parent / "images" / "meffec_icon.png")
        )
        self.setWindowIcon(QtGui.QIcon(icon_pixmap))

        self.initialize_models()
        self.initialize_websocket_connection()
        self.initialize_effects_handlers()
        self.initialize_scripts_handler()

        self.user_interface = MeffecControllerUserInterface(
            self.log_model, self.connected_clients_model, self.effects_model
        )
        self.connect_ui_signals()

    def initialize_models(self) -> None:
        """Initializes and stores our models."""
        self.log_model = models.LogModel()
        self.connected_clients_model = models.ConnectedClientsModel()
        self.effects_model = models.EffectsModel()

    def initialize_websocket_connection(self) -> None:
        """Initializes the websocket connection and connects the signals.."""
        self.websocket_handler = websocket_handler.WebsocketHandler(
            self.log_model
        )
        self.websocket_handler.connected_clients_received.connect(
            self.connected_clients_model.set_clients
        )
        self.websocket_handler.connection_status_changed.connect(
            self.process_connection_change
        )
        self.websocket_handler.connect_to_server()

    def initialize_effects_handlers(self) -> None:
        """Initializes the effects handlers and stores them in a dataclass."""
        self.script_available_classes = data_structures.ScriptAvailableClasses(
            self.log_model,
            effects_handlers.AudioHandler(),
            effects_handlers.OSCHandler(),
            effects_handlers.DeviceHandler(),
            effects_handlers.TimingHandler(),
        )
        self.script_available_classes.device_handler.device_action_sent.connect(
            self.websocket_handler.send_device_action
        )

    def initialize_scripts_handler(self) -> None:
        """Initializes the scripts handler and starts the scripts scan."""
        self.scripts_handler = scripts_handler.ScriptsHandler(
            self.log_model, self.effects_model, self.script_available_classes
        )
        self.scripts_handler.effects_changed.connect(
            self.websocket_handler.send_effects_to_server
        )
        self.websocket_handler.play_effect_received.connect(
            self.scripts_handler.run_effect_by_category_and_name
        )
        self.scripts_handler.find_scripts()
        self.scripts_handler.start_watching_folder()

    def connect_ui_signals(self) -> None:
        """Connects the signals from our UI to functions on this application class."""
        self.user_interface.settings_changed.connect(self.process_new_settings)
        self.user_interface.run_effect.connect(
            self.scripts_handler.run_effect_by_class
        )
        self.user_interface.reindex_scripts.connect(
            self.scripts_handler.find_scripts
        )

    def process_new_settings(self) -> None:
        """Runs all the functions to utilize the new settings."""
        self.websocket_handler.websocket.close()
        self.scripts_handler.find_scripts()

    def process_connection_change(self, connected: bool) -> None:
        """Runs the proper functions if the connect status changes.

        Args:
            connected: If we are connected to the server.
        """
        self.user_interface.connection_status_changed(connected)

        if connected:
            self.websocket_handler.send_effects_to_server(
                self.effects_model.effect_categories
            )


if __name__ == "__main__":
    app = MeffecController()
    sys.exit(app.exec())
