"""User interface code for the Meffec controller."""

import contextlib

import data_structures
import models
from PySide6 import QtCore, QtGui, QtWidgets


class MeffecControllerUserInterface(QtWidgets.QMainWindow):
    """The main Qt user interface for the Meffec controller."""

    settings_changed = QtCore.Signal()
    run_effect = QtCore.Signal(data_structures.Effect)
    reindex_scripts = QtCore.Signal()

    def __init__(
        self,
        log_model: models.LogModel,
        connected_clients_model: models.ConnectedClientsModel,
        effects_model: models.EffectsModel,
    ) -> None:
        """Calls the functions to set up our UI."""
        super().__init__()
        self.log_model = log_model

        self.setWindowTitle("Meffec Controller")
        self.create_menu_bar()

        self.create_user_interface(
            log_model, connected_clients_model, effects_model
        )
        self.show()

    def create_user_interface(
        self,
        log_model: models.LogModel,
        connected_clients_model: models.ConnectedClientsModel,
        effects_model: models.EffectsModel,
    ) -> None:
        """Creates the Meffec controller user interface."""
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        main_widget.setLayout(main_layout)

        horizontal_split_widget = QtWidgets.QWidget()
        horizontal_split_layout = QtWidgets.QHBoxLayout()
        horizontal_split_layout.setContentsMargins(0, 0, 0, 0)
        horizontal_split_widget.setLayout(horizontal_split_layout)
        main_layout.addWidget(horizontal_split_widget, 3)

        vertical_split_widget = QtWidgets.QWidget()
        vertical_split_layout = QtWidgets.QVBoxLayout()
        vertical_split_widget.setLayout(vertical_split_layout)
        vertical_split_layout.setContentsMargins(0, 0, 0, 0)
        horizontal_split_layout.addWidget(vertical_split_widget)

        horizontal_split_layout.addWidget(
            self.get_effects_widget(effects_model)
        )
        vertical_split_layout.addWidget(self.get_info_widget())
        vertical_split_layout.addWidget(
            self.get_clients_widget(connected_clients_model)
        )

        main_layout.addWidget(self.get_logs_widget(log_model), 2)

        self.setCentralWidget(main_widget)

    def create_menu_bar(self) -> None:
        """Creates the native menu settings item."""
        menu_bar = self.menuBar()
        settings_menu = QtWidgets.QMenu("Preferences")
        menu_bar.addMenu(settings_menu)

        open_settings_action = QtGui.QAction(
            "Settings",
            self,
            statusTip="Opens the Meffec Controller settings",
            triggered=self.open_settings_dialog,
        )
        settings_menu.addAction(open_settings_action)

        edit_menu = QtWidgets.QMenu("Edit")
        menu_bar.addMenu(edit_menu)
        reindex_scripts_action = QtGui.QAction(
            "Reindex scripts",
            self,
            statusTip="Reindexes and reloads all scripts.",
            triggered=self.emit_reindex_signal,
        )
        edit_menu.addAction(reindex_scripts_action)

    def open_settings_dialog(self) -> None:
        """Opens the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.settings_changed.emit()

    def get_info_widget(self) -> QtWidgets.QWidget:
        """Creates and returns the information widget.

        Returns:
            Info widget
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        layout.addWidget(QtWidgets.QLabel("Connection status"))

        self.connection_label = QtWidgets.QLabel(
            "<font color='red'><b>Not connected to Meffec server.</b></font>"
        )
        layout.addWidget(self.connection_label)

        return widget

    def get_clients_widget(
        self, connected_clients_model: models.ConnectedClientsModel
    ) -> QtWidgets.QWidget:
        """Creates and returns the clients widget.

        Returns:
            Client widget.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        label = QtWidgets.QLabel("Connected clients")
        layout.addWidget(label)

        clients_list_view = QtWidgets.QListView()
        clients_list_view.setModel(connected_clients_model)
        layout.addWidget(clients_list_view)

        return widget

    def get_effects_widget(
        self, effects_model: models.EffectsModel
    ) -> QtWidgets.QWidget:
        """Creates and returns the effects widget.

        Returns:
            Effects widget.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        label = QtWidgets.QLabel("Loaded effects")
        layout.addWidget(label)

        self.effects_tree_view = QtWidgets.QTreeView()
        self.effects_tree_view.setModel(effects_model)
        layout.addWidget(self.effects_tree_view)

        execute_effect_button = QtWidgets.QPushButton("Execute effect")
        execute_effect_button.clicked.connect(self.run_selected_effect)
        layout.addWidget(execute_effect_button)

        return widget

    def get_logs_widget(self, log_model: models.LogModel) -> QtWidgets.QWidget:
        """Creates and returns the logs widget.

        Returns:
            Logs widget.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        label = QtWidgets.QLabel("Logs")
        layout.addWidget(label)

        logs_list_view = QtWidgets.QListView()
        logs_list_view.setModel(log_model)
        layout.addWidget(logs_list_view)

        self.log_model.layoutChanged.connect(logs_list_view.scrollToBottom)

        return widget

    def connection_status_changed(self, connected: bool) -> None:
        """Updates the connected status pixmap according to new state."""
        if connected:
            self.connection_label.setText(
                "<font color='green'><b>Connected to Meffec server!</b></font>"
            )

        else:
            self.connection_label.setText(
                "<font color='red'><b>Not connected to Meffec server.</b></font>"
            )

    def run_selected_effect(self) -> None:
        """Runs the selected effect. Will give an IndexError if we don't have
        anything selected so we suppress it."""
        with contextlib.suppress(IndexError):
            self.run_effect.emit(
                self.effects_tree_view.selectionModel()
                .selectedIndexes()[0]
                .internalPointer()
                .effect_data
            )

    def emit_reindex_signal(self, _) -> None:
        """The triggered QAction passes an argument so we need another function to emit the signal."""
        self.reindex_scripts.emit()


class SettingsDialog(QtWidgets.QDialog):
    """Dialog that allows the user to configure the Meffec controller."""

    def __init__(self, parent=None) -> None:
        """Initializes the settings dialog."""
        super().__init__(parent)
        self.setWindowTitle("Meffec Settings")
        self.settings = QtCore.QSettings()

        self.create_user_interface()
        self.resize(500, 300)

    def create_user_interface(self) -> None:
        """Creates the settings user interface."""
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.get_effects_folder_widget())
        self.layout.addWidget(self.get_meffec_server_address_widget())
        self.layout.addWidget(self.get_authentication_token_widget())
        self.layout.addWidget(self.get_osc_server_address_widget())

        self.button_box = self.get_button_box()
        self.layout.addWidget(self.button_box)

    def get_effects_folder_widget(self) -> QtWidgets.QWidget:
        """Creates and returns the effects folder UI section.

        Returns:
            Effects folder widget.
        """
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(2)
        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)

        label = QtWidgets.QLabel("Effects scripts folder")
        label.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(label)

        input_layout = QtWidgets.QHBoxLayout()

        self.folder_path = QtWidgets.QLineEdit()
        self.folder_path.setText(
            self.settings.value(
                data_structures.SettingsKey.EFFECTS_SCRIPTS_FOLDER.value
            )
        )
        self.folder_path.setPlaceholderText("/path/to/folder")
        input_layout.addWidget(self.folder_path, 6)

        select_folder_button = QtWidgets.QPushButton("Select folder")
        select_folder_button.clicked.connect(self.select_effects_folder)
        input_layout.addWidget(select_folder_button, 2)

        main_layout.addLayout(input_layout)

        return widget

    def get_meffec_server_address_widget(self) -> QtWidgets.QWidget:
        """Creates and returns the Meffec server address UI section.

        Returns:
            Meffec server address widget.
        """
        layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel("Meffec Server URL"))

        self.meffec_server_address = QtWidgets.QLineEdit()
        self.meffec_server_address.setText(
            self.settings.value(
                data_structures.SettingsKey.MEFFEC_SERVER_URL.value
            )
        )
        self.meffec_server_address.setPlaceholderText(
            "wss://meffec.domainname.com"
        )

        layout.addWidget(self.meffec_server_address)
        return widget

    def get_authentication_token_widget(self) -> QtWidgets.QWidget:
        """Creates and returns the Meffec server address UI section.

        Returns:
            Meffec server address widget.
        """
        layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel("Authentication token"))

        self.authentication_token = QtWidgets.QLineEdit()
        self.authentication_token.setText(
            self.settings.value(
                data_structures.SettingsKey.AUTHENTICATION_TOKEN.value
            )
        )
        self.authentication_token.setPlaceholderText("YOURTOKEN")
        self.authentication_token.setEchoMode(
            QtWidgets.QLineEdit.EchoMode.Password
        )

        layout.addWidget(self.authentication_token)
        return widget

    def get_osc_server_address_widget(self) -> QtWidgets.QWidget:
        """Creates and returns the OSC server address UI section.

        Returns:
            OSC server address widget.
        """
        layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel("OSC Server URL (if using)"))

        self.osc_server_address = QtWidgets.QLineEdit()
        self.osc_server_address.setText(
            self.settings.value(
                data_structures.SettingsKey.OSC_SERVER_URL.value
            )
        )
        self.osc_server_address.setPlaceholderText("127.0.0.1:25565")

        layout.addWidget(self.osc_server_address)
        return widget

    def select_effects_folder(self) -> None:
        """Opens a folder selection dialog and sets the selected path."""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Effects Folder"
        )
        if folder_path:
            self.folder_path.setText(folder_path)

    def get_button_box(self) -> QtWidgets.QWidget:
        """Creates and returns the button box with OK and Cancel buttons."""
        button_box = QtWidgets.QDialogButtonBox(QtCore.Qt.Horizontal)
        button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def accept(self) -> None:
        """Accepts user input and stores settings."""
        self.settings.setValue(
            data_structures.SettingsKey.EFFECTS_SCRIPTS_FOLDER.value,
            self.folder_path.text(),
        )
        self.settings.setValue(
            data_structures.SettingsKey.MEFFEC_SERVER_URL.value,
            self.meffec_server_address.text(),
        )
        self.settings.setValue(
            data_structures.SettingsKey.AUTHENTICATION_TOKEN.value,
            self.authentication_token.text(),
        )
        self.settings.setValue(
            data_structures.SettingsKey.OSC_SERVER_URL.value,
            self.osc_server_address.text(),
        )
        super().accept()
