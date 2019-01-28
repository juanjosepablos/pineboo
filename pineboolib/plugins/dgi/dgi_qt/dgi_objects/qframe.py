# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets

class QFrame(QtWidgets.QFrame):
    _line_width = None
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._line_width = 1
        self._do_style()
        
        
    def _do_style(self):
        self.style_str = "QFrame{ background-color: transparent;"
        self.style_str += " border-width: %spx;" % self._line_width
        self.style_str += " }"
        self.setStyleSheet(self.style_str)