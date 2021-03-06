"""Fluintvalidator module."""
# -*- coding: utf-8 -*-
from PyQt5 import QtGui
from typing import Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5 import QtWidgets  # noqa: F401


class FLUIntValidator(QtGui.QIntValidator):
    """FLUItValidator class."""

    _formatting: bool

    def __init__(self, minimum: int, maximum: int, parent: Optional["QtWidgets.QWidget"]) -> None:
        """Inicialize."""

        super().__init__(minimum, maximum, parent)

        self._formatting = False

    def validate(self, input_: str, pos_cursor: int) -> Tuple[QtGui.QValidator.State, str, int]:
        """Valiate a Value."""

        if not input_ or self._formatting:
            return (self.Acceptable, input_, pos_cursor)

        i_v = QtGui.QIntValidator(0, 1000000000, self)
        state = i_v.validate(input_, pos_cursor)

        ret_0 = self.Invalid if state[0] is self.Intermediate else state[0]
        ret_1 = state[1]
        ret_2 = state[2]

        return (ret_0, ret_1, ret_2)
