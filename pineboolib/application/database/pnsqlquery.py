# -*- coding: utf-8 -*-
"""
Module for PNSqlQuery class.
"""

from pineboolib.core.utils import logging

from pineboolib.application.utils import sql_tools
from pineboolib import application
from pineboolib.application import types

from PyQt5 import QtWidgets


from typing import Any, Union, List, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces.ifieldmetadata import IFieldMetaData  # noqa: F401
    from pineboolib.interfaces.iconnection import IConnection  # noqa: F401
    from pineboolib.interfaces.iapicursor import IApiCursor  # noqa: F401
    from pineboolib.application.types import Array  # noqa: F401
    from .pnparameterquery import PNParameterQuery  # noqa: F401
    from .pngroupbyquery import PNGroupByQuery  # noqa: F401

LOGGER = logging.getLogger(__name__)


class PNSqlQueryPrivate(object):
    """
    PNSqlQueryPrivate class.

    Store internal values ​​of the query.
    """

    _name: str

    """
    Parte FROM de la consulta
    """
    _from: Optional[str]

    """
    Parte WHERE de la consulta
    """
    _where: Optional[str]

    """
    Parte ORDER BY de la consulta
    """
    _order_by: Optional[str]

    """
    Base de datos sobre la que trabaja
    """
    _db: "IConnection"

    """
    Lista de parámetros
    """
    _parameter_dict: Dict[str, Any] = {}

    """
    Lista de grupos
    """
    _group_dict: Dict[int, Any] = {}

    """
    Lista de nombres de los campos
    """
    _field_list: List[str]

    """
    Lista de nombres de las tablas que entran a formar
    parte en la consulta
    """
    _tables_list: List[str]

    _last_query: Union[bool, str]
    _forward_only: bool
    _limit: Optional[int]
    _offset: Optional[int]

    def __init__(self, name: Optional[str] = None) -> None:
        """Create a new instance of PNSqlQueryPrivate."""

        if name:
            self._name = name
        self._parameter_dict = {}
        self._group_dict = {}
        self._tables_list = []
        self._field_list = []
        self._order_by = None
        self._where = None
        self._from = None
        self._last_query = False
        self._forward_only = False
        self._limit = None
        self._offset = None


