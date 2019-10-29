"""PNConnection_manager module."""
from PyQt5 import QtCore


from pineboolib import application

from typing import Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.fllegacy import flmanager
    from pineboolib.fllegacy import flmanagermodules
    from . import pnconnection
from pineboolib.interfaces.iconnection import IConnection


class PNConnectionManager(QtCore.QObject):
    """PNConnectionManager Class."""

    _manager: "flmanager.FLManager"
    _manager_modules: "flmanagermodules.FLManagerModules"
    conn_dict: Dict[str, IConnection] = {}

    # def __init__(
    #    self,
    #    db_name: str,
    #    db_host: Optional[str],
    #    db_port: Optional[int],
    #    db_user_name: Optional[str],
    #    db_password: Optional[str],
    #    driver_alias: str,
    # ):
    #    """Initialize."""

    #    super().__init__()
    #    self.conn_dict["main_conn"] = pnconnection.PNConnection(self, db_name, db_host, db_port, db_user_name, db_password, driver_alias)

    def setMainConn(self, main_conn: "pnconnection.PNConnection") -> bool:
        """Set main connection."""

        if "main_conn" in self.conn_dict:
            conn_ = self.conn_dict["main_conn"]
            conn_.conn.close()
            del conn_
            del self.conn_dict["main_conn"]

        self.conn_dict["main_conn"] = main_conn
        return True

    def mainConn(self) -> "pnconnection.PNConnection":
        """Return main conn."""
        ret_ = None
        if "main_conn" in self.conn_dict.keys():
            ret_ = self.conn_dict["main_conn"]

        return ret_

    def finish(self) -> None:
        """Set the connection as terminated."""

        for n in list(self.conn_dict.keys()):
            conn_ = self.conn_dict[n].conn
            if conn_ not in [None, self.mainConn().conn]:
                conn_.close()

            del self.conn_dict[n]

        self.conn_dict = {}
        del self

    def useConn(self, name_or_conn: Union[str, IConnection] = "default") -> IConnection:
        """
        Select another connection which can be not the default one.

        Allow you to select a connection.
        """
        name: str
        if isinstance(name_or_conn, IConnection):
            name = name_or_conn.connectionName()
        else:
            name = name_or_conn

        name_conn_: str = "%s_%s" % (application.project.session_id(), name)
        # if name in ("default", None):
        #    return self

        if name_conn_ in self.conn_dict.keys():
            connection_ = self.conn_dict[name_conn_]
        else:
            # if self.driverSql is None:
            #    raise Exception("No driver selected")
            from . import pnconnection

            connection_ = pnconnection.PNConnection(self.mainConn().db_name_)
            connection_.name = name
            self.conn_dict[name_conn_] = connection_

        return connection_

    def dictDatabases(self) -> Dict[str, IConnection]:
        """Return dict with own database connections."""

        dict_ = {}
        session_name = application.project.session_id()
        for n in self.conn_dict.keys():
            if session_name:
                if n.startswith(session_name):
                    dict_[n.replace("%s_" % session_name, "")] = self.conn_dict[n]
            else:
                if n[0] == "_":
                    dict_[n[1:]] = self.conn_dict[n]
                else:
                    dict_[n] = self.conn_dict[n]

        return dict_

    def removeConn(self, name="default") -> bool:
        """Delete a connection specified by name."""

        name_conn_: str = "%s_%s" % (application.project.session_id(), name)

        self.conn_dict[name_conn_]._isOpen = False
        conn_ = self.conn_dict[name_conn_].conn
        if conn_ not in [None, self.mainConn().conn]:
            conn_.close()

        del self.conn_dict[name_conn_]
        return True

    def database(self, name: str = "default") -> "IConnection":
        """Return the connection to a database."""

        return self.useConn(name)

    def manager(self) -> "flmanager.FLManager":
        """
        Flmanager instance that manages the connection.

        Flmanager manages metadata of fields, tables, queries, etc .. to then be managed this data by the controls of the application.
        """

        if not getattr(self, "_manager", None):
            # FIXME: Should not load from FL*
            from pineboolib.fllegacy import flmanager

            self._manager = flmanager.FLManager(self.mainConn())

        return self._manager

    def managerModules(self) -> "flmanagermodules.FLManagerModules":
        """
        Instance of the FLManagerModules class.

        Contains functions to control the state, health, etc ... of the database tables.
        """

        if not getattr(self, "_manager_modules", None):
            from pineboolib.fllegacy.flmanagermodules import FLManagerModules

            # FIXME: Should not load from FL*
            self._manager_modules = FLManagerModules(self.mainConn())

        return self._manager_modules

    def db(self) -> "IConnection":
        """Return the connection itself."""

        return self.useConn("default")

    def dbAux(self) -> "IConnection":
        """
        Return the auxiliary connection to the database.

        This connection is useful for out of transaction operations.
        """
        return self.useConn("dbAux")
