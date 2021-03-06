# -*- coding: utf-8 -*-
"""
Manage tables used by Pineboo.

Maintains the definition of a table.

This class maintains the definition of
certain characteristics of a base table
of data.

Additionally it can be used for the definition of
the metadata of a query, see FLTableMetaData :: query ().
"""

from pineboolib.core import decorators

from pineboolib.interfaces import itablemetadata
from pineboolib import logging
import copy

from typing import Optional, List, Dict, Union, TYPE_CHECKING
from . import pnfieldmetadata
from . import pncompoundkeymetadata

if TYPE_CHECKING:
    from . import pnrelationmetadata  # noqa

LOGGER = logging.getLogger("CursorTableModel")


class PNTableMetaData(itablemetadata.ITableMetaData):
    """PNTableMetaData Class."""

    private: "PNTableMetaDataPrivate"

    def __init__(
        self,
        name_or_metadata: Union[str, "PNTableMetaData"] = "",
        alias: Optional[str] = None,
        query_name: Optional[str] = None,
    ) -> None:
        """
        Collect the data to start.

        @param name_or_metadata Name of the table to define
        @param alias Alias ​​of the table, used in forms
        @param query_name (Optional) Name of the query from which you define your metadata
        """

        super().__init__(name_or_metadata, alias, query_name)
        # tmp = None
        if not isinstance(name_or_metadata, str):
            self.inicializeFLTableMetaData(name_or_metadata)

        else:
            if alias is not None and query_name is not None:
                self.inicializeNewFLTableMetaData(name_or_metadata, alias, query_name)
            else:
                self.inicializeFLTableMetaDataP(name_or_metadata)

    def inicializeFLTableMetaData(self, other: Optional["PNTableMetaData"] = None) -> None:
        """
        Initialize the data from another PNTableMetaData.
        """

        self.private = PNTableMetaDataPrivate()
        self.copy(other)

    def inicializeNewFLTableMetaData(self, name: str, alias: str, query_name: str = None) -> None:
        """
        Initialize the data with the basic information.

        @param name Name of the table to define
        @param alias Alias ​​of the table, used in forms
        @param query_name (Optional) Name of the query from which you define your metadata

        """
        self.private = PNTableMetaDataPrivate(name, alias, query_name)

    def inicializeFLTableMetaDataP(self, name: str) -> None:
        """
        Initialize the private part, without data. Just specify the name.
        """

        self.private = PNTableMetaDataPrivate(name)

        self.private._compound_key = pncompoundkeymetadata.PNCompoundKeyMetaData()

        """
        try:
            table = self._prj.tables[name]
        except:
            return None

        for field in table.fields:
            field.setMetadata(self)
            if field.isCompoundKey():
                self.private._compound_key.addFieldMD(field)
            if field.isPrimaryKey():
                self.private._primary_key = field.name()

            self.private._field_list.append(field)
            self.private._field_names.append(field.name())

            if field.type() == FLFieldMetaData.Unlock:
                self.private._field_names_unlock.append(field.name())
        """

    def name(self) -> str:
        """
        Get the name of the table.

        @return The name of the table described
        """

        return self.private._name

    def setName(self, name: str) -> None:
        """
        Set the name of the table.

        @param name Table name
        """

        # QObject::setName(n);
        self.private._name = name

    def setAlias(self, alias: str) -> None:
        """
        Set the alias.

        @param a Alias
        """

        self.private._alias = alias

    def setQuery(self, query: str) -> None:
        """
        Set the name of the query.

        @param q Query name
        """

        self.private._query = query

    def alias(self) -> str:
        """
        Get the alias associated with the table.

        @return Alias.
        """

        return self.private._alias

    def query(self) -> str:
        """
        Get the name of the query from which it defines its metadata.

        The name will correspond to the definition of a query by
        (.qry file). If the name of the query is defined then
        the name of the table will correspond to the main table of the query
        when referring to several tables.
        """

        return self.private._query

    def isQuery(self) -> bool:
        """
        Get if you define the metadata of a query.
        """

        return True if self.private._query else False

    def addFieldMD(self, field_metadata: "pnfieldmetadata.PNFieldMetaData") -> None:
        """
        Add the description of a field to the list of field descriptions.

        @param f FLFieldMetaData object with the description of the field to add
        """

        # if f is None:
        #     return
        if not field_metadata.metadata():
            field_metadata.setMetadata(self)
        self.private._field_list.append(field_metadata)
        self.private.addFieldName(field_metadata.name())
        self.private.formatAlias(field_metadata)

        if field_metadata.type() == pnfieldmetadata.PNFieldMetaData.Unlock:
            self.private._field_names_unlock.append(field_metadata.name())
        if field_metadata.isPrimaryKey():
            self.private._primary_key = field_metadata.name().lower()

    def removeFieldMD(self, field_name: str) -> None:
        """
        Remove the description of a field from the list of field descriptions.

        @param fN Name of the field to be deleted
        """
        for _field in self.private._field_list:
            if _field.name().lower() == field_name.lower():
                self.private._field_list.remove(_field)
                break

        self.private.removeFieldName(field_name)

    def setCompoundKey(self, cK: Optional["pncompoundkeymetadata.PNCompoundKeyMetaData"]) -> None:
        """
        Set the composite key of this table.

        @param cK FLCompoundKey object with the description of the composite key
        """

        self.private._compound_key = cK

    def primaryKey(self, prefixTable=False) -> str:
        """
        Get the name of the field that is the primary key for this table.

        @param prefixTable If TRUE, a prefix with the name of the table is added; tablename.fieldname
        """

        if not self.private._primary_key:
            raise Exception("No primaryKey in %s" % self.private._name)

        if "." in self.private._primary_key:
            return self.private._primary_key

        if prefixTable:
            return str("%s.%s" % (self.private._name, self.private._primary_key))
        else:
            return str(self.private._primary_key)

    def fieldNameToAlias(self, field_name: Optional[str] = None) -> Optional[str]:
        """
        Get the alias of a field from its name.

        @param fN Field name
        """

        if field_name:
            for key in self.private._field_list:
                if key.name().lower() == field_name.lower():
                    return key.alias()

        return None

    def fieldAliasToName(self, alias_name: Optional[str] = None) -> Optional[str]:
        """
        Get the name of a field from its alias.

        @param aN Field alias name
        """

        if alias_name:
            for key in self.private._field_list:
                if key.alias().lower() == alias_name.lower():
                    return key.name()

        return None

    def fieldType(self, field_name: Optional[str] = None) -> Optional[int]:
        """
        Get the type of a field from its name.

        @param fN Field name
        """
        type_ = None
        if field_name:
            field_name = str(field_name)

            for field in self.private._field_list:
                if field.name() == field_name.lower():
                    type_ = field.type()
                    break

        ret_ = None
        if type_ is not None:
            if type_ in ("string", "counter", "timestamp"):
                ret_ = 3
            elif type_ == "stringlist":
                ret_ = 4
            elif type_ == "pixmap":
                ret_ = 6
            elif type_ == "uint":
                ret_ = 17
            elif type_ == "bool":
                ret_ = 18
            elif type_ == "double":
                ret_ = 19
            elif type_ == "date":
                ret_ = 26
            elif type_ == "time":
                ret_ = 27
            elif type_ == "serial":
                ret_ = 100
            elif type_ == "unlock":
                ret_ = 200
            elif type_ == "check":
                ret_ = 300
            else:
                # FIXME: Falta int
                LOGGER.warning("FIXME:: No hay definido un valor numérico para el tipo %s", type_)

        return ret_

    def fieldIsPrimaryKey(self, field_name: Optional[str] = None) -> Optional[bool]:
        """
        Get if a field is the primary key from its name.

        @param fN Field name.
        """

        if field_name:
            for field in self.private._field_list:
                if field.name() == field_name.lower():
                    return field.isPrimaryKey()

        return None

    def fieldIsIndex(self, field_name: Optional[str] = None) -> int:
        """
        Get if a field is index based on its name.

        @param fN Field name.
        """
        if field_name:
            if field_name in self.fieldNames():
                return self.fieldNames().index(field_name)

        LOGGER.warning("FLTableMetaData.fieldIsIndex(%s) No encontrado", field_name)
        return -1

    def fieldIsCounter(self, field_name: Optional[str] = None) -> Optional[bool]:
        """
        Get if a field is a counter.

        @param fN Field name.
        @author Andrés Otón Urbano (baxas@eresmas.com)
        """
        if field_name:
            for field in self.private._field_list:
                if field.name() == field_name.lower():
                    return field.isCounter()

        return False

    def fieldAllowNull(self, field_name: Optional[str] = None) -> Optional[bool]:
        """
        Get if a field can be null.

        @param fN Field name
        """

        if field_name:
            for field in self.private._field_list:
                if field.name() == field_name.lower():
                    return field.allowNull()

        return False

    def fieldIsUnique(self, field_name: Optional[str] = None) -> Optional[bool]:
        """
        Get if a field is unique from its name.

        @param fN Field name.
        """
        if field_name:
            for field in self.private._field_list:
                if field.name() == field_name.lower():
                    return field.isUnique()

        return False

    def fieldTableM1(self, field_name: Optional[str]) -> Optional[str]:
        """
        Get the name of the foreign table related to a field in this table by an M1 relationship (many to one).

        @param fN Field of the relation M1 of this table, which is supposed to be related
            with another field from another table.
        @return The name of the related table M1, if there is a relationship for the field, or a string
            empty without the field is not related.
        """

        if field_name:
            for field in self.fieldList():
                if field.name() == field_name.lower():
                    relation_ = field.relationM1()
                    if relation_:
                        return relation_.foreignTable()

        return None

    def fieldForeignFieldM1(self, field_name: Optional[str]) -> Optional[str]:
        """
        Get the name of the foreign table field related to the one indicated by an M1 relationship (many still).

        @param fN Field of the relation M1 of this table, which is supposed to be related
            with another field from another table.
        @return The name of the foreign field related to the indicated.
        """

        if field_name:
            for field in self.fieldList():
                if field.name() == field_name.lower():
                    relation_ = field.relationM1()
                    if relation_:
                        return relation_.foreignField()
        return None

    def relation(
        self, field_name: str, foreign_field: str, foreign_table: str
    ) -> Optional["pnrelationmetadata.PNRelationMetaData"]:
        """
        Get the relationship object that defines two fields.

        @param field_name Field name of this table that is part of the relationship.
        @param foreign_field Name of the foreign field to this table that is part of the relationship.
        @param foreign_table Name of the foreign table.
        @return Returns a FLRelationMetaData object with the relationship information, provided
            when it exists If it does not exist, it returns False.
        """

        for field in self.fieldList():
            if field.name() == field_name.lower():
                relation_ = field.relationM1()
                if relation_:
                    if (
                        relation_.foreignField() == foreign_field.lower()
                        and relation_.foreignTable() == foreign_table.lower()
                    ):
                        return relation_

                relation_list = field.relationList()
                for itr in relation_list:
                    if (
                        itr.foreignField() == foreign_field.lower()
                        and itr.foreignTable() == foreign_table.lower()
                    ):
                        return itr

        return None

    def fieldLength(self, field_name: Optional[str] = None) -> Optional[int]:
        """
        Get the length of a field from its name.

        @param fN Field name.
        @return field length.
        """

        if field_name:
            for field in self.fieldList():
                if field.name() == field_name.lower():
                    return field.length()

        return None

    def fieldPartInteger(self, field_name: Optional[str] = None) -> Optional[int]:
        """
        Get the number of digits of the entire part of a field from its name.

        @param fN Field name.
        @return integer length.
        """

        if field_name:
            for field in self.fieldList():
                if field.name() == field_name.lower():
                    return field.partInteger()

        return None

    def fieldPartDecimal(self, field_name: Optional[str] = None) -> Optional[int]:
        """
        Get the number of digits of the decimal part of a field from its name.

        @param fN Field name.
        @return part decimal length.
        """

        if field_name:
            for field in self.fieldList():
                if field.name() == field_name.lower():
                    return field.partDecimal()

        return None

    def fieldCalculated(self, field_name: Optional[str] = None) -> Optional[int]:
        """
        Get if a field is calculated.

        @param fN Field name.
        """

        if field_name:
            for field in self.fieldList():
                if field.name() == field_name.lower():
                    return field.calculated()

        return None

    def fieldVisible(self, field_name: Optional[str] = None) -> Optional[bool]:
        """
        Get if a field is visible.

        @param fN Field name.
        """

        if field_name:
            for field in self.fieldList():
                if field.name() == field_name.lower():
                    return field.visible()

        return None

    def field(
        self, field_name: Optional[str] = None
    ) -> Optional["pnfieldmetadata.PNFieldMetaData"]:
        """
        Get the metadata of a field.

        @param fN Field name.
        @return A FLFieldMetaData object with the information or metadata of a given field.
        """

        if field_name:
            for field in self.private._field_list:
                if field.name() == field_name.lower():
                    return field

        return None

    def fieldList(self) -> List["pnfieldmetadata.PNFieldMetaData"]:
        """
        Return a list of field definitions.

        @return Object with the table field deficits list
        """

        return self.private._field_list

    def fieldListArray(self, prefix_table: bool = False) -> List[str]:
        """
        To get a string with the names of the fields separated by commas.

        @param prefix_table If TRUE a prefix is ​​added to each field with the name of the table; tablename.fieldname
        @return String with the names of the fields separated by commas.
        """

        listado = []
        cadena = "%s." % self.name() if prefix_table else ""

        for field in self.private._field_list:
            listado.append("%s%s" % (cadena, field.name()))

        return listado

    # def fieldListObject(self):
    #    #print("FiledList count", len(self.private._field_list))
    #    return self.private._field_list

    def indexPos(self, field_name: str) -> int:
        """
        Return the position of a field in the real order.

        @param field_name. Field Name.
        @return position index or None.
        """

        return self.fieldIsIndex(field_name)

    def fieldListOfCompoundKey(
        self, field_name: Optional[str] = None
    ) -> Optional[List["pnfieldmetadata.PNFieldMetaData"]]:
        """
        Get the list of fields of a compound key, from the name of a field that you want to find out if it is in that compound key.

        @param fN Name of the field you want to find out if it belongs to a compound key.
        @return If the field belongs to a composite key, it returns the list of fields
          that form said composite key, including the consulted field. If
          that the consulted field does not belong to any compound key returns None
        """

        if field_name:
            if self.private._compound_key:
                if self.private._compound_key.hasField(field_name):
                    return self.private._compound_key.fieldList()
        return None

    def fieldNames(self) -> List[str]:
        """
        Get a list of texts containing the names of fields separated by commas.

        The order of the fields from left to right corresponds to the order in which
        have been added with the addFieldMD () or addFieldName () method

        @return field name list.
        """

        return self.private._field_names

    def fieldNamesUnlock(self) -> List[str]:
        """
        List of field names in the table that are of type PNFieldMetaData :: Unlock.

        @return field name list.
        """

        return self.private._field_names_unlock

    def concurWarn(self) -> bool:
        """
        Return concurWarn flag.

        @return True or False
        """

        return self.private._concur_warn

    def setConcurWarn(self, state: bool = True) -> None:
        """
        Enable concurWarn flag.

        @param state. True or False.
        """

        self.private._concur_warn = state

    @decorators.BetaImplementation
    def detectLocks(self) -> bool:
        """
        Return lock detection flag.

        @return b. True or False.
        """

        return self.private._detect_locks

    def setDetectLocks(self, state: bool = True) -> None:
        """
        Enable lock detection flag.

        @return b. True or False.
        """

        self.private._detect_locks = state

    def FTSFunction(self) -> str:
        """
        Return function name to call for Full Text Search.

        @return function name or None.
        """

        return self.private.full_text_search_function

    def setFTSFunction(self, full_text_search_function: str) -> None:
        """
        Set the function name to call for Full Text Search.

        @param ftsfun. function name.
        """

        self.private.full_text_search_function = full_text_search_function

    def inCache(self) -> bool:
        """
        Return if the metadata is cached (FLManager :: cacheMetaData_).

        @return True or False.
        """

        return self.private._in_cache if self.private else False

    def setInCache(self, state: bool = True) -> None:
        """
        Set the metadata is cached (FLManager :: cacheMetaData_).

        @return True or False.
        """

        self.private._in_cache = state

    def copy(self, other: Optional["PNTableMetaData"] = None) -> None:
        """
        Copy the values ​​of a PNFieldMetaData from another.

        @param other. PNTableMetaData.
        """

        if other is None or other == self:
            return

        self.private = copy.copy(other.private)

    def indexFieldObject(self, position: int) -> "pnfieldmetadata.PNFieldMetaData":
        """
        Return the PNFieldMetaData of the given field.

        @param i. Position.
        @return PNfieldMetadata.
        """
        if position < 0 or position >= len(self.private._field_list):
            raise ValueError("Value n:%s out of bounds" % position)

        return self.private._field_list[position]


