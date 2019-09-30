"""FLTable Module."""

# -*- coding: utf-8 -*-
# pytype: skip-file
# type: ignore
from typing import Tuple

MODULE = None

pluginType = (
    MODULE
)  # noqa: F281  # La constante MODULE es parte de cómo PyQt carga los plugins. Es insertada por el loader en el namespace local


def moduleInformation() -> Tuple[str, str]:
    """Return module inormation."""

    return "pineboolib.pncontrolsfactory", ("FLTable")