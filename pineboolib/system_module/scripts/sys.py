"""Sys module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa
import traceback
from pineboolib import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.database import pnsqlcursor

logger = logging.getLogger(__name__)


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""
        self.form = self
        self.iface = self

    def init(self) -> None:
        """Init function."""
        settings = qsa.AQSettings()
        app_ = qsa.aqApp
        if not app_:
            return
        flfactppal = qsa.SysType().isLoadedModule("flfactppal")
        if flfactppal is True:
            try:
                codEjercicio = qsa.from_project("flfactppal").iface.pub_ejercicioActual()
            except Exception as e:
                logger.error(
                    "Module flfactppal was loaded but not able to execute <flfactppal.iface.pub_ejercicioActual()>"
                )
                logger.error(
                    "... this usually means that flfactppal has failed translation to python"
                )
                logger.exception(e)
                codEjercicio = None
            if codEjercicio:
                util = qsa.FLUtil()
                nombreEjercicio = util.sqlSelect(
                    u"ejercicios", u"nombre", qsa.ustr(u"codejercicio='", codEjercicio, u"'")
                )
                if qsa.AQUtil.sqlSelect(u"flsettings", u"valor", u"flkey='PosInfo'") == "True":
                    texto = ""
                    if nombreEjercicio:
                        texto = qsa.ustr(u"[ ", nombreEjercicio, u" ]")
                    texto = qsa.ustr(
                        texto,
                        u" [ ",
                        app_.db().driverNameToDriverAlias(app_.db().driverName()),
                        u" ] * [ ",
                        qsa.SysType().nameBD(),
                        u" ] * [ ",
                        qsa.SysType().nameUser(),
                        u" ] ",
                    )
                    app_.setCaptionMainWidget(texto)

                else:
                    if nombreEjercicio:
                        app_.setCaptionMainWidget(nombreEjercicio)

                oldApi = settings.readBoolEntry(u"application/oldApi")
                if not oldApi:
                    valor = util.readSettingEntry(u"ebcomportamiento/ebCallFunction")
                    if valor:
                        funcion = qsa.Function(valor)
                        try:
                            funcion()
                        except Exception:
                            qsa.debug(traceback.format_exc())

        if settings.readBoolEntry("ebcomportamiento/git_updates_enabled", False):
            qsa.sys.AQTimer().singleShot(2000, qsa.SysType.search_git_updates)


def afterCommit_flfiles(curFiles: "pnsqlcursor.PNSqlCursor") -> bool:
    """Afet commit flfiles."""
    if curFiles.modeAccess() != curFiles.Browse:
        qry = qsa.FLSqlQuery()
        qry.setTablesList(u"flserial")
        qry.setSelect(u"sha")
        qry.setFrom(u"flfiles")
        qry.setForwardOnly(True)
        if qry.exec_():
            if qry.first():
                util = qsa.FLUtil()
                v = util.sha1(qry.value(0))
                while qry.next():
                    if qry.value(0) is not None:
                        v = util.sha1(v + qry.value(0))
                curSerial = qsa.FLSqlCursor(u"flserial")
                curSerial.select()
                if not curSerial.first():
                    curSerial.setModeAccess(curSerial.Insert)
                else:
                    curSerial.setModeAccess(curSerial.Edit)

                curSerial.refreshBuffer()
                curSerial.setValueBuffer(u"sha", v)
                curSerial.commitBuffer()

        else:
            curSerial = qsa.FLSqlCursor(u"flserial")
            curSerial.select()
            if not curSerial.first():
                curSerial.setModeAccess(curSerial.Insert)
            else:
                curSerial.setModeAccess(curSerial.Edit)

            curSerial.refreshBuffer()
            curSerial.setValueBuffer(u"sha", curFiles.valueBuffer(u"sha"))
            curSerial.commitBuffer()

    return True


form = None