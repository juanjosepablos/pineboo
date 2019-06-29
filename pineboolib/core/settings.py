# -*- coding: utf-8 -*-
import logging
import json

from PyQt5.QtCore import QSettings, QSize

logger = logging.getLogger("core.settings")


class PinebooSettings(QSettings):
    def __init__(self, name=""):
        format = QSettings.IniFormat  # QSettings.NativeFormat - usar solo ficheros ini.
        scope = QSettings.UserScope
        organization = "Eneboo"
        application = "Pineboo" + name
        super().__init__(format, scope, organization, application)

    def dump_value(self, value):
        if isinstance(value, QSize):
            value = {"__class__": "QSize", "width": value.width(), "height": value.height()}
        return json.dumps(value)

    def load_value(self, value):
        value = json.loads(value)
        if value is dict and "__class__" in value:
            classname = value["__class__"]
            if classname == "QSize":
                return QSize(value["width"], value["height"])
            else:
                raise ValueError("Unknown classname %r" % classname)
        return value

    def value(self, key, default=None):
        value = super().value(key, None)
        if value is None:
            return default
        try:
            return self.load_value(value)
        except Exception as exc:
            # No format, just string
            logger.debug("Error trying to parse json for %s: %s (%s)", key, exc, value)
            return value

    def set_value(self, key, value):
        return super().setValue(key, self.dump_value(value))

    setValue = set_value


config = PinebooSettings("Config")
settings = PinebooSettings("Settings")