class PNTableMetaDataPrivate:
    """PNTableMetaData Class."""

    """
    Nombre de la tabla
    """

    _name: str

    """
    Alias de la tabla
    """
    _alias: str

    """
    Lista de campos que tiene esta tabla
    """
    _field_list: List["pnfieldmetadata.PNFieldMetaData"]

    """
    Clave compuesta que tiene esta tabla
    """
    _compound_key: Optional["pncompoundkeymetadata.PNCompoundKeyMetaData"] = None

    """
    Nombre de la consulta (fichero .qry) de la que define los metadatos
    """
    _query: str

    """
    Cadena de texto con los nombre de los campos separados por comas
    """
    _field_names: List[str] = []

    """
    Mapas alias<->nombre
    """
    _alias_field_map: Dict[str, str]
    _field_alias_map: Dict[str, str]

    """
    Lista de nombres de campos de la tabla que son del tipo FLFieldMetaData::Unlock
    """
    _field_names_unlock: List[str] = []

    """
    Clave primaria
    """
    _primary_key: Optional[str]

    """
    Indica si se debe avisar de colisión de concurrencia entre sesiones.

    Si este flag es true y dos o mas sesiones/usuarios están modificando los
    mismos campos,al validar un formulario (FLFormRecordDB::validateForm)
    mostrará un aviso de advertencia.

    Ver también FLSqlCursor::concurrencyFields().
    """
    _concur_warn: bool

    """
    Indica si se deben comprobar riesgos de bloqueos para esta tabla

    Si este flag es true FLSqlCursor::commitBuffer() chequeará siempre
    los riesgos de bloqueo para esta tabla.

    Ver también FLSqlDatabase::detectRisksLocks
    """
    _detect_locks: bool

    """
    Indica el nombre de función a llamar para la búsqueda con Full Text Search
    """
    full_text_search_function: str

    """
    Indica si lo metadatos están en caché (FLManager::cacheMetaData_)
    """
    _in_cache: bool

    count_ = 0

    def __init__(self, name: str = None, alias=None, qry_name: str = None) -> None:
        """
        Initialize the class.

        @param nane metadata name.
        @param alias metadata alias.
        @param qry_name query string.
        """
        self._name = ""
        self._primary_key = None
        self._field_list = []
        self._field_names = []
        self._field_names_unlock = []
        self._alias_field_map = {}
        self._field_alias_map = {}
        self._detect_locks = True
        self._query = ""
        self._in_cache = False
        # print("Vaciando field list ahora",  len(self._field_list))
        if name is None:
            self.inicializeFLTableMetaDataPrivate()
        elif name and not alias and not qry_name:
            self.inicializeFLTableMetaDataPrivateS(name)
        else:
            self.inicializeNewFLTableMetaDataPrivate(name, alias, qry_name)
        self.count_ += 1

    def inicializeFLTableMetaDataPrivate(self) -> None:
        """
        Initialize class ends with empty data.
        """

        self._compound_key = None

    def inicializeNewFLTableMetaDataPrivate(self, name: str, alias: str, query: str = None) -> None:
        """
        Initialize the class end with data.

        @param name metadata name.
        @param alias metadata alias.
        @param query query string.
        """

        self._name = name.lower()
        self._alias = alias
        self._compound_key = None
        if query is not None:
            self._query = query
        self._concur_warn = False
        self._detect_locks = False

    def inicializeFLTableMetaDataPrivateS(self, name: str) -> None:
        """
        Initialize the class end with basic data.

        @param name metadata name.
        """

        self._name = str(name)
        self._alias = self._name

    def addFieldName(self, name: str) -> None:
        """
        Add the name of a field to the field name string, see fieldNames().

        @param name Field Name.
        """

        self._field_names.append(name.lower())

    def removeFieldName(self, name: str) -> None:
        """
        Remove the name of a field from the field name string, see fieldNames().

        @param name Field Name
        """

        if name in self._field_names:
            self._field_names.remove(name)

        if name in self._field_names_unlock:
            self._field_names_unlock.remove(name)
        if self._primary_key == name:
            self._primary_key = None

    def formatAlias(self, field_object: Optional["pnfieldmetadata.PNFieldMetaData"] = None) -> None:
        """
        Format the alias of the indicated field to avoid duplicates.

        @param f Object field whose alias you want to format
        """

        if field_object is not None:
            alias = field_object.alias()
            field = field_object.name().lower()

            if alias in self._alias_field_map:
                alias = "%s(%s)" % (alias, str(len(self._alias_field_map) + 1))

            field_object.private.alias_ = alias

            self._alias_field_map[alias] = field
            self._field_alias_map[field] = alias

    def clearFieldList(self) -> None:
        """
        Clear the list of field definitions.
        """

        self._field_list = []
        self._field_names = []
