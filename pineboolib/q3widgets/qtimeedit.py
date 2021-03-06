"""Qtimeedit module."""
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, Qt  # type: ignore
from typing import Optional, Union


class QTimeEdit(QtWidgets.QTimeEdit):
    """QTimeEdit class."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Inicialize."""
        super().__init__(parent)

        self.setDisplayFormat("hh:mm:ss A")

    def setTime(self, time: Union[Qt.QTime, str]) -> None:
        """Set time."""
        if not isinstance(time, Qt.QTime):
            t_list = time.split(":")
            time = Qt.QTime(int(t_list[0]), int(t_list[1]), int(t_list[2]))
        super().setTime(time)

    def getTime(self) -> str:
        """Return time."""

        return super().time().toString("hh:mm:ss")

    time: str = property(getTime, setTime)  # type: ignore [assignment] # noqa F821
