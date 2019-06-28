# -*- coding: utf-8 -*-
import logging
from pineboolib.pncontrolsfactory import aqApp, QMainWindow

logger = logging.getLogger("mainForm_%s" % __name__)


class MainForm(QMainWindow):

    is_closing_ = False
    mdi_enable_ = True

    def __init__(self):
        super().__init__()

        aqApp.main_widget_ = self
        self.is_closing_ = False
        self.mdi_enable_ = True

    @classmethod
    def setDebugLevel(self, q):
        MainForm.debugLevel = q

    def initScript(self):
        from pineboolib.core.utils.utils_base import filedir

        mw = mainWindow
        mw.createUi(filedir("plugins/mainform/eneboo_mdi/mainform.ui"))
        aqApp.container_ = mw
        aqApp.init()

    def createUi(self, ui_file):
        mng = aqApp.db().managerModules()
        self.w_ = mng.createUI(ui_file, None, self)
        self.w_.setObjectName("container")


mainWindow = MainForm()
