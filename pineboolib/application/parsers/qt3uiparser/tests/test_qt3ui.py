"""Test_pnsqlquery module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from PyQt5 import QtWidgets, QtCore


class TestQT3UIParser(unittest.TestCase):
    """TestQT3UIParser Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_mainForm(self) -> None:
        """Test mainForm widget."""

        mng_modules = application.PROJECT.conn_manager.managerModules()
        from pineboolib.core.utils.utils_base import filedir

        file_1 = filedir("./application/parsers/qt3uiparser/tests/fixtures/main_form_qt3.ui")
        widget = mng_modules.createUI(file_1)
        self.assertTrue(widget)

        action = widget.findChild(QtWidgets.QAction, "ebcomportamiento")
        self.assertTrue(action)

    def test_formRecord(self) -> None:
        """Test formRecord widget."""

        mng_modules = application.PROJECT.conn_manager.managerModules()
        from pineboolib.core.utils.utils_base import filedir

        file_1 = filedir("./application/parsers/qt3uiparser/tests/fixtures/form_record_qt3.ui")
        widget = mng_modules.createUI(file_1)
        self.assertTrue(widget)
        bt_01 = widget.findChild(QtWidgets.QWidget, "pb_uno", QtCore.Qt.FindChildrenRecursively)
        self.assertTrue(bt_01)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
