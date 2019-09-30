"""QCombobox module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets  # type: ignore


from typing import Optional, Union, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .qframe import QFrame  # noqa: F401
    from .qgroupbox import QGroupBox  # noqa: F401


class QComboBox(QtWidgets.QComboBox):
    """QComboBox class."""

    def __init__(self, parent: Optional[Union["QFrame", "QGroupBox"]] = None) -> None:
        """Inicialize."""

        super().__init__(parent)
        self.setEditable(False)

    def insertStringList(self, strl: List[str]) -> None:
        """Set items from an string list."""

        self.insertItems(len(strl), strl)

    def setReadOnly(self, b: bool) -> None:
        """Set read only."""

        super().setEditable(not b)

    def getCurrentItem(self) -> Any:
        """Return current item selected."""

        return super().currentIndex

    def setCurrentItem(self, i: Union[str, int]) -> None:
        """Set current item."""

        pos = -1
        if isinstance(i, str):
            pos = 0
            size_ = self.model().rowCount()
            for n in range(size_):
                item = self.model().index(n, 0)
                if item.data() == i:
                    pos = n
                    break

        else:
            pos = i

        super().setCurrentIndex(pos)

    def getCurrentText(self) -> str:
        """Return current item text."""

        return super().currentText()

    def setCurrentText(self, value: str) -> None:
        """Set current item text."""

        super().setCurrentText(value)

    currentItem = property(getCurrentItem, setCurrentItem, None, "get/set current item index")
    currentText = property(  # type: ignore
        getCurrentText, setCurrentText, None, "get/set current text"
    )