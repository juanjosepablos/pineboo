"""Aqobjectquerylist module."""

from PyQt5 import QtCore, QtWidgets

from pineboolib.application import types
from typing import Union, Optional


def AQObjectQueryList(
    obj_: Union[QtCore.QObject, int, None],
    inherits_class: Optional[str] = None,
    object_name: Optional[str] = None,
    reg_ext_match: bool = False,
    recursirve_search: bool = False,
) -> types.Array:
    """Return a list with objects."""

    if isinstance(obj_, int) or obj_ is None:
        obj_ = QtWidgets.QApplication.topLevelWidgets()[0]

    if inherits_class is None:
        inherits_class = "QWidgets"

    class_ = getattr(QtWidgets, inherits_class, QtWidgets.QWidget)

    args_ = []

    args_.append(class_)

    if object_name and object_name == "":
        object_name = None

    args_.append(object_name)

    if recursirve_search:
        args_.append(QtCore.Qt.FindChildrenRecursively)

    return types.Array(obj_.findChildren(*args_))
