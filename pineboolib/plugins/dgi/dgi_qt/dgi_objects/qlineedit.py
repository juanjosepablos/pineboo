# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets


class QLineEdit(QtWidgets.QLineEdit):

    _parent = None

    def __init__(self, parent=None):
        super(QLineEdit, self).__init__(parent=None)
        self._parent = parent
        #if not pineboolib.project._DGI.localDesktop():
        #    pineboolib.project._DGI._par.addQueque("%s_CreateWidget" % self._parent.objectName(), "QLineEdit")

    def getText(self):
        return super(QLineEdit, self).text()

    def setText(self, v):
        if not isinstance(v, str):
            v = str(v)
        super(QLineEdit, self).setText(v)
        #if not pineboolib.project._DGI.localDesktop():
        #    pineboolib.project._DGI._par.addQueque("%s_setText" % self._parent.objectName(), v)

    text = property(getText, setText)