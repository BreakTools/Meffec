"""Data structures for the Meffec Controllers. Here I store some dataclasses and enum classes."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Any, List

import effects_handlers


class SettingsKey(Enum):
    """Class for storing string names of setting keys for use with QSettings."""

    EFFECTS_SCRIPTS_FOLDER = "settings/effects_scripts_folder"
    MEFFEC_SERVER_URL = "settings/meffec_server_url"
    OSC_SERVER_URL = "settings/osc_server_url"
    AUTHENTICATION_TOKEN = "settings/authentication_token"


@dataclass
class ConnectedMeffecClient:
    """Dataclass for storing information about a connected client."""

    type: str
    name: str


@dataclass
class ScriptAvailableClasses:
    """Class that stores the classes that are passed to the effect scripts."""

    log_model: Any  # CiRculAr imPorT
    audio_handler: effects_handlers.AudioHandler
    osc_handler: effects_handlers.OSCHandler
    device_handler: effects_handlers.DeviceHandler
    timing_handler: effects_handlers.TimingHandler


@dataclass
class Effect:
    """Dataclass for storing an effect and it's module for execution."""

    name: str
    description: str
    module: ModuleType
    script_path: Path

    def get_app_data(self) -> dict:
        """Returns only the data needed for display in the app.

        Returns:
            Dict with app data.
        """
        return {"name": self.name, "description": self.description}


@dataclass
class EffectsCategory:
    """Dataclass for storing an effects category."""

    name: str
    effects: List[Effect]

    def get_app_data(self) -> dict:
        """Returns only the data needed for display in the app.

        Returns:
            Dict with app data.
        """
        effects = [effect.get_app_data() for effect in self.effects]
        return {"name": self.name, "effects": effects}


@dataclass
class Ambiance:
    """Dataclass for storing ambiance data."""

    category: str
    audio_player: effects_handlers.FadeableAudioPlayer


@dataclass
class DeviceAction:
    """Dataclass for storing device action information."""

    device: str
    data: dict
