# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMessageBox
class MessageBox(QMessageBox):
    @classmethod
    def msgbox(cls, typename, text, button0, button1=None, button2=None, title=None, form=None):
        if form:
            logger.warn("MessageBox: Se intentó usar form, y no está implementado.")
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
        msg.addButton(button0)
        if button1:
            msg.addButton(button1)
        if button2:
            msg.addButton(button2)
        return msg.exec_()

    @classmethod
    def question(cls, *args):
        return cls.msgbox("question", *args)

    @classmethod
    def information(cls, *args):
        return cls.msgbox("question", *args)

    @classmethod
    def warning(cls, *args):
        return cls.msgbox("warning", *args)

    @classmethod
    def critical(cls, *args):
        return cls.msgbox("critical", *args)