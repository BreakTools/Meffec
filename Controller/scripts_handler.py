"""Code for handling scanning, loading and running the effects scripts."""

from __future__ import annotations

import importlib
from pathlib import Path
from types import ModuleType

import data_structures
import models
from PySide6 import QtCore
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ScriptChangeHandler(FileSystemEventHandler):
    """Handles file change events for script reloading."""

    def __init__(self, scripts_handler: ScriptsHandler, folder: Path) -> None:
        """Initializes the handler with the scripts handler and folder to monitor."""
        super().__init__()
        self.scripts_handler = scripts_handler
        self.folder = folder

    def on_modified(self, event):
        """Called when a file is modified."""
        if event.src_path.endswith(".py"):
            self.scripts_handler.reload_script(Path(event.src_path))

    def on_created(self, event):
        """Called when a new file is created."""
        if event.src_path.endswith(".py"):
            self.scripts_handler.find_scripts()

    def on_deleted(self, event):
        if event.src_path.endswith(".py"):
            self.scripts_handler.find_scripts()


class ScriptsHandler(QtCore.QObject):
    """Class that handles the scanning, loading, and running of effects scripts."""

    effects_changed = QtCore.Signal(list)

    def __init__(
        self,
        log_model: models.LogModel,
        effects_model: models.EffectsModel,
        script_available_classes: data_structures.ScriptAvailableClasses,
    ) -> None:
        """Initializes the scripts handler."""
        super().__init__()
        self.log_model = log_model
        self.effects_model = effects_model
        self.script_available_classes = script_available_classes
        self.observer = Observer()
        self.folder_to_watch = self.get_scripts_folder()

    def start_watching_folder(self) -> None:
        """Starts the watchdog observer to monitor the scripts folder."""
        self.event_handler = ScriptChangeHandler(self, self.folder_to_watch)
        self.observer.schedule(
            self.event_handler, str(self.folder_to_watch), recursive=False
        )
        self.observer.start()

    def stop_watching_folder(self) -> None:
        """Stops the watchdog observer."""
        self.observer.stop()
        self.observer.join()

    def find_scripts(self) -> None:
        """Scans the specified folder for effect scripts and stores them in the model."""
        self.log_model.log("Indexing all scripts.")
        folder_to_scan = self.get_scripts_folder()
        effects_categories = self.get_categories_from_scripts_folder(
            folder_to_scan
        )
        self.effects_changed.emit(effects_categories)
        self.effects_model.setup_effects_tree(effects_categories)

    def reload_script(self, script_path: Path) -> None:
        """Reloads or loads a script when it is modified or created."""
        self.log_model.log(f"Reloading script: {script_path.name}")
        effect = self.get_effect_by_script_path(script_path)
        effect.module = self.load_script_module(script_path)

    def get_scripts_folder(self) -> Path:
        """Retrieves the folder path to scan for effect scripts from settings.

        Returns:
            The script folder from the stored settings.
        """
        settings = QtCore.QSettings()
        folder_path = settings.value(
            data_structures.SettingsKey.EFFECTS_SCRIPTS_FOLDER.value
        )
        return Path(folder_path)

    def get_categories_from_scripts_folder(
        self, folder: Path
    ) -> list[data_structures.EffectsCategory]:
        """Scans the folder for Python scripts and categorizes the effects.

        Args:
            folder: The folder to scan.

        Returns:
            All the effects in their right categories.
        """
        effects_categories = []
        for script_path in folder.glob("*.py"):
            module = self.load_script_module(script_path)

            if module and hasattr(module, "get_effect_info"):
                effect_info = module.get_effect_info()
                self.add_effect_to_category(
                    effect_info, effects_categories, module, script_path
                )

            else:
                self.log_model.log(
                    f"Could not load script {script_path.stem} because it has no get_effect_info function."
                )

        return effects_categories

    def load_script_module(self, script_path: Path) -> ModuleType:
        """Loads a Python script as a module.

        Args:
            script_path: The path to the script to load.

        Returns:
            The loaded module.
        """
        spec = importlib.util.spec_from_file_location(
            script_path.stem, script_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    def add_effect_to_category(
        self,
        effect_info: dict,
        effects_categories: list,
        module: ModuleType,
        script_path: Path,
    ) -> None:
        """Adds the effect to the appropriate category or creates a new one.

        Args:
            effect_info: The effect info as provided by the script.
            effect_categories: The already stored categories.
            script_path: The path to the script.
        """
        try:
            effect = data_structures.Effect(
                effect_info["name"],
                effect_info["description"],
                module,
                script_path,
            )

            for category in effects_categories:
                if category.name == effect_info["category"]:
                    category.effects.append(effect)
                    return

        except KeyError:
            self.log_model.log(
                f"Could not find proper info keys for script {script_path.stem}. Skipped."
            )
            return

        effects_categories.append(
            data_structures.EffectsCategory(effect_info["category"], [effect])
        )

    def run_effect_by_class(self, effect: data_structures.Effect) -> None:
        """Runs the given effect with the available classes.

        Args:
            effect: The effect to run.
        """
        if hasattr(effect.module, "run_effect"):
            self.log_model.log(f"Running effect {effect.name}.")
            try:
                effect.module.run_effect(self.script_available_classes)
            except Exception as error:
                self.log_model.log(
                    f"Could not run effect {effect.name}: {error}"
                )
        else:
            self.log_model.log(
                f"Could not run effect {effect.name} because it has no run_effect function."
            )

    def run_effect_by_category_and_name(
        self, category: str, name: str
    ) -> None:
        """Uses the category and name to find the effect on the model and runs it.

        Args:
            category: The name of the category to search.
            name: The name of the effect to execute.
        """
        self.run_effect_by_class(
            self.get_effect_by_category_and_name(category, name)
        )

    def get_effect_by_category_and_name(
        self, category: str, name: str
    ) -> data_structures.Effect:
        """Uses the category and name to find the effect on the model and returns it.

        Args:
            category: The name of the category to search.
            name: The name of the effect to to find.
        """
        for category_item in self.effects_model.root_item.children:
            if category_item.get_display_text() != category:
                continue

            for effect_item in category_item.children:
                if effect_item.get_display_text() == name:
                    return effect_item.effect_data

        return None

    def get_effect_by_script_path(
        self, script_path: Path
    ) -> data_structures.Effect:
        """Uses the scrpt path to find the effect on the model and returns it.

        Args:
            script_path: Path to the script.
        """
        for category_item in self.effects_model.root_item.children:
            for effect_item in category_item.children:
                if effect_item.get_script_path() == script_path:
                    return effect_item.effect_data

        return None
