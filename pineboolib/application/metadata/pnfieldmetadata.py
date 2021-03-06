# -*- coding: utf-8 -*-
"""Manage the data of a field in a table."""

from pineboolib.core.utils.utils_base import aqtt

from pineboolib.core.utils import logging
from pineboolib.interfaces import IFieldMetaData

from typing import List, Optional, Union, Any, TYPE_CHECKING

from .pnrelationmetadata import PNRelationMetaData

if TYPE_CHECKING:
    from pineboolib.application.metadata.pntablemetadata import PNTableMetaData


LOGGER = logging.getLogger("PNFieldMetadata")


class PNFieldMetaData(IFieldMetaData):
    """PNFieldMetaData Class."""

    Serial = "serial"
    Unlock = "unlock"
    Check = "check"
    count_ = 0

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the metadata with the collected data.

        @param n Field Name.
        @param to Alias ​​del campo, used in form labels.
        @param aN TRUE if it allows nulls (NULL), FALSE if it allows them (NOT NULL).
        @param _isPrimaryKey TRUE if it is a primary key, FALSE if it is not a primary key, be
                primary key implies being Index and Unique.
        @param t Field type.
        @param l Length of the field in characters, provided it is of type string
               of characters.
        @param c Indicates if the field is calculated.
        @param v Indicates if the field is visible.
        @param ed Indicates if the field is editable.
        @param pI Indicates the number of digits of the whole part.
        @param pD Indicates the number of decimals.
        @param iNX TRUE if the field is index.
        @param uNI TRUE if the field determines unique records.
        @param coun Indicates if it is an accountant. For automatic references.
        @param defValue Default value for the field.
        @param oT Indicates if the changes in the field are out of transaction.
        @param rX Regular expression used as a validation mask.
        @param vG Indicates if the field is visible in the grid of the table.
        @param gen Indicates if the field is generated.
        @param iCK Indicates if it is a composite key.
        """

        if len(args) == 1:
            self.inicializeFLFieldMetaData(args[0])
        else:
            self.inicializeNewFLFieldMetaData(*args, **kwargs)
        ++self.count_

    def inicializeFLFieldMetaData(self, other: "PNFieldMetaData") -> None:
        """Initialize by copying information from another metadata."""

        self.private = PNFieldMetaDataPrivate()
        self.copy(other)

    def inicializeNewFLFieldMetaData(
        self,
        n: str,
        a: str,
        aN: bool,
        isPrimaryKey: bool,
        t: str,
        length_: int = 0,
        c: bool = False,
        v: bool = True,
        ed: bool = True,
        pI: int = 4,
        pD: int = 0,
        iNX: bool = False,
        uNI: bool = False,
        coun: bool = False,
        defValue: Optional[str] = None,
        oT: bool = False,
        rX: Optional[str] = None,
        vG: bool = True,
        gen: bool = True,
        iCK: bool = False,
    ) -> None:
        """
        Initialize with the information collected.

        @param n Field Name.
        @param to Alias ​​del campo, used in form labels.
        @param aN TRUE if it allows nulls (NULL), FALSE if it allows them (NOT NULL).
        @param _isPrimaryKey TRUE if it is a primary key, FALSE if it is not a primary key, be
                primary key implies being Index and Unique.
        @param t Field type.
        @param l Length of the field in characters, provided it is of type string
               of characters.
        @param c Indicates if the field is calculated.
        @param v Indicates if the field is visible.
        @param ed Indicates if the field is editable.
        @param pI Indicates the number of digits of the whole part.
        @param pD Indicates the number of decimals.
        @param iNX TRUE if the field is index.
        @param uNI TRUE if the field determines unique records.
        @param coun Indicates if it is an accountant. For automatic references.
        @param defValue Default value for the field.
        @param oT Indicates if the changes in the field are out of transaction.
        @param rX Regular expression used as a validation mask.
        @param vG Indicates if the field is visible in the grid of the table.
        @param gen Indicates if the field is generated.
        @param iCK Indicates if it is a composite key.
        """
        self.private = PNFieldMetaDataPrivate(
            n,
            a,
            aN,
            isPrimaryKey,
            t,
            length_,
            c,
            v,
            ed,
            pI,
            pD,
            iNX,
            uNI,
            coun,
            defValue,
            oT,
            rX,
            vG,
            gen,
            iCK,
        )

    def name(self) -> str:
        """
        Get the name of the field.

        @return Field Name.
        """
        if self.private._field_name is None:
            return ""
        return self.private._field_name

    def setName(self, name: str) -> None:
        """
        Set the name for the field.

        @param n Field Name
        """

        self.private._field_name = name

    def alias(self) -> str:
        """
        Get the alias of the field.

        @return Alias Name.
        """

        return aqtt(self.private.alias_)

    def allowNull(self) -> bool:
        """
        Get if it allows nulls.

        @return TRUE if it allows nulls, FALSE otherwise
        """

        return self.private._allow_null

    def isPrimaryKey(self) -> bool:
        """
        Get if it is primary key.

        @return TRUE if it is primary key, FALSE otherwise
        """

        return self.private.is_primary_key

    def setIsPrimaryKey(self, value: bool) -> None:
        """
        Set if it is primary key.

        @return TRUE if it is primary key, FALSE otherwise
        """

        self.private.is_primary_key = value

    def isCompoundKey(self) -> bool:
        """
        Get if it is a composite key.

        @return TRUE if it is a composite key, FALSE otherwise
        """

        if self.private.is_compound_key is None:
            return False
        return self.private.is_compound_key

    def type(self) -> str:
        """
        Return the type of the field.

        @return The field type.
        """

        return str(self.private.type_)

    def length(self) -> int:
        """
        Get the length of the field.

        @return The length of the field.
        """

        return int(self.private.length_ or 0)

    def calculated(self) -> Any:
        """
        Get if the field is calculated.

        @return TRUE if the field is calculated, FALSE otherwise
        """

        return self.private.calculated_

    def setCalculated(self, calculated) -> None:
        """
        Set if the field is calculated.

        @param calculated Value TRUE if you want to set the field as calculated, FALSE otherwise.
        """
        self.private.calculated_ = calculated

    def editable(self) -> bool:
        """
        Get if the field is editable.

        @return TRUE if the field is editable, FALSE otherwise
        """
        return self.private.editable_ if self.private.editable_ is not None else False

    def setEditable(self, editable: bool) -> None:
        """
        Set whether the field is editable.

        @param ed Value TRUE if you want the field to be editable, FALSE otherwise.
        """
        self.private.editable_ = editable

    def visible(self) -> bool:
        """
        Get if the field is visible.

        @return TRUE if the field is visible, FALSE otherwise
        """
        return self.private.visible_

    def visibleGrid(self) -> bool:
        """
        Get if the field is visible in the grid of the table.

        @return TRUE if the field is visible in the grid of the table, FALSE otherwise
        """
        return self.private._visible_grid

    def generated(self) -> bool:
        """@return TRUE if the field is generated, that is, it is included in the queries."""

        return self.private.generated_

    def setGenerated(self, generated: bool) -> None:
        """Set a field as generated."""

        self.private.generated_ = generated

    def setVisible(self, visible: bool) -> None:
        """
        Set if the field is visible.

        @param v Value TRUE if you want to make the field visible, FALSE otherwise.
        """

        self.private.visible_ = visible

    def setVisibleGrid(self, visible_grid: bool) -> None:
        """
        Set whether the field is visible in the grid of the table.

        @param v Value TRUE if you want to make the field visible, FALSE otherwise.
        """

        self.private._visible_grid = visible_grid

    def partInteger(self) -> int:
        """
        Get the number of digits of the whole part.

        @return The number of digits of the entire part of the field.
        """

        return int(self.private._part_integer or 0)

    def partDecimal(self) -> int:
        """
        Get the number of digits of the decimal part.

        @return The number of digits of the decimal part of the field.
        """

        return int(self.private._part_decimal or 0)

    def isCounter(self) -> bool:
        """
        Get if the field is a counter.

        @return TRUE if the field is a reference with counter
        """
        return self.private.contador_

    def isIndex(self) -> bool:
        """
        Get if the field is index.

        @return TRUE if the field is index, FALSE otherwise
        """
        return self.private._is_index

    def isUnique(self) -> bool:
        """
        Get if the field determines unique records.

        @return TRUE if the field determines unique records, FALSE otherwise
        """
        return self.private._is_unique

    def addRelationMD(self, r: "PNRelationMetaData") -> None:
        """
        Add a relationship with another table for this field.

        Add a new FLRelationMetaData object to the list of relationships for this field.
        Note that for one field there can only be one single ratio of type M1 (many to one), so in
        in case you want to add several relationships of this type for the field only the first one will be taken into account.
        Type 1M relationships (one to many) may all exist those necessary. See FLRelationMetaData :: Cardinality.

        @param r FlRelationMetaData object with the definition of the relationship to add.
        """

        is_relation_m1 = False
        # print("FLFieldMetadata(%s).addRelationMD(card %s)" % (self.name(), r.cardinality()))

        if r.cardinality() == PNRelationMetaData.RELATION_M1:
            is_relation_m1 = True
        if is_relation_m1 and self.private._relation_m1:
            LOGGER.debug(
                "addRelationMD: Se ha intentado crear más de una relación muchos a uno para el mismo campo"
            )
            return
        if self.private._field_name is None:
            LOGGER.warning("addRelationMD: no fieldName")
            return
        r.setField(self.private._field_name)
        if is_relation_m1:
            self.private._relation_m1 = r
            return

        if not self.private._relation_list:
            self.private._relation_list = []

        self.private._relation_list.append(r)

    def relationList(self) -> List["PNRelationMetaData"]:
        """
        To get the list of relationship definitions.

        Does not include the M1 relationship

        @return Object with the list of deficits in the field relations
        """

        return self.private._relation_list

    def relationM1(self) -> Optional["PNRelationMetaData"]:
        """
        Get the many-to-one relationship for this field.

        Not included in relationList ()

        @return Object FLRelationMetaData with the description of the relationship many to one for this field.
        """
        return self.private._relation_m1

    def setAssociatedField(self, r_or_name: Union[str, IFieldMetaData], f: str) -> None:
        """
        Set an associated field for this field, and the name of the foreign table field to use to filter.

            according to the value of the associated field.

        @param r FLFieldMetaData object or Name that defines the field to be associated with this
        @param f Name of the field to apply the filter

        """
        name = r_or_name.name() if not isinstance(r_or_name, str) else r_or_name

        self.private.associated_field_name = name
        self.private.associated_field_filter_to = f

    def associatedField(self) -> Optional["PNFieldMetaData"]:
        """
        Return the associated field for this field.

        @return FLFieldMetaData object that defines the field associated with it, or 0 if there is no associated field.
        """
        mtd = self.metadata()
        if mtd is None:
            return None
        return mtd.field(self.private.associated_field_name)

    def associatedFieldFilterTo(self) -> str:
        """
        Return the name of the field to be filtered according to the associated field.

        @return Field name of the foreign table M-1, to which the filter must be applied according to the value of the associated field.
        """
        return self.private.associated_field_filter_to

    def associatedFieldName(self) -> Optional[str]:
        """
        Return the name of the associated field this.

        @return Name of the associated field.
        """

        return self.private.associated_field_name

    def defaultValue(self) -> Optional[Union[Any]]:
        """
        Return the default value for the field.

        @return Value that is assigned to the field by default
        """

        if self.private._default_value in (None, "null"):
            self.private._default_value = None

        if self.private.type_ in ("bool", "unlock") and isinstance(
            self.private._default_value, str
        ):
            return self.private._default_value == "true"

        return self.private._default_value

    def outTransaction(self) -> bool:
        """
        Return if the field is modified out of transaction.

        @return TRUE if the field is modified out of transaction, FALSE otherwise
        """
        return self.private._out_transaction if self.private._out_transaction is not None else False

    def regExpValidator(self) -> Optional[str]:
        """
        Return the regular expression that serves as a validation mask for the field.

        @return Character string containing a regular expression, used as
            mask to validate the values ​​entered in the field
        """
        return self.private._reg_exp_validator

    def optionsList(self) -> List[str]:
        """
        Return the list of options for the field.

        @return List of field options
        """
        return self.private._options_list

    def getIndexOptionsList(self, name: str) -> Optional[int]:
        """
        Return the index of a given field.

        @return List of field options.
        """
        if name in self.private._options_list:
            return self.private._options_list.index(name)

        return None

    def setOptionsList(self, ol: str) -> None:
        """
        Set the list of options for the field.

        @param ol Text string with options for the field.
        """
        self.private._options_list = []
        if ol.find("QT_TRANSLATE") != -1:
            for componente in ol.split(";"):
                self.private._options_list.append(aqtt(componente))
        else:
            for componente in ol.split(","):
                self.private._options_list.append(aqtt(componente))

    def isCheck(self) -> bool:
        """
        Get if the field is of type Check.
        """

        if self.private.type_ == self.Check:
            return True
        else:
            return False

    def hasOptionsList(self) -> bool:
        """
        Get if the field has a list of options.
        """

        return True if self.private._options_list else False

    def fullyCalculated(self) -> bool:
        """
        Return if a field is fully calculated.
        """

        return self.private._fully_calculated

    def setFullyCalculated(self, c: bool) -> None:
        """
        Specify if a field is fully calculated.
        """

        self.private._fully_calculated = c
        if c:
            self.private.generated_ = True

    def trimed(self) -> bool:
        """Return if a field is trimmed."""

        return self.private.trimmed_

    def setTrimed(self, t: bool) -> None:
        """Specify if a field is trimmed."""

        self.private.trimmed_ = t

    def setMetadata(self, mtd: "PNTableMetaData") -> None:
        """
        Set the PNTableMetaData object to which it belongs.
        """
        self.private.mtd_ = mtd

    def metadata(self) -> Optional["PNTableMetaData"]:
        """
        Get the FLTableMetaData object to which it belongs.
        """

        return self.private.mtd_

    def flDecodeType(self, fltype_=None) -> Optional[str]:
        """
        Get the type of the field converted to an equivalent type of the QVariant class.
        """

        _type = None
        # print("Decode", fltype)

        if fltype_ == "int":
            _type = "int"
        elif fltype_ in ("serial", "uint"):
            _type = "uint"
        elif fltype_ in ("bool", "unlock"):
            _type = "bool"
        elif fltype_ == "double":
            _type = "double"
        elif fltype_ == "time":
            _type = "time"
        elif fltype_ == "date":
            _type = "date"
        elif fltype_ in ("string", "pixmap", "stringlist", "timestamp"):
            _type = "string"
        elif fltype_ == "bytearray":
            _type = "bytearray"

        # print("Return", _type)
        return _type

    def searchOptions(self) -> Any:
        """
        Return different search options for this field.

        @return list of different options
        """

        return self.private._search_options

    def setSearchOptions(self, options_list: str) -> None:
        """
        Set the list of options for the field.

        @param ol Text string with options for the field.
        """

        self.private._search_options = []
        for dato in options_list.split(","):
            self.private._search_options.append(dato)

    def copy(self, other: "PNFieldMetaData") -> None:
        """
        Copy the metadata of another pnfieldmetadata.
        """

        if other is self:
            return

        other_private = other.private

        if other_private._relation_m1:
            self.private._relation_m1 = other_private._relation_m1

        self.private.clearRelationList()

        if other_private._relation_list:
            for relation in other_private._relation_list:
                self.private._relation_list.append(relation)

        self.private._field_name = other_private._field_name
        self.private.alias_ = other_private.alias_
        self.private._allow_null = other_private._allow_null
        self.private.is_primary_key = other_private.is_primary_key
        self.private.type_ = other_private.type_
        self.private.length_ = other_private.length_
        self.private.calculated_ = other_private.calculated_
        self.private._fully_calculated = other_private._fully_calculated
        self.private.trimmed_ = other_private.trimmed_
        self.private.visible_ = other_private.visible_
        self.private.editable_ = other_private.editable_
        self.private._part_decimal = other_private._part_decimal
        self.private._part_integer = other_private._part_integer
        self.private._is_index = other_private._is_index
        self.private._is_unique = other_private._is_unique
        self.private.contador_ = other_private.contador_
        self.private.associated_field_name = other_private.associated_field_name
        self.private.associated_field_filter_to = other_private.associated_field_filter_to
        self.private._default_value = other_private._default_value
        self.private._options_list = other_private._options_list
        self.private._out_transaction = other_private._out_transaction
        self.private._reg_exp_validator = other_private._reg_exp_validator
        self.private._visible_grid = other_private._visible_grid
        self.private.generated_ = other_private.generated_
        self.private.is_compound_key = other_private.is_compound_key

        # self = copy.deepcopy(other)

    def formatAssignValue(self, field_name: str, value: Any, upper: bool) -> str:
        """
        Return the correct comparison for a given field.
        """

        if value is None or not field_name:
            return "1 = 1"

        is_text = False
        # if isinstance(value, str):
        if self.type() in ("string", "time", "date", "pixmap", "timestamp"):
            is_text = True

        format_value: Any = None

        if is_text:
            format_value = "'%s'" % value
        else:
            format_value = value

        # if isinstance(value, (int, float)):
        # format_value = str(value)
        # else:
        # format_value = "'" + str(value) + "'"

        # print("format_value es %s, %s y value era %s" % (format_value, type(format_value), value.toString()))

        # if format_value == None:
        #    return "1 = 1"

        if upper and is_text:
            field_name = "upper(%s)" % field_name
            format_value = format_value.upper()

        return "%s = %s" % (field_name, format_value)

    def __len__(self) -> int:
        """Return the length of a field."""

        return self.private.length_ if self.private.length_ is not None else 0


class PNFieldMetaDataPrivate(object):
    """PNFieldMetaDataPrivate Class."""

    """
    Nombre del campo en la tabla
    """

    _field_name = None

    """
    Alias o mote para el campo, usado como
    etiqueta de campos en los formularios
    """
    alias_ = None

    """
    Almacena si el campo permite ser nulo
    """
    _allow_null: bool

    """
    Almacena si el campo es clave primaria
    """
    is_primary_key: bool

    """
    Tipo del campo
    """
    type_ = None

    """
    Longitud del campo
    """
    length_ = None

    """
    Indica si el campo es calculado de forma diferida.
    Esto indica que el campo se calcula al editar o insertar un registro, en el commit.
    """
    calculated_: bool

    """
    Indica si el campo es totalmente calculado.
    Esto indica que el valor campo del campo es dinámico y se calcula en cada refresco.
    Un campo totalmente calculado implica que es generado.
    """
    _fully_calculated: bool

    """
    Indica que al leer el campo de la base de datos los espacios mas a la derecha
    son eliminados.
    """
    trimmed_: bool

    """
    Indica si el campo es visible
    """
    visible_: bool

    """
    Indica si el campo es editable
    """
    editable_ = None

    """
    Indica el número de dígitos de la parte entera
    """
    _part_integer = None

    """
    Indica el númeor de dígitos de la parte decimal
    """
    _part_decimal = None

    """
    Indica si el campo es índice
    """
    _is_index: bool

    """
    Indica si el campo es único
    """
    _is_unique: bool

    """
    Indica si el campo es un contador de referencia y abanq en el
    momento de insertar un registro debe intentar calcular cual sería el
    siguiente numero.

    @author Andrés Otón Urbano (andresoton@eresmas.com)
    """
    contador_: bool

    """
    Lista de relaciones para este campo
    """
    _relation_list: List["PNRelationMetaData"] = []

    """
    Mantiene, si procede, la relación M1 (muchos a uno)
    para el campo (solo puede haber una relacion de este tipo para un campo)
    """
    _relation_m1: Any = None

    """
    Asocia este campo con otro, para efectuar filtros en búsquedas.

    El campo que se asocia a este debe tener una relación M-1.
    Este campo también debe tener una relación M-1. Al asociar un campo a este,
    las búsquedas mediante los botones de búsqueda en los formularios de edición
    de registros vendrán condicionadas por el valor del campo asociado en el
    momento de realizar dicha búsqueda. Cuando se realiza una búsqueda para
    este campo la tabla relacionada con él (M-1) será mostrada para elegir un
    registro de todos los posibles, en el caso normal se muestran todos los registros,
    pero cuando se asocia un campo sólo se muestran aquellos registros que satisfagan el
    valor del campo asociado. Ejemplo : En la tabla albaranes asociamos el campo
    'codemporig' al campo 'codalmorig' (NO es lo mismo que asociar 'codalmorig'
    a 'codemporig') cuando abrimos el formulario de albaranes elegimos una empresa
    origen (codemporig), cuando vayamos a elegir un almacen origen (codalmorig) sólo
    se podrá elegir entre los almacenes que son de la empresa origen , ya que el formulario
    de búsqueda sólo se mostrarán los almacenes cuyo código de empresa
    (ver FLFieldMetaData::associated_field_filter_to) sea igual al valor de la empresa origen
    elegida (codemporig)
    """
    associated_field_name = ""

    """
    Nombre del campo que se debe filtra según el campo asociado.

    Esta propiedad sólo tiene sentido cuando hay un campo asociado a este,
    ver FLFieldMetaData ::associatedField_ , y si ese campo tiene una relacion M-1. Indica
    el nombre del campo de la tabla foránea en la relación M-1, que se debe utilizar para filtrar
    los registros según el valor del campo asociado. Ejemplo : En la tabla albaranes asociamos el campo
    'codemporig' al campo 'codalmorig' (NO es lo mismo que asociar 'codalmorig'
    a 'codemporig'), e indicamos que el campo de filtro es 'codempresa' de la tabla relacionada M-1 con el
    campo 'codalmorig' (Almacenes) . Cuando abrimos el formulario de albaranes elegimos una empresa
    origen (codemporig), cuando vayamos a elegir un almacen origen (codalmorig) sólo se podrá elegir
    entre los almacenes que son de la empresa origen, ya que el formulario de búsqueda sólo se mostrarán
    los almacenes cuyo código de empresa (el campo indicado de filtro ) sea igual al valor de la empresa
    origen elegida (codemporig)
    """
    associated_field_filter_to = ""

    """
    Valor por defecto para el campo
    """
    _default_value = None

    """
    Lista de opciones para el campo
    """
    _options_list: List[str]

    """
    Indica si las modificaciones del campo se hacen fuera de cualquier transaccion.

    Al estar activado este flag, todos los cambios en el valor de este campo se
    realizan fuera de la transaccion y de forma exclusiva. Es decir los cambios
    realizados en el campo son inmediatamente reflejados en la tabla sin esperar a
    que se termine transaccion, y de forma exclusiva (bloqueando el registro al que
    pertenece el campo mientras se modifica). Esto permite en el acto hacer visibles
    para todas las demas conexiones de la base de datos los cambios realizados en un campo.
    Hay que tener en cuenta que al tener el campo esta caracteristica especial de modificarse
    fuera de la transaccion, el "rollback" no tendra efecto sobre los cambios realizados
    en el y siempre permanecera en la base de datos la ultima modificacion efectuada en
    el campo.
    """
    _out_transaction = None

    """
    Almacena la expresion regular que sirve como mascara de validacion para el campo.
    """
    _reg_exp_validator = None

    """
    Indica si el campo debe ser visible en la rejilla de la tabla.
    """
    _visible_grid = True

    """
    Indica si el campo es generado, es decir, se incluye en las consultas
    """
    generated_ = False

    """
    Almacena si el campo es clave compuesta
    """
    is_compound_key = None

    """
    Contiene las distintas opciones de búsqueda
    """
    _search_options: List[str]

    """
    Objeto FLTableMetaData al que pertenece
    """
    mtd_: Optional["PNTableMetaData"] = None

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the class."""

        self._reg_exp_validator = ""
        self._search_options = []
        self._allow_null = False
        self.is_primary_key = False

        if not args:
            self.inicializeEmpty()
        else:
            self.inicialize(*args, **kwargs)

    def inicializeEmpty(self) -> None:
        """Fill in the data without information."""

        self._relation_list = []
        self._relation_m1 = None
        self.associated_field_filter_to = ""
        self.associated_field_name = ""
        self.mtd_ = None

    def inicialize(
        self,
        name: str,
        alias: str,
        allow_null: bool,
        is_primary_key: bool,
        type_: Optional[str],
        length_: int,
        calculated: bool,
        visible: bool,
        editable: bool,
        part_integer: int,
        part_decimal: int,
        is_index: bool,
        is_unique: bool,
        coun: bool,
        default_value: Optional[str],
        out_transaction: bool,
        regular_expression: Optional[str],
        visible_grid: bool,
        gen: bool,
        is_compound_key: bool,
    ) -> None:
        """
        Fill in the data with information.

        @param name Field Name.
        @param alias ​​used in form labels.
        @param allow_null TRUE if it allows nulls (NULL), FALSE if it allows them (NOT NULL).
        @param is_primary_key TRUE if it is a primary key, FALSE if it is not a primary key, be
                primary key implies being Index and Unique.
        @param type_ Field type.
        @param length_ Length of the field in characters, provided it is of type string
               of characters.
        @param calculated Indicates if the field is calculated.
        @param visible Indicates if the field is visible.
        @param ed Indicates if the field is editable.
        @param part_integer Indicates the number of digits of the whole part.
        @param part_decimal Indicates the number of decimals.
        @param is_index TRUE if the field is index.
        @param is_unique TRUE if the field determines unique records.
        @param coun Indicates if it is an accountant. For automatic references.
        @param default_value Default value for the field.
        @param out_transaction Indicates if the changes in the field are out of transaction.
        @param regular_expression Regular expression used as a validation mask.
        @param visible_grid Indicates if the field is visible in the grid of the table.
        @param gen Indicates if the field is generated.
        @param is_compound_key Indicates if it is a compound key.
        """

        self._field_name = name.lower()
        self.alias_ = alias
        if calculated:
            self._allow_null = True
        else:
            self._allow_null = allow_null
        self.is_primary_key = is_primary_key
        self.type_ = type_
        self.length_ = length_
        self.calculated_ = calculated
        self.visible_ = visible
        self.editable_ = editable
        self._part_integer = part_integer
        self._part_decimal = part_decimal
        self._is_index = is_index
        self._is_unique = is_unique
        self.contador_ = coun
        self._relation_list = []
        self._relation_m1 = None
        self.associated_field_filter_to = ""
        self.associated_field_name = ""
        self._default_value = default_value
        self._out_transaction = out_transaction
        self._reg_exp_validator = regular_expression
        self._visible_grid = visible_grid
        self.generated_ = gen
        self.is_compound_key = is_compound_key
        self.mtd_ = None
        self._fully_calculated = False
        self.trimmed_ = False
        self._options_list = []

        if self.type_ is None:
            if self._part_decimal > 0:
                self.type_ = "double"
            elif self.length_ > 0:
                self.type_ = "string"
            else:
                self.type_ = "uint"
            LOGGER.info(
                "%s:: El campo %s no tiene especificado tipo y se especifica tipo %s",
                __name__,
                self._field_name,
                self.type_,
            )

        if int(length_) < 0:
            self.length_ = 0

        if int(part_integer) < 0:
            self._part_integer = 0
        if int(part_decimal) < 0:
            self._part_decimal = 0
        # print("Tipo ", t)

        if not type_ == "string" and not int(length_) == 0:
            self.length_ = 0

        # if not t == "int" and not t == "uint" and t == "double" and not int(pI) == 0:
        # self._part_integer = 0

        elif type_ == "double" and not int(part_decimal) >= 0:
            self._part_decimal = 0

    def __del_(self):
        """
        Delete properties when deleted.
        """
        self.clearRelationList()
        if self._relation_m1 and self._relation_m1.deref():
            self._relation_m1 = None

    def clearRelationList(self) -> None:
        """
        Clear the list of relationship definitions.
        """
        self._relation_list = []
