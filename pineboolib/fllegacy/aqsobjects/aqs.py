# -*- coding: utf-8 -*-
"""
AQS package.

Main entrance to the different AQS resources.
"""

from PyQt5 import QtCore, QtWidgets, QtGui, QtXml

from pineboolib.core.utils import logging

from typing import Any, Optional, Union

from . import aqshttp, aqods

logger = logging.getLogger("AQS")


class SMTP(object):
    """Smtp enumerate class."""

    SmtpSslConnection: int = 1
    SmtpTlsConnection: int = 2
    SmtpAuthPlain: int = 1
    SmtpAuthLogin: int = 2
    SmtpSendOk: int = 11
    SmtpError: int = 7
    SmtpMxDnsError: int = 10
    SmtpSocketError: int = 12
    SmtpAttachError: int = 15
    SmtpServerError: int = 16
    SmtpClientError: int = 17


class Docker(object):
    """Docker enumerate class."""

    LeftDockWidgetArea: int = 1
    InDock: str = "InDock"
    OutSideDock: str = "OutSideDock"


class FLTableDB(object):
    """Fltabledb enumerate class."""

    RefreshData = [False, True]


class PrinterColorMode(object):
    """PrintColorMode enumerate class."""

    PrintGrayScale = 0
    PrintColor = 1


class Events(object):
    """AQS Events."""

    Close = QtGui.QCloseEvent
    Show = QtGui.QShowEvent
    ContextMenu = QtGui.QContextMenuEvent


class AQS_Class(SMTP, Docker, FLTableDB, PrinterColorMode, aqods.OdsStyleFlags, Events):
    """AQS Class."""

    Box = None
    Plain = None
    StFailed = None

    def __getattr__(self, name: str) -> Any:
        """
        Return the attributes of the main classes, if it is not in the class.

        @param name. Attribute name.
        @return Attribute or None.
        """

        if name == "DockLeft":
            name = "LeftDockWidgetArea"
            return getattr(self, name)
        elif name == "WordBreak":
            name = "TextWordWrap"
            return getattr(self, name)

        ret_ = getattr(QtCore.Qt, "%sOrder" % name, None)

        if ret_ is None:
            ret_ = getattr(QtGui, "Q%sEvent" % name, None)

        if ret_ is None:
            for lib in [
                QtWidgets.QFrame,
                QtWidgets.QLabel,
                QtWidgets.QSizePolicy,
                QtCore.Qt,
                QtCore.QEvent,
            ]:
                ret_ = getattr(lib, name, None)
                if ret_ is not None:
                    break

        if ret_ is None:
            ret_ = getattr(aqshttp.AQSHttp(), "Http%s" % name, None)

        if ret_ is not None:
            logger.warning("AQS: Looking up attr: %r -> %r  (Please set these in AQS)", name, ret_)
            return ret_

        logger.warning("AQS: No se encuentra el atributo %s", name)

    @staticmethod
    def ColorDialog_getColor(
        color: Optional[Union[int, str, QtGui.QColor]] = None,
        parent: Optional[QtWidgets.QWidget] = None,
        name: Optional[str] = None,
    ) -> Any:
        """
        Display the color selection dialog.

        @param color. Specify the initial color.
        @param parent. Parent.
        @param name. deprecated. Parameter used for compatibility.
        """

        if color is None:
            qcolor = QtGui.QColor("black")
        elif not isinstance(color, QtGui.QColor):
            qcolor = QtGui.QColor(color)
        else:
            qcolor = color

        cL = QtWidgets.QColorDialog(qcolor, parent)
        return cL.getColor()

    @classmethod
    def toXml(
        cls,
        obj_: QtCore.QObject,
        include_children: bool = True,
        include_complex_types: bool = False,
    ) -> QtXml.QDomDocument:
        """
        Convert an object to xml.

        @param obj_. Object to be processed
        @param include_children. Include children of the given object
        @param include_complex_types. Include complex children
        @return xml of the given object
        """

        xml_ = QtXml.QDomDocument()

        if not obj_:
            return xml_

        e = xml_.createElement(type(obj_).__name__)
        e.setAttribute("class", type(obj_).__name__)
        xml_.appendChild(e)

        _meta = obj_.metaObject()

        i = 0
        # _p_properties = []
        for i in range(_meta.propertyCount()):
            mp = _meta.property(i)
            # if mp.name() in _p_properties:
            #    i += 1
            #    continue

            # _p_properties.append(mp.name())

            val = getattr(obj_, mp.name(), None)
            try:
                val = val()
            except Exception:
                pass

            if val is None:
                i += 1
                continue

            val = str(val)

            if not val and not include_complex_types:
                i += 1
                continue
            e.setAttribute(mp.name(), val)

            i += 1

        if include_children:

            for child in obj_.children():

                itd = cls.toXml(child, include_children, include_complex_types)
                xml_.firstChild().appendChild(itd.firstChild())
        return xml_

    @staticmethod
    def pixmap_fromMimeSource(name: str) -> QtGui.QPixmap:
        """
        Get a QtGui.QPixmap of a given file name.

        @param name. File Name
        @return QtGui.QPixmap
        """

        from pineboolib.core.utils.utils_base import pixmap_fromMimeSource

        return pixmap_fromMimeSource(name)

    Pixmap_fromMineSource = pixmap_fromMimeSource

    @classmethod
    def sha1(cls, byte_array: bytes) -> str:
        """
        Return the sha1 of a set of bytes.

        @param byte_array: bytes to process.
        @return sha1 string
        """

        from pineboolib.q3widgets.qbytearray import QByteArray

        ba = QByteArray(byte_array)
        return ba.sha1()

    @classmethod
    def Application_setOverrideCursor(cls, shape: "QtGui.QCursor", replace: bool = False) -> None:
        """
        Set override cursor.

        @param. shape. QtGui.QCursor instance to override.
        @param. replace. Not used.
        """

        QtWidgets.QApplication.setOverrideCursor(shape)

    @classmethod
    def Application_restoreOverrideCursor(cls) -> None:
        """Restore override cursor."""
        QtWidgets.QApplication.restoreOverrideCursor()

    @classmethod
    def TextCodec_codecForName(cls, codec_name: str) -> str:
        """Return codec name."""

        return codec_name


AQS = AQS_Class()
