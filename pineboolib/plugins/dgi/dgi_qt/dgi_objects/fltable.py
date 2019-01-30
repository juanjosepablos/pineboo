# -*- coding: utf-8 -*-

from pineboolib.pncontrolsfactory import QTable
from pineboolib import decorators

class FLTable(QTable):
    AlwaysOff = None

    @decorators.NotImplementedWarn
    def setColumnMovingEnabled(self, b):
        pass

    @decorators.NotImplementedWarn
    def setVScrollBarMode(self, mode):
        pass

    @decorators.NotImplementedWarn
    def setHScrollBarMode(self, mode):
        pass