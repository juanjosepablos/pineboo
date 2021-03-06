"""Messagebox module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QApplication  # type: ignore
from pineboolib.core.utils import logging
from typing import Any

logger = logging.getLogger("messageBox")


class MessageBox(QMessageBox):
    """MessageBox class."""

    @classmethod
    def msgbox(
        cls, typename, text, button0, button1=None, button2=None, title=None, form=None
    ) -> Any:
        """Return a messageBox."""
        from pineboolib import application

        if application.PROJECT._splash:
            application.PROJECT._splash.hide()

        if not isinstance(text, str):
            logger.warning("MessageBox help!", stack_info=True)
            # temp = text
            text = button1
            button1 = title
            title = button0
            button0 = button2
            button2 = None

        if form:
            logger.warning("MessageBox: Se intentó usar form, y no está implementado.")
        icon = QMessageBox.NoIcon
        if not title:
            title = "Pineboo"
        if typename == "question":
            icon = QMessageBox.Question
            if not title:
                title = "Question"
        elif typename == "information":
            icon = QMessageBox.Information
            if not title:
                title = "Information"
        elif typename == "warning":
            icon = QMessageBox.Warning
            if not title:
                title = "Warning"
        elif typename == "critical":
            icon = QMessageBox.Critical
            if not title:
                title = "Critical"
        # title = unicode(title,"UTF-8")
        # text = unicode(text,"UTF-8")
        msg = QMessageBox(icon, title, text)
        parent = QApplication.activeModalWidget() or application.PROJECT.main_window
        msg.setParent(parent)

        msg.setWindowModality(QtCore.Qt.ApplicationModal)
        msg.setEnabled(True)
        if button0:
            msg.addButton(button0)
        if button1:
            msg.addButton(button1)
        if button2:
            msg.addButton(button2)

        # size = msg.sizeHint()
        # screen_rect = QDesktopWidget().screenGeometry(parent)
        # screen_num = QDesktopWidget().screenNumber(parent)
        # geo = QDesktopWidget().availableGeometry(screen_num)
        # print("*", geo, geo.x(), geo.y())
        # msg.move(QPoint(geo.x() + ( geo.width() / 2 ) + 100, geo.y() + ( geo.height() / 2 )))

        return msg.exec_()

    @classmethod
    def question(cls, *args) -> QMessageBox.StandardButton:
        """Return an question messageBox."""

        return cls.msgbox("question", *args)

    @classmethod
    def information(cls, *args) -> QMessageBox.StandardButton:
        """Return an information messageBox."""
        return cls.msgbox("question", *args)

    @classmethod
    def warning(cls, *args) -> QMessageBox.StandardButton:
        """Return an warning messageBox."""
        clip_board = QApplication.clipboard()
        clip_board.clear()
        text_ = args[0] if isinstance(args[0], str) else args[2]
        clip_board.setText(text_)

        return cls.msgbox("warning", *args)

    @classmethod
    def critical(cls, *args) -> QMessageBox.StandardButton:
        """Return an critical messageBox."""
        clip_board = QApplication.clipboard()
        clip_board.clear()
        text_ = args[0] if isinstance(args[0], str) else args[2]
        clip_board.setText(text_)
        return cls.msgbox("critical", *args)
