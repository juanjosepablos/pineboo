# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import datetime

from PyQt4 import QtCore, QtGui

from pineboolib import qsaglobals
from pineboolib import flcontrols
from pineboolib.flcontrols import FLTable, FLReportViewer, QLineEdit
from pineboolib.fllegacy import FLSqlQuery as FLSqlQuery_Legacy
from pineboolib.fllegacy import FLSqlCursor as FLSqlCursor_Legacy
from pineboolib.fllegacy import FLTableDB as FLTableDB_Legacy
from pineboolib.fllegacy import FLUtil as FLUtil_Legacy

def Object(x=None):
    if x is None: x = {}
    return dict(x)

def Array(x=None):
    if x is None: return {}
    else: return list(x)

def Boolean(x=False): return bool(x)

def FLSqlQuery(*args):
    #if not args: return None
    return FLSqlQuery_Legacy.FLSqlQuery(*args)

def FLUtil(*args):
    return FLUtil_Legacy.FLUtil(*args)

def FLSqlCursor(action=None):
    if action is None: return None
    return FLSqlCursor_Legacy.FLSqlCursor(action)

def FLTableDB(*args):
    if not args: return None
    return FLTableDB_Legacy.FLTableDB(*args)

class FormDBWidget(QtGui.QWidget):
    def __init__(self, action, project, parent = None):
        super(FormDBWidget, self).__init__(parent)
        self._action = action
        self._cursor = FLSqlCursor(action.name)
        self._prj = project
        self._class_init()

    def _class_init(self):
        pass

    def child(self, childName):
        ret = self.findChild(QtGui.QWidget, childName)
        if ret is None:
            print("WARN: No se encontró el control %r" % childName)
        #else:
        #    print("DEBUG: Encontrado el control %r: %r" % (childName, ret))
        return ret

    def cursor(self):
        return self._cursor

def FLFormSearchDB(name):
    return flcontrols.FLFormSearchDB(name)

class Date(QtCore.QDate):
    pass

class Dialog(QtGui.QDialog):
    pass