class PNSqlQuery(object):
    """
    Handle queries with specific features.

    It offers the functionality to handle QSqlQuery queries and also offers methods
    to work with parameterized queries and grouping levels.
    """

    _count_ref_query: int = 0
    _invalid_tables_list = False
    _is_active: bool
    _field_name_to_pos_dict: Optional[Dict[str, int]]
    _sql_inspector: sql_tools.SqlInspector
    _row: List[Any]
    _datos: List[Any]
    _posicion: int
    _cursor: Optional["IApiCursor"]
    private_query: PNSqlQueryPrivate

    def __init__(self, cx=None, connection_name: Union[str, "IConnection"] = "default") -> None:
        """
        Initialize a new query.
        """

        if application.PROJECT.conn_manager.mainConn() is None:
            raise Exception("Project is not connected yet")
        self._field_name_to_pos_dict = None
        self.private_query = PNSqlQueryPrivate(cx)
        if isinstance(connection_name, str):
            self.private_query._db = application.PROJECT.conn_manager.useConn(connection_name)
        else:
            self.private_query._db = connection_name

        self._count_ref_query = self._count_ref_query + 1
        self._row = []
        self._datos = []
        self._invalid_tables_list = False
        self.private_query._field_list = []
        self._is_active = False
        self._cursor = None

        retorno_qry = None
        if cx:
            retorno_qry = application.PROJECT.conn_manager.manager().query(cx, self)

        if retorno_qry:
            self.private_query = retorno_qry.private_query

    def __del__(self) -> None:
        """
        Delete cursor properties when closing.
        """

        try:
            if self._cursor is not None:
                self._cursor.close()
            del self._sql_inspector
        except Exception:
            pass

    @property
    def sql_inspector(self) -> sql_tools.SqlInspector:
        """
        Return a sql inspector instance.

        Collect a query and return information about its composition.
        @return sql_inspector
        """

        if not getattr(self, "_sql_inspector", None):
            self._sql_inspector = sql_tools.SqlInspector()

        return self._sql_inspector

    def exec_(self, sql: Optional[str] = None) -> bool:
        """
        Run a query.

        This can be specified or calculated from the values ​​previously provided.
        @param sql. query text.
        @return True or False return if the execution is successful.
        """
        self._is_active = False
        if not sql:
            sql = self.sql()
        else:
            self._invalid_tables_list = False

        if not sql:
            LOGGER.warning("exec_: no sql provided and PNSqlQuery.sql() also returned empty")
            return False

        self.sql_inspector.set_sql(sql)
        self.sql_inspector.resolve()

        if self._invalid_tables_list:
            LOGGER.error("exec_: invalid tables list found")
            return False

        # self._sql_inspector = sql_tools.SqlInspector(sql.lower())

        # sql = self.db().driver().fix_query(sql)
        if sql is None:
            raise Exception("The query is empty!")

        self._last_query = sql
        try:

            self._cursor = self.db().cursor()
            if self._cursor is None:
                raise Exception("self._cursor is empty!")
            LOGGER.trace("exec_: Ejecutando consulta: <%s> en <%s>", sql, self._cursor)
            self.db().execute_query(sql, self._cursor)
            self._datos = self._cursor.fetchall()
            self._posicion = -1
        except Exception as exc:
            LOGGER.error(exc)
            LOGGER.info("Error ejecutando consulta: <%s>", sql)
            LOGGER.trace("Detalle:", stack_info=True)
        if self.db().lastError():
            LOGGER.warning("Error ejecutando consulta: <%s>\n%s", sql, self.db().lastError())
            self._invalid_tables_list = True
            LOGGER.trace("Detalle:", stack_info=True)
            return False

        self._is_active = True
        # conn.commit()
        LOGGER.trace("_exec: Rows: %s SQL: <%s>", len(self._datos), sql)

        return True

    def addParameter(self, parameter: Optional["PNParameterQuery"]) -> None:
        """
        Add the parameter description to the parameter dictionary.

        @param p FLParameterQuery object with the description of the parameter to add.
        """

        if parameter:
            self.private_query._parameter_dict[parameter.name()] = parameter.value()

    def addGroup(self, group: Optional["PNGroupByQuery"]) -> None:
        """
        Add a group description to the group dictionary.

        @param g PNGroupByQuery object with the description of the group to add.
        """

        if group:
            if not self.private_query._group_dict:
                self.private_query._group_dict = {}

            self.private_query._group_dict[group.level()] = group.field()

    def setName(self, name: str) -> None:
        """
        To set the name of the query.

        @param name. query name.
        """
        self.private_query._name = name

    def name(self) -> str:
        """
        To get the name of the query.
        """

        return self.private_query._name

    def select(self) -> str:
        """
        To get the SELECT part of the SQL statement from the query.

        @return text string with the query SELECT.
        """
        ret_: List[str]

        if self.private_query._field_list:
            ret_ = self.private_query._field_list
        else:
            field_names = self.sql_inspector.field_list()
            size_dict: int = len(field_names.keys())
            list_: List[str] = []
            if size_dict > 0:
                i = -1
                while len(list_) != size_dict:
                    i += 1
                    for k in field_names.keys():
                        if int(field_names[k]) == i:
                            list_.append(k)
                            break

            ret_ = list_

        return ",".join(ret_)

    def from_(self) -> str:
        """
        To get the FROM part of the SQL statement from the query.

        @return text string with the query FROM.
        """

        return (
            self.private_query._from if self.private_query._from else self.sql_inspector.get_from()
        )

    def where(self) -> str:
        """
        To get the WHERE part of the SQL statement from the query.

        @return text string with the query WHERE.
        """

        return (
            self.private_query._where
            if self.private_query._where
            else self.sql_inspector.get_where()
        )

    def orderBy(self) -> Optional[str]:
        """
        To get the ORDERBY part of the SQL statement from the query.

        @return text string with the query ORDERBY.
        """

        return (
            self.private_query._order_by
            if self.private_query._order_by
            else self.sql_inspector.get_order_by()
        )

    def setSelect(self, select: Union[str, List, "Array"], sep: str = ",") -> None:
        """
        To set the SELECT part of the SQL statement of the query.

        @param s Text string with the SELECT part of the SQL statement that
            Generate the query. This string should NOT include the reserved word.
            SELECT, nor the character '*' as a wild card. Only support the list
            of fields that should appear in the query separated by the string
            indicated in the parameter 'sep'
        @param sep String used as a separator in the field list. Default the comma is used.
        """
        list_fields = []

        if isinstance(select, str):
            if sep in select:
                # s = s.replace(" ", "")

                prev = ""
                for child in select.split(sep):

                    field_ = prev + child
                    if field_.count("(") == field_.count(")"):
                        list_fields.append(field_)
                        prev = ""
                    else:
                        prev = "%s," % field_

        elif isinstance(select, list):
            list_fields = list(select)
        else:
            for key, value in select:
                list_fields.append(value)

            # s = s.split(sep)

        # self.private_query.select_ = s.strip_whitespace()
        # self.private_query.select_ = self.private_query.select_.simplifyWhiteSpace()
        self.private_query._field_list.clear()

        if not list_fields and isinstance(select, str) and not "*" == select:
            self.private_query._field_list.append(select)
        else:

            # fieldListAux = s.split(sep)
            # for f in s:
            #    f = str(f).strip()

            table: Optional[str]
            field: Optional[str]

            for child in list_fields:
                table = field = None
                try:
                    if child.startswith(" "):
                        child = child[1:]
                    table = child[: child.index(".")]
                    field = child[child.index(".") + 1 :]
                except Exception:
                    pass

                if field == "*" and not table:
                    mtd = self.db().connManager().manager().metadata(table, True)
                    if mtd is not None:
                        self.private_query._field_list = mtd.fieldNames()
                        if not mtd.inCache():
                            del mtd

                else:
                    self.private_query._field_list.append(child)

                # self.private_query.select_ = ",".join(self.private_query._field_list)

    def setFrom(self, from_: str) -> None:
        """
        To set the FROM part of the SQL statement of the query.

        @param f Text string with the FROM part of the SQL statement that generate the query
        """

        self.private_query._from = from_
        # self.private_query._from = f.strip_whitespace()
        # self.private_query._from = self.private_query._from.simplifyWhiteSpace()

    def setWhere(self, where_: str) -> None:
        """
        To set the WHERE part of the SQL statement of the query.

        @param s Text string with the WHERE part of the SQL statement that generates the query.
        """

        self.private_query._where = where_
        # self.private_query._where = w.strip_whitespace()
        # self.private_query._where = self.private_query._where.simplifyWhiteSpace()

    def setOrderBy(self, order_by: str) -> None:
        """
        To set the ORDER BY part of the SQL statement of the query.

        @param s Text string with the ORDER BY part of the SQL statement that generate the query
        """
        self.private_query._order_by = order_by
        # self.private_query._order_by = w.strip_whitespace()
        # self.private_query._order_by = self.private_query._order_by.simplifyWhiteSpace()

    def sql(self) -> str:
        """
        To get the full SQL statement of the query.

        This method joins the three parts of the query (SELECT, FROM AND WHERE),
        replace the parameters with the value they have in the dictionary and return all in a text string.
        @return Text string with the full SQL statement that generates the query.
        """
        # for tableName in self.private_query.tablesList_:
        #    if not self.private_query._db.manager().existsTable(tableName) and not self.private_query._db.manager().createTable(tableName):
        #        return

        res = None

        if not self.private_query._field_list:
            if self._last_query:
                return self._last_query

            LOGGER.warning("sql(): No select yet. Returning empty")
            return ""

        select = ",".join(self.private_query._field_list)

        if not self.private_query._from:
            res = "SELECT %s" % select
        elif not self.private_query._where:
            res = "SELECT %s FROM %s" % (select, self.private_query._from)
        else:
            res = "SELECT %s FROM %s WHERE %s" % (
                select,
                self.private_query._from,
                self.private_query._where,
            )

        if self.private_query._group_dict and not self.private_query._order_by:
            res = res + " ORDER BY "
            init_gd = False
            i = 0
            while i < len(self.private_query._group_dict):
                group_dict: str = self.private_query._group_dict[i]
                if not init_gd:
                    res = res + group_dict
                    init_gd = True
                else:
                    res = res + ", " + group_dict

                i = i + 1

        elif self.private_query._order_by:
            res += " ORDER BY %s" % self.private_query._order_by

        if self.private_query._limit is not None:
            res += " LIMIT %s" % self.private_query._limit

        if self.private_query._offset is not None:
            if self.private_query._limit is None:
                res += " LIMIT %s" % 99999999
                LOGGER.warning("It is highly recommended to use limit next to offset")

            res += " OFFSET %s" % self.private_query._offset
            if self.private_query._order_by is None:
                LOGGER.warning("It is highly recommended to use order by next to offset")

        if self.private_query._parameter_dict:
            for parameter_dict in self.private_query._parameter_dict.keys():
                value = self.private_query._parameter_dict[parameter_dict]

                if value is None:
                    dialog = QtWidgets.QInputDialog()

                    if dialog is not None:
                        value = dialog.getText(
                            QtWidgets.QApplication.activeWindow(),
                            "Entrada de parámetros de la consulta",
                            parameter_dict,
                        )
                        if value:
                            value = value[0]

                res = res.replace(
                    "[%s]" % parameter_dict, "'%s'" % value
                )  # FIXME: ajustar al tipo de dato pnparameterquery.setValue!!

        return res

    def parameterDict(self) -> Dict[str, Any]:
        """
         To obtain the parameters of the query.

        @return Parameter dictionary
        """
        return self.private_query._parameter_dict

    def groupDict(self) -> Dict[int, Any]:
        """
        To obtain the grouping levels of the query.

        @return Dictionary of grouping levels.
        """

        return self.private_query._group_dict

    def fieldList(self) -> List[str]:
        """
        To get the list of field names.

        @return List of text strings with the names of the fields in the query.
        """
        # return self.private_query._field_list if self.private_query._field_list else self.sql_inspector.field_names()
        return self.sql_inspector.field_names() or self.private_query._field_list

    def setGroupDict(self, group_dict: Dict[int, Any]) -> None:
        """
        Assign a parameter dictionary to the query parameter dictionary.

        The parameter dictionary of the FLGroupByQueryDict type, already built,
        It is assigned as the new group dictionary of the query, in the event that
        There is already a dictionary of groups, this is destroyed and overwritten by the new one.
        The dictionary passed to this method becomes the property of the query, and she is the
        responsible for deleting it. If the dictionary to be assigned is null or empty this
        method does nothing.

        @param gd Dictionary of parameters.
        """
        if not group_dict:
            return

        self.private_query._group_dict = group_dict

    def setParameterDict(self, parameter_dict: Dict[str, Any]) -> None:
        """
        Assign a group dictionary to the group dictionary of the query.

        The group dictionary of the FLParameterQueryDict type, already built,
        It is assigned as the new dictionary of query parameters, in the event that
        There is already a dictionary of parameters, it is destroyed and overwritten by the new one.
        The dictionary passed to this method becomes the property of the query, and she is the
        responsible for deleting it. If the dictionary to be assigned is null or empty this
        method does nothing.

        @param pd Parameter dictionary
        """

        if not parameter_dict:
            return

        self.private_query._parameter_dict = parameter_dict

    def showDebug(self) -> None:
        """
        Show the content of the query, by the standard output.

        It is intended only for debugging tasks.
        """
        if not self.isActive():
            LOGGER.warning(
                "DEBUG : La consulta no está activa : No se ha ejecutado exec() o la sentencia SQL no es válida"
            )

        LOGGER.warning("DEBUG : Nombre de la consulta : %s", self.private_query._name)
        LOGGER.warning("DEBUG : Niveles de agrupamiento :")
        if self.private_query._group_dict:
            for lev in self.private_query._group_dict.values():
                LOGGER.warning("**Nivel : %s", lev.level())
                LOGGER.warning("**Campo : %s", lev.field())
        else:
            LOGGER.warning("**No hay niveles de agrupamiento")

        # LOGGER.warning("DEBUG : Parámetros : ")
        # if self.private_query._parameter_dict:
        #     if par in self.private_query._parameter_dict:
        #         LOGGER.warning("**Nombre : %s", par.name())
        #         LOGGER.warning("Alias : %s", par.alias())
        #         LOGGER.warning("Tipo : %s", par.type())
        #         LOGGER.warning("Valor : %s", par.value())
        # else:
        #     LOGGER.warning("**No hay parametros")

        LOGGER.warning("DEBUG : Sentencia SQL")
        LOGGER.warning("%s", self.sql())
        if not self.private_query._field_list:
            LOGGER.warning("DEBUG ERROR : No hay campos en la consulta")
            return

        linea = ""
        LOGGER.warning("DEBUG: Campos de la consulta : ")
        for field in self.private_query._field_list:
            LOGGER.warning("**%s", field)
            linea += "__%s" % self.value(field)
        LOGGER.warning("DEBUG : Contenido de la consulta : ")
        LOGGER.warning(linea)

    def value(self, field_name: Union[str, int, None], raw: bool = False) -> Any:
        """
        Get the value of a query field.

        Given a name of a query field, this method returns a QVariant object
        with the value of that field. The name must correspond to the one placed in
        the SELECT part of the SQL statement of the query.

        @param n Name of the query field
        @param raw If TRUE and the value of the field is a reference to a large value
             (see FLManager :: storeLargeValue ()) returns the value of that reference,
             instead of content to which that reference points

        """

        ret = None

        if field_name is None:
            LOGGER.trace("value::invalid use with n=None.", stack_info=True)
            return None

        if isinstance(field_name, str):
            pos: int = self.sql_inspector.fieldNameToPos(field_name.lower())
        if isinstance(field_name, int):
            pos = field_name

        if self._row:
            ret = self._row[pos]

        if ret in (None, "None"):
            ret = self.sql_inspector.resolve_empty_value(pos)
        else:
            try:
                ret = self.sql_inspector.resolve_value(pos, ret, raw)
            except Exception:
                LOGGER.exception("value::error retrieving row position %s", pos)

        return ret

    def isNull(self, field_name: str) -> bool:
        """
        Indicate whether a query field is null or not.

        Given a name of a query field, this method returns true if the query field is null.
        The name must correspond to the one placed in
        the SELECT part of the SQL statement of the query.

        @param n Name of the query field
        """
        if not self._row:
            return True

        if isinstance(field_name, str):
            pos_ = self.fieldNameToPos(field_name)

            return self._row[pos_] in (None, "None")

        raise Exception("isNull. field not found %s" % field_name)

    def posToFieldName(self, position: int) -> str:
        """
        Return the field name, given its position in the query.

        @param p Position of the field in the query, start at zero and left to right.
        @return Name of the corresponding field. If the field does not exist, it returns None.
        """
        if self.sql_inspector.sql() == "":
            self.sql_inspector.set_sql(self.sql())
            self.sql_inspector.resolve()

        return self.sql_inspector.posToFieldName(position)
        # if p < 0 or p >= len(self.private_query._field_list):
        #    return None
        # ret_ = None
        # try:
        #    ret_ = self.private_query._field_list[p]
        # except Exception:
        #    pass

        # return ret_

    def fieldNameToPos(self, field_name: str) -> int:
        """
        Return the position of a field in the query, given its name.

        @param n Field Name.
        @return Position of the field in the query. If the field does not exist, return -1.
        """
        if self.sql_inspector.sql() == "":
            self.sql_inspector.set_sql(self.sql())
            self.sql_inspector.resolve()

        return self.sql_inspector.fieldNameToPos(field_name.lower())
        # i = 0
        # for field in self.private_query._field_list:
        #    if field.lower() == n.lower():
        #        return i
        #    i = i + 1
        # if n in self.private_query._field_list:
        #    return self.private_query._field_list.index(n)
        # else:
        #    return False

    def tablesList(self) -> List[str]:
        """
        To get the list of names of the query tables.

        @return List of names of the tables that become part of the query.
        """

        return (
            self.private_query._tables_list
            if self.private_query._tables_list
            else self.sql_inspector.table_names()
        )

    def setTablesList(self, table_list: Union[str, List, types.Array]) -> None:
        """
        Set the list of names of the query tables.

        @param table_list Text list (or a list) with the names of the tables separated by commas, e.g. "table1, table2, table3"
        """
        self.private_query._tables_list = []
        if isinstance(table_list, list):
            table_list = ",".join(table_list)
        else:
            table_list = str(table_list)

        table_list = table_list.replace(" ", "")
        for tabla in table_list.split(","):
            if (
                not self.db().connManager().manager().existsTable(tabla)
                and len(table_list.split(",")) >= 1
            ):
                self._invalid_tables_list = True
                LOGGER.warning("setTablesList: table not found %r. Query will not execute.", tabla)

            self.private_query._tables_list.append(tabla)

    def setValueParam(self, param_name: str, value: Any) -> None:
        """
        Set the value of a parameter.

        @param name Parameter name.
        @param v Value for the parameters.
        """

        self.private_query._parameter_dict[param_name] = value

    def valueParam(self, param_name: str) -> Any:
        """
        Get the value of a parameter.

        @param name Parameter name.
        """

        if param_name in self.private_query._parameter_dict.keys():
            return self.private_query._parameter_dict[param_name]
        else:
            return None

    def size(self) -> int:
        """
        Report the number of results returned by the query.

        @return number of results.
        """
        return len(self._datos)

    def fieldMetaDataList(self) -> List["IFieldMetaData"]:
        """
        To get the list of query field definitions.

        @return Object with the list of deficiencies in the query fields.
        """
        list_: List["IFieldMetaData"] = []
        dictado_ = self.sql_inspector.mtd_fields()
        for k in dictado_.keys():
            list_.append(dictado_[k])

        return list_

    def db(self) -> "IConnection":
        """
        Get the database you work on.

        @return PNConnection user by the query.
        """
        return self.private_query._db

    def isValid(self) -> bool:
        """
        Return if the query has an invalid defined table.

        @return True or False.
        """

        return False if self._invalid_tables_list else True

    def isActive(self) -> bool:
        """
        Indicate whether the data has been collected completely.

        @return True or False.
        """
        return self._is_active

    def at(self) -> Any:
        """
        Return the current position in the result list.

        @return line position.
        """

        return self._posicion

    def lastQuery(self) -> Union[bool, str]:
        """
        Return the last query made.

        @return query string.
        """

        return self._last_query

    def numRowsAffected(self) -> int:
        """
        Return Number of lines selected in the query.

        @return number of lines.
        """
        return len(self._datos)

    def lastError(self) -> str:
        """Return last error if exists , empty elsewhere."""

        return self.db().lastError()

    def driver(self) -> Any:
        """Return sql driver."""

        return self.db().driver()

    def isForwardOnly(self) -> bool:
        """Return if is forward only enabled."""
        return self.private_query._forward_only

    def setForwardOnly(self, forward: bool) -> None:
        """Set forward only option value."""
        self.private_query._forward_only = forward

    def seek(self, postition: int, relative=False) -> bool:
        """
        Position the cursor on a given result.

        @param i Position to search.
        @param relative Boolean indicates if the position is relative or absolut.
        @return True or False.
        """

        if not self._cursor:
            return False

        pos = postition
        if relative:
            pos = postition + self._posicion

        if self._datos:
            if pos >= 0 and pos <= len(self._datos) - 1:
                self._posicion = pos
                self._row = self._datos[self._posicion]
                return True

        return False

    def next(self) -> bool:
        """
        Position the query cursor in the next record.

        @return True or False.
        """
        if not self._cursor:
            return False

        if self._datos:
            self._posicion += 1
            if self._posicion < len(self._datos):
                self._row = self._datos[self._posicion]
                return True

        return False

    def prev(self) -> bool:
        """
        Position the query cursor in the provious record.

        @return True or False.
        """
        if not self._cursor:
            return False

        if self._datos:
            self._posicion -= 1
            if self._posicion >= 0:
                self._row = self._datos[self._posicion]
                return True

        return False

    def first(self) -> bool:
        """
        Position the query cursor in the first record.

        @return True or False.
        """
        if not self._cursor:
            return False

        if self._datos:
            self._posicion = 0
            self._row = self._datos[self._posicion]
            return True

        return False

    def last(self) -> bool:
        """
        Position the query cursor in the last record.

        @return True or False.
        """
        if not self._cursor:
            return False

        if self._datos:
            self._posicion = len(self._datos) - 1
            self._row = self._datos[self._posicion]
            return True

        return False

    def setLimit(self, limit: int) -> None:
        """Set limit."""

        self.private_query._limit = limit

    def setOffset(self, offset: int) -> None:
        """Set offset."""

        self.private_query._offset = offset
