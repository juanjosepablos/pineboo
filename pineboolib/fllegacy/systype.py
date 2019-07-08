from typing import Callable

from PyQt5 import QtCore  # type: ignore

from pineboolib.core.utils.singleton import Singleton
from pineboolib.core.settings import config
from pineboolib.core import decorators
from pineboolib.fllegacy.flutil import FLUtil
from pineboolib.application import project

from pineboolib.core.utils.logging import logging

logger = logging.getLogger("fllegacy.systype")


class SysType(object, metaclass=Singleton):
    def __init__(self) -> None:
        self._name_user = None
        self.sys_widget = None
        self.time_user_ = QtCore.QDateTime.currentDateTime()

    def nameUser(self) -> str:
        ret_ = None
        if project.DGI_.use_alternative_credentials():
            ret_ = project.DGI_.get_nameuser()
        else:
            ret_ = project.conn.user()

        return ret_

    def interactiveGUI(self) -> str:
        return project.DGI_.interactiveGUI()

    def isUserBuild(self) -> bool:
        return self.version().upper().find("USER") > -1

    def isDeveloperBuild(self) -> bool:
        return self.version().upper().find("DEVELOPER") > -1

    def isNebulaBuild(self) -> bool:
        return self.version().upper().find("NEBULA") > -1

    def isDebuggerMode(self) -> bool:
        return bool(config.value("application/isDebuggerMode", False))

    @decorators.NotImplementedWarn
    def isCloudMode(self) -> bool:
        return False

    def isDebuggerEnabled(self) -> bool:
        return bool(config.value("application/dbadmin_enabled", False))

    def isQuickBuild(self):
        return not self.isDebuggerEnabled()

    def isLoadedModule(self, modulename: str) -> bool:
        return modulename in project.conn.managerModules().listAllIdModules()

    def translate(self, *args) -> str:
        util = FLUtil()

        group = args[0] if len(args) == 2 else "scripts"
        text = args[1] if len(args) == 2 else args[0]

        return util.translate(group, text)

    def osName(self) -> str:
        util = FLUtil()
        return util.getOS()

    def nameBD(self):
        return project.conn.DBName()

    def toUnicode(self, val: str, format: str) -> str:
        return val.encode(format).decode("utf-8", "replace")

    def fromUnicode(self, val, format):
        return val.encode("utf-8").decode(format, "replace")

    def Mr_Proper(self):
        project.conn.Mr_Proper()

    def installPrefix(self):
        from pineboolib.core.utils.utils_base import filedir

        return filedir("..")

    def __getattr__(self, fun_: str) -> Callable:
        if self.sys_widget is None:
            if "sys" in project.actions:
                self.sys_widget = project.actions["sys"].load().widget
            else:
                logger.warn("No action found for 'sys'")
        return getattr(self.sys_widget, fun_, None)

    def installACL(self, idacl):
        # acl_ = project.acl()
        acl_ = None  # FIXME: Add ACL later
        if acl_:
            acl_.installACL(idacl)

    def version(self) -> str:
        return str(project.version)

    def processEvents(self) -> None:
        return project.DGI_.processEvents()

    def write(self, encode_, dir_, contenido):
        import codecs

        f = codecs.open(dir_, encoding=encode_, mode="w+")
        f.write(contenido)
        f.seek(0)
        f.close()

    def cleanupMetaData(self, connName="default"):
        project.conn.useConn(connName).manager().cleanupMetaData()

    def updateAreas(self):
        from pineboolib.fllegacy.flapplication import aqApp

        aqApp.initToolBox()

    def reinit(self):
        from pineboolib.fllegacy.flapplication import aqApp

        aqApp.reinit()

    def setCaptionMainWidget(self, t):
        from pineboolib.fllegacy.flapplication import aqApp

        aqApp.setCaptionMainWidget(t)

    def nameDriver(self, connName="default"):
        return project.conn.useConn(connName).driverName()

    def nameHost(self, connName="default"):
        return project.conn.useConn(connName).host()

    def addDatabase(self, *args):
        # def addDatabase(self, driver_name = None, db_name = None, db_user_name = None,
        #                 db_password = None, db_host = None, db_port = None, connName="default"):
        if len(args) == 1:
            conn_db = project.conn.useConn(args[0])
            if not conn_db.isOpen():
                if conn_db.driverName_ and conn_db.driverSql.loadDriver(conn_db.driverName_):
                    conn_db.driver_ = conn_db.driverSql.driver()
                    conn_db.conn = conn_db.conectar(
                        project.conn.db_name, project.conn.db_host, project.conn.db_port, project.conn.db_userName, project.conn.db_password
                    )
                    if conn_db.conn is False:
                        return False

                    conn_db._isOpen = True

        else:
            conn_db = project.conn.useConn(args[6])
            if not conn_db.isOpen():
                conn_db.driverName_ = conn_db.driverSql.aliasToName(args[0])
                if conn_db.driverName_ and conn_db.driverSql.loadDriver(conn_db.driverName_):
                    conn_db.conn = conn_db.conectar(args[1], args[4], args[5], args[2], args[3])

                    if conn_db.conn is False:
                        return False

                    # conn_db.driver().db_ = conn_db
                    conn_db._isOpen = True
                    # conn_db._dbAux = conn_db

        return True

    def removeDatabase(self, connName="default"):
        return project.conn.useConn(connName).removeConn(connName)

    def idSession(self):
        # FIXME: Code copied from flapplication.aqApp
        return self.time_user_.toString(QtCore.Qt.ISODate)
