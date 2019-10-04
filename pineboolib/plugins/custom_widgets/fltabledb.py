"""FLTableDB Module."""

# -*- coding: utf-8 -*-
# pytype: skip-file
# type: ignore
from typing import Tuple, Any

try:
    MODULE: Any
    pluginType = (
        MODULE  # noqa: F821
    )  # La constante MODULE es parte de cómo PyQt carga los plugins. Es insertada por el loader en el namespace local
except Exception:
    pass


def moduleInformation() -> Tuple[str, str]:
    """Return module inormation."""

    return "pineboolib.fllegacy.fltabledb", ("FLTableDB")