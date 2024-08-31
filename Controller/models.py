"""Qt models for the Meffec controller."""

from __future__ import annotations

from pathlib import Path

import data_structures
from PySide6 import QtCore


class ConnectedClientsModel(QtCore.QAbstractListModel):
    """Models for storing connected clients."""

    def __init__(self) -> None:
        """Initializes the connected clients model."""
        super().__init__()
        self.clients = []

    def data(
        self, index: QtCore.QModelIndex, role: QtCore.Qt.DisplayRole
    ) -> str:
        """Returns the connected client data stored on the model for the view to display.

        Args:
            index: The index to retrieve data for.
            role: The role this data will play.

        Returns:
            The name of the connected client at the specified index.
        """
        if role != QtCore.Qt.DisplayRole:
            return None

        return self.clients[index.row()].name

    def flags(self, _) -> QtCore.Qt.ItemFlags:
        """Returns the flags for each item, disabling selection.

        Args:
            _: The index of the item (unused).

        Returns:
            The item flags, indicating the item is enabled but not selectable.
        """
        return QtCore.Qt.ItemIsEnabled

    def set_clients(
        self, clients: list[data_structures.ConnectedMeffecClient]
    ) -> None:
        """Stores the new clients list on the model.

        Args:
            clients: The new list of clients.
        """
        self.clients = clients
        self.layoutChanged.emit()

    def rowCount(self, _) -> int:
        """Called by the Qt view to get the length of our data.

        Args:
            _: The index of the item (unused).

        Returns:
            The amount of rows the list view should have.
        """
        return len(self.clients)


class LogModel(QtCore.QStringListModel):
    """Model used for storing logs to be displayed in UI."""

    def log(self, log_text: str) -> None:
        """Logs the given text by storing it on this model.

        Args:
            log_text: The text to log and store in the model.
        """
        current_logs = self.stringList()
        current_logs.append(log_text)
        self.setStringList(current_logs)
        self.layoutChanged.emit()

    def flags(self, _) -> QtCore.Qt.ItemFlags:
        """Returns the flags for each item, disabling selection.

        Args:
            _: The index of the item (unused).

        Returns:
            The item flags, indicating the item is enabled but not selectable.
        """
        return QtCore.Qt.ItemIsEnabled


class EffectItem:
    """Class used for storing effect data in our tree model."""

    def __init__(
        self,
        parent: EffectItem,
        display_text: str,
        effect_data: data_structures.Effect,
    ):
        """Initializes the effect item.

        Args:
            parent: The parent item in the tree.
            display_text: The text to display for this effect item.
            effect_data: The effect data associated with this item.
        """
        self.parent = parent
        self.children = []
        self.display_text = display_text
        self.effect_data = effect_data

    def get_display_text(self):
        """Gets the text to display in the UI tree.

        Returns:
            The display text for this effect item.
        """
        return self.display_text

    def get_script_path(self) -> Path:
        """Returns the stored effect script path.

        Returns:
            The effect script path.
        """
        return self.effect_data.script_path

    def add_child(self, item: EffectItem):
        """Adds a child to this item in the tree.

        Args:
            item: The child item to add.
        """
        self.children.append(item)

    def get_child(self, row: int) -> EffectItem | None:
        """Returns the stored child for the given row.

        Args:
            row: The row of the child to retrieve.

        Returns:
            The child effect item at the specified row, or None if the row is out of bounds.
        """
        if row >= len(self.children):
            return None

        return self.children[row]

    def get_child_count(self):
        """Returns the total amount of children stored on this item.

        Returns:
            The number of children items.
        """
        return len(self.children)

    def get_parent(self):
        """Returns the parent of this item.

        Returns:
            The parent effect item, or None if this item is the root.
        """
        return self.parent

    def get_row(self):
        """Returns the row this item is in.

        Returns:
            The index of this item within its parent's children, or 0 if it is the root item.
        """
        if self.parent:
            return self.parent.children.index(self)

        return 0


class EffectsModel(QtCore.QAbstractItemModel):
    """Tree model used for storing all effects in their categories."""

    def __init__(self):
        """Initializes the effects model."""
        super().__init__()
        self.root_item = EffectItem(None, None, None)
        self.effect_categories = []

    def setup_effects_tree(
        self,
        categories: list[data_structures.EffectsCategory],
    ) -> None:
        """Sets up the effects tree with the given categories.

        Args:
            categories: The list of effect categories to populate the tree with.
        """
        self.effect_categories = categories
        self.root_item = EffectItem(None, None, None)

        for category in categories:
            category_item = EffectItem(self.root_item, category.name, None)
            self.root_item.add_child(category_item)

            for effect in category.effects:
                effect_item = EffectItem(category_item, effect.name, effect)
                category_item.add_child(effect_item)

        self.layoutChanged.emit()

    def data(
        self, index: QtCore.QModelIndex, role: QtCore.Qt.DisplayRole
    ) -> str:
        """Retrieves the display data for the effect stored on the given index.

        Args:
            index: The model index to retrieve data for.
            role: The role for the data retrieval.

        Returns:
            The display text for the effect at the specified index.
        """
        if role == QtCore.Qt.DisplayRole:
            return index.internalPointer().get_display_text()

        return None

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        """Returns the flags for the given index. Only effects are selectable in the UI.

        Args:
            index: The index of the item.

        Returns:
            The item flags, indicating if the item is selectable based on its data.
        """
        try:
            if index.internalPointer().effect_data is None:
                return QtCore.Qt.ItemIsEnabled
        except AttributeError:
            # Happens sometimes and I'm not sure why
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(
        self,
        _,
        orientation: QtCore.Qt.Orientation,
        role: QtCore.Qt.DisplayRole,
    ):
        """Returns the text that should be displayed in the horizontal header.

        Args:
            _: The section of the header (unused).
            orientation: The orientation of the header.
            role: The role for the header data.

        Returns:
            The header text to display.
        """
        if (
            orientation == QtCore.Qt.Horizontal
            and role == QtCore.Qt.DisplayRole
        ):
            return "Category / Effect"

        return None

    def index(self, row: int, column: int, parent_index: QtCore.QModelIndex):
        """Creates the index for the given row and column.

        Args:
            row: The row of the item.
            column: The column of the item.
            parent_index: The parent index of the item.

        Returns:
            The created model index for the specified row and column, or an invalid index if no item is found.
        """
        parent_item = (
            parent_index.internalPointer()
            if parent_index.isValid()
            else self.root_item
        )

        child_item = parent_item.get_child(row)
        if child_item is not None:
            return self.createIndex(row, column, child_item)

        return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex) -> None:
        """Gets the parent for the given index.

        Args:
            index: The model index of the item.

        Returns:
            The parent index for the specified item, or an invalid index if the item is at the root.
        """
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.get_parent()

        if parent_item == self.root_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.get_row(), 0, parent_item)

    def rowCount(self, index: QtCore.QModelIndex) -> int:
        """Returns the amount of rows the tree view should display.

        Args:
            index: The model index for which to count rows.

        Returns:
            The number of child items for the specified index, or the root item if the index is invalid.
        """
        if not index.isValid():
            return self.root_item.get_child_count()

        return index.internalPointer().get_child_count()

    def columnCount(self, _) -> int:
        """Returns the amount of columns. We only have one.

        Args:
            _: The index of the item (unused).

        Returns:
            The number of columns, which is always 1.
        """
        return 1
