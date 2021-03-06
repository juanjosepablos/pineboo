"""Qlistview module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from pineboolib.core import decorators

from typing import Any, List, Optional, Union, cast


class QListView(QtWidgets.QWidget):
    """QListView class."""

    _resizeable: bool
    _clickable: bool
    _root_is_decorated: bool
    _default_rename_action: bool
    _tree: QtWidgets.QTreeView
    _cols_labels: List[str]
    _key: str
    _root_item: Any
    _current_row: int

    doubleClicked = QtCore.pyqtSignal(object)
    selectionChanged = QtCore.pyqtSignal(object)
    expanded = QtCore.pyqtSignal(object)
    collapsed = QtCore.pyqtSignal(object)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Inicialize."""

        super().__init__(parent=None)
        lay = QtWidgets.QVBoxLayout(self)
        self._tree = QtWidgets.QTreeView(self)
        lay.addWidget(self._tree)
        self._tree.setModel(QtGui.QStandardItemModel())
        self._cols_labels = []
        self._resizeable = True
        self._clickable = True
        self._default_rename_action = False
        self._root_is_decorated = False
        self._key = ""
        self._root_item = None
        self._current_row = -1
        cast(QtCore.pyqtSignal, self._tree.doubleClicked).connect(self.doubleClickedEmit)
        cast(QtCore.pyqtSignal, self._tree.clicked).connect(self.singleClickedEmit)
        cast(QtCore.pyqtSignal, self._tree.activated).connect(self.singleClickedEmit)

    def singleClickedEmit(self, index: Any) -> None:
        """Emit single clicked signal."""
        if not self._clickable:
            return

        if index.column() != 0:
            index = index.sibling(index.row(), 0)
        else:
            index = index.sibling(index.row(), index.column())
        item = index.model().itemFromIndex(index)

        self.selectionChanged.emit(item)

    def doubleClickedEmit(self, index: Any) -> None:
        """Emit double clicked signal."""
        if not self._clickable:
            return

        item = index.model().itemFromIndex(index)
        self.doubleClicked.emit(item)

    def addItem(self, t: str) -> None:
        """Add a new item."""

        from pineboolib.fllegacy.fllistviewitem import FLListViewItem

        self._current_row = self._current_row + 1
        item = FLListViewItem()
        item.setEditable(False)
        item.setText(t)
        if self._tree is not None:
            cast(QtGui.QStandardItemModel, self._tree.model()).setItem(self._current_row, 0, item)

    def setHeaderLabel(self, labels: Union[str, List[str]]) -> None:
        """Set header labels from a stringlist."""
        if isinstance(labels, str):
            labels = [labels]

        if self._tree is not None:
            cast(QtGui.QStandardItemModel, self._tree.model()).setHorizontalHeaderLabels(labels)
        self._cols_labels = labels

    def setColumnText(self, col: int, new_value: str) -> None:
        """Set Column text."""

        i = 0
        new_list = []
        for old_value in self._cols_labels:
            value = new_value if i == col else old_value
            new_list.append(value)

        self._cols_labels = new_list

    def addColumn(self, text: str) -> None:
        """Add a new column."""

        self._cols_labels.append(text)

        self.setHeaderLabel(self._cols_labels)

    def setClickable(self, c: bool) -> None:
        """Set clickable."""
        self._clickable = True if c else False

    def setResizable(self, r: bool) -> None:
        """Set resizeable."""
        self._resizeable = True if r else False

    def eventFilter(self, obj: QtCore.QObject, ev: QtCore.QEvent) -> bool:
        """Event filter."""

        if isinstance(ev, QtGui.QResizeEvent):
            if not self._resizeable:
                return False

        return super().eventFilter(obj, ev)

    def setItemMargin(self, s: int) -> None:
        """Set items margin."""

        style_ = "QTreeView::item#%s { border: 0px; padding: %spx; }" % (self.objectName(), s)
        self._tree.setStyleSheet(style_)

    # @decorators.NotImplementedWarn
    # def resizeEvent(self, e: QtCore.QEvent) -> None:
    #    """Process resize event."""
    #    if self._resizeable:
    #        super().resizeEvent(e)

    def clear(self) -> None:
        """Clear all data."""

        self._cols_labels = []

    @decorators.NotImplementedWarn
    def defaultRenameAction(self) -> bool:
        """Return default_rename_action enabled."""
        return self._default_rename_action

    @decorators.NotImplementedWarn
    def setDefaultRenameAction(self, b: bool) -> None:
        """Set default_rename_action enabled."""
        self._default_rename_action = b

    def model(self) -> QtGui.QStandardItemModel:
        """Return model index."""

        if self._tree is not None:
            return cast(QtGui.QStandardItemModel, self._tree.model())
        else:
            raise Exception("No hay _tree")
