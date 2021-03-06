"""Fltabledb module."""

# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

from pineboolib.application.database import pnsqlcursor
from pineboolib.application.metadata import pnfieldmetadata, pnrelationmetadata
from pineboolib.application.qsatypes import sysbasetype

from pineboolib.q3widgets import qtable

from pineboolib.core.utils import utils_base
from pineboolib.core import decorators, settings

from pineboolib import application

from pineboolib import logging

from . import (
    fldatatable,
    flformsearchdb,
    flutil,
    flformrecorddb,
    fldoublevalidator,
    fluintvalidator,
    flintvalidator,
    flcheckbox,
    fltimeedit,
    fldateedit,
    flspinbox,
)

from pineboolib.fllegacy.aqsobjects import aqods

from typing import Any, Optional, List, Union, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces import isqlcursor


logger = logging.getLogger(__name__)
DEBUG = False


class FLTableDB(QtWidgets.QWidget):
    """
    PLUGIN that contains a database table.

    This object contains everything needed to handle
    the data in a table. In addition to the functionality of
    Search the table by a field, using filters.

    This plugin to be functional must have as one
    from your parents or predecessor to an FLFormDB object.

    @author InfoSiAL S.L.
    """

    """
    Tipos de condiciones para el filtro
    """
    All: int = 0
    Contains: int = 1
    Starts: int = 2
    End: int = 3
    Equal: int = 4
    Dist: int = 5
    Greater: int = 6
    Less: int = 7
    FromTo: int = 8
    Null: int = 9
    NotNull: int = 10

    _parent: QtWidgets.QWidget
    _name: str
    loadLater_: bool

    tdbFilter: Optional[Any]

    pbData: QtWidgets.QPushButton
    pbFilter: QtWidgets.QPushButton
    pbOdf: QtWidgets.QPushButton

    comboBoxFieldToSearch: QtWidgets.QComboBox
    comboBoxFieldToSearch2: QtWidgets.QComboBox
    lineEditSearch: QtWidgets.QLineEdit

    tabDataLayout: QtWidgets.QVBoxLayout
    tabControlLayout: QtWidgets.QHBoxLayout

    dataLayout: QtWidgets.QHBoxLayout
    tabData: QtWidgets.QFrame
    tabFilter: QtWidgets.QFrame
    buttonsLayout: QtWidgets.QVBoxLayout
    masterLayout: QtWidgets.QVBoxLayout
    tabFilterLoaded: bool

    _loaded: bool
    """
    Tamaño de icono por defecto
    """
    iconSize: Optional[Any]

    """
    Componente para visualizar los registros
    """
    tableRecords_: Optional[fldatatable.FLDataTable]

    """
    Nombre de la tabla a la que esta asociado este componente.
    """
    tableName_: Optional[str]

    """
    Nombre del campo foráneo
    """
    foreignField_: Optional[str]

    """
    Nombre del campo de la relación
    """
    fieldRelation_: Optional[str]

    """
    Cursor con los datos de origen para el componente
    """
    cursor_: "isqlcursor.ISqlCursor"

    """
    Cursor auxiliar de uso interno para almacenar los registros de la tabla
    relacionada con la de origen
    """
    cursorAux: Optional["isqlcursor.ISqlCursor"]

    """
    Matiene la ventana padre
    """
    topWidget: Optional[QtWidgets.QWidget]

    """
    Indica que la ventana ya ha sido mostrada una vez
    """
    showed: bool

    """
    Mantiene el filtro de la tabla
    """
    filter_: str

    """
    Almacena si el componente está en modo sólo lectura
    """
    readonly_: bool
    reqReadOnly_: bool

    """
    Almacena si el componente está en modo sólo edición
    """
    editonly_: bool
    reqEditOnly_: bool

    """
    Indica si el componente está en modo sólo permitir añadir registros
    """
    insertonly_: bool
    reqInsertOnly_: bool

    """
    Almacena los metadatos del campo por el que está actualmente ordenada la tabla
    """
    sortField_: Optional[pnfieldmetadata.PNFieldMetaData]

    """
    Almacena los metadatos del campo por el que está actualmente ordenada la tabla en segunda instancia

    @author Silix - dpinelo
    """
    sortField2_: Optional[pnfieldmetadata.PNFieldMetaData]

    """
    Crónometro interno
    """
    timer: Optional[QtCore.QTimer]

    """
    Filtro inicial de búsqueda
    """
    initSearch_: Optional[str]

    """
    Indica que la columna de seleción está activada
    """
    checkColumnEnabled_: bool

    """
    Indica el texto de la etiqueta de encabezado para la columna de selección
    """
    aliasCheckColumn_: str

    """
    Indica el nombre para crear un pseudocampo en el cursor para la columna de selección
    """
    fieldNameCheckColumn_: str

    """
    Indica que la columna de selección está visible
    """
    checkColumnVisible_: bool

    """
    Indica el número de columna por la que ordenar los registros
    """
    sortColumn_: int

    """
    Indica el número de columna por la que ordenar los registros

    @author Silix - dpinelo
    """
    sortColumn2_: int

    """
    Indica el número de columna por la que ordenar los registros

    @author Silix
    """
    sortColumn3_: int

    """
    Indica el sentido ascendente o descendente del la ordenacion actual de los registros
    """
    orderAsc_: bool

    """
    Indica el sentido ascendente o descendente del la ordenacion actual de los registros

    @author Silix - dpinelo
    """
    orderAsc2_: bool

    """
    Indica el sentido ascendente o descendente del la ordenacion actual de los registros

    @author Silix
    """
    orderAsc3_: bool

    """
    Indica si se debe establecer automáticamente la primera columna como de ordenación
    """
    autoSortColumn_: bool

    """
    Almacena la última claúsula de filtro aplicada en el refresco
    """
    tdbFilterLastWhere_: Optional[str]

    """
    Diccionario que relaciona literales descriptivos de una condición de filtro
    con su enumeración
    """
    mapCondType: List[str]

    """
    Indica si el marco de búsqueda está oculto
    """
    findHidden_: bool

    """
    Indica si el marco para conmutar entre datos y filtro está oculto
    """
    filterHidden_: bool

    """
    Indica si se deben mostrar los campos tipo pixmap en todas las filas
    """
    showAllPixmaps_: bool

    """
    Nombre de la función de script a invocar para obtener el color y estilo de las filas y celdas

    El nombre de la función debe tener la forma 'objeto.nombre_funcion' o 'nombre_funcion',
    en el segundo caso donde no se especifica 'objeto' automáticamente se añadirá como
    prefijo el nombre del formulario donde se inicializa el componente FLTableDB seguido de un punto.
    De esta forma si utilizamos un mismo formulario para varias acciones, p.e. master.ui, podemos controlar
    si usamos distintas funciones de obtener color para cada acción (distintos nombres de formularios) o
    una única función común para todas las acciones.

    Ej. Estableciendo 'tdbGetColor' si el componente se inicializa en el formulario maestro de clientes,
    se utilizará 'formclientes.tdbGetColor', si se inicializa en el fomulario maestro de proveedores, se
    utilizará 'formproveedores.tdbGetColor', etc... Si establecemos 'flfactppal.tdbGetColor' siempre se llama a
    esa función independientemente del formulario en el que se inicialize el componente.

    Cuando se está pintando una celda se llamará a esa función pasándole cinco parámentros:
    - Nombre del campo correspondiente a la celda
    - Valor del campo de la celda
    - Cursor de la tabla posicionado en el registro correspondiente a la fila que
      está pintando. AVISO: En este punto los valores del buffer son indefinidos, no se hace refreshBuffer
      por motivos de eficiencia
    - Tipo del campo, ver flutil.FLUtilInterface::Type en FLObjectFactory.h
    - Seleccionado. Si es TRUE indica que la celda a pintar está en la fila resaltada/seleccionada.
      Generalmente las celdas en la fila seleccionada se colorean de forma distinta al resto.

    La función debe devolver una array con cuatro cadenas de caracteres;

    [ "color_de_fondo", "color_lapiz", "estilo_fondo", "estilo_lapiz" ]

    En los dos primeros, el color, se puede utilizar cualquier valor aceptado por QColor::setNamedColor, ejemplos;

    "green"
    "#44ADDB"

    En los dos últimos, el estilo, se pueden utilizar los valores aceptados por QBrush::setStyle y QPen::setStyle,
    ver en fldatatable.FLDataTable.cpp las funciones nametoBrushStyle y nametoPenStyle, ejemplos;

    "SolidPattern"
    "DiagCrossPattern"
    "DotLine"
    "SolidLine"

    Si alguno de los valores del array es vacio "", entonces se utilizarán los colores o estilos establecidos por defecto.
    """
    functionGetColor_: Optional[str]

    """
    Indica que no se realicen operaciones con la base de datos (abrir formularios). Modo "sólo tabla".
    """
    onlyTable_: bool
    reqOnlyTable_: bool

    """
    Editor falso
    """
    fakeEditor_: Optional[Any] = None

    tableDB_filterRecords_functionName_: Optional[str]

    def __init__(
        self, parent: Optional["QtWidgets.QWidget"] = None, name: Optional[str] = None
    ) -> None:
        """
        Inicialize.
        """
        if parent is None:
            return
        super(FLTableDB, self).__init__(parent)
        self.topWidget = parent
        self.tableRecords_ = None
        self.tableName_ = None
        self.foreignField_ = None
        self.fieldRelation_ = None
        self.cursorAux = None
        self.showAllPixmaps_ = True
        self.showed = False
        self.filter_ = ""
        self.sortColumn_ = 0
        self.sortColumn2_ = 1
        self.sortColumn3_ = 2
        self.sortField_ = None
        self.initSearch_ = None
        self.autoSortColumn_ = True
        self.orderAsc_ = True
        self.orderAsc2_ = True
        self.orderAsc3_ = True
        self.readonly_ = False
        self.editonly_ = False
        self.onlyTable_ = False
        self.insertonly_ = False
        self.reqReadOnly_ = False
        self.reqEditOnly_ = False
        self.reqInsertOnly_ = False
        self.reqOnlyTable_ = False
        self.tabFilterLoaded = False
        self.timer_1 = QtCore.QTimer(self)
        if name:
            self.setObjectName(name)
        self.checkColumnVisible_ = False
        self.checkColumnEnabled_ = False
        self.tdbFilterLastWhere_ = None
        self.filter_ = ""

        self.iconSize = []

        self.iconSize = application.PROJECT.DGI.iconSize()

        self.tabControlLayout = QtWidgets.QHBoxLayout()
        self.tabFilter = QtWidgets.QFrame()  # contiene filtros
        self.tabFilter.setObjectName("tdbFilter")
        self.tabData = QtWidgets.QFrame()  # contiene data
        self.tabData.setObjectName("tabTable")
        self.functionGetColor_ = None

        from . import flformdb

        while not isinstance(self.topWidget, flformdb.FLFormDB):
            self.topWidget = self.topWidget.parentWidget()
            if not self.topWidget:
                break

        self._loaded = False
        self.createFLTableDBWidget()

    # def __getattr__(self, name):
    #    return DefFun(self, name)

    def load(self) -> None:
        """Initialize the cursor and controls."""

        # Es necesario pasar a modo interactivo lo antes posible
        # Sino, creamos un bug en el cierre de ventana: se recarga toda la tabla para saber el tamaño
        # print("FLTableDB(%s): setting columns in interactive mode" % self._tableName))
        if self.loaded():
            return

        if self.topWidget is not None:
            if not self.topWidget.cursor():
                logger.warning(
                    "FLTableDB : Uno de los padres o antecesores de FLTableDB deber ser de la clase FLFormDB o heredar de ella"
                )
                return

            self.cursor_ = cast(pnsqlcursor.PNSqlCursor, self.topWidget.cursor())

        self.initCursor()
        # self.setFont(QtWidgets.QApplication.font())

        if not self.objectName():
            self.setObjectName("FLTableDB")

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refreshDelayed)

        # FIXME: El problema de que aparezca al editar un registro que no es, es por carga doble de initCursor()
        # ...... Cuando se lanza showWidget, y tiene _initCursorWhenLoad, lanza initCursor y luego otra vez.
        # ...... esta doble carga provoca el error y deja en el formulario el cursor original.

        self.mapCondType = []

        self._loaded = True
        self.showWidget()

        if DEBUG:
            logger.warning(
                "**FLTableDB::name: %r cursor: %r", self.objectName(), self.cursor().curName()
            )

    def loaded(self) -> bool:
        """Return if the control is inicilized."""

        return self._loaded

    def initCursor(self) -> None:
        """
        Start the cursor according to this field either from the source table or from a related table.
        """
        if not self.topWidget or not hasattr(self, "cursor_"):
            return

        if not self.cursor().metadata():
            return

        tmd_ = self.cursor().metadata()
        if self.sortField_ is None:
            if tmd_ is not None:
                self.sortField_ = tmd_.field(tmd_.primaryKey())

        own_tmd_ = None
        if self.tableName_:
            if DEBUG:
                logger.warning(
                    "**FLTableDB::name: %r tableName: %r", self.objectName(), self.tableName_
                )

            if not self.cursor().db().connManager().manager().existsTable(self.tableName_):
                own_tmd_ = True
                tmd_ = self.cursor().db().connManager().manager().createTable(self.tableName_)
            else:
                own_tmd_ = True
                manager_tmd = self.cursor().db().connManager().manager().metadata(self.tableName_)

                if not manager_tmd or isinstance(manager_tmd, bool):
                    return

                tmd_ = manager_tmd

            if tmd_ is None:
                return

            if not self.foreignField_ or not self.fieldRelation_:
                if not self.cursor().metadata():
                    if own_tmd_ and tmd_ and not tmd_.inCache():
                        del tmd_
                    return

                if not self.cursor().metadata().name() == self.tableName_:
                    ctxt = self.cursor().context()
                    self.cursor_ = pnsqlcursor.PNSqlCursor(
                        self.tableName_, True, self.cursor().db().connectionName(), None, None, self
                    )

                    if self.cursor():
                        self.cursor().setContext(ctxt)
                        self.cursorAux = None

                    if own_tmd_ and tmd_ and not tmd_.inCache():
                        del tmd_

                    return

            else:
                cursorTopWidget = cast(pnsqlcursor.PNSqlCursor, self.topWidget.cursor())
                if cursorTopWidget and cursorTopWidget.metadata().name() != self.tableName_:
                    self.cursor_ = cursorTopWidget

        if (
            not self.tableName_
            or not self.foreignField_
            or not self.fieldRelation_
            or self.cursorAux
        ):
            if own_tmd_ and tmd_ and not tmd_.inCache():
                del tmd_

            return

        self.cursorAux = self.cursor()
        curName = self.cursor().metadata().name()
        rMD = (
            self.cursor()
            .metadata()
            .relation(self.foreignField_, self.fieldRelation_, self.tableName_)
        )
        testM1 = tmd_.relation(self.fieldRelation_, self.foreignField_, curName)
        checkIntegrity = False
        if not rMD:
            if testM1:
                if testM1.cardinality() == pnrelationmetadata.PNRelationMetaData.RELATION_M1:
                    checkIntegrity = True
            fMD = self.cursor().metadata().field(self.foreignField_)
            if fMD is not None:
                tmd_aux_ = self.cursor().db().connManager().manager().metadata(self.tableName_)
                if not tmd_aux_ or tmd_aux_.isQuery():
                    checkIntegrity = False
                if tmd_aux_ and not tmd_aux_.inCache():
                    del tmd_aux_

                rMD = pnrelationmetadata.PNRelationMetaData(
                    self.tableName_,
                    self.fieldRelation_,
                    pnrelationmetadata.PNRelationMetaData.RELATION_1M,
                    False,
                    False,
                    checkIntegrity,
                )
                fMD.addRelationMD(rMD)
                logger.warning(
                    "FLTableDB : La relación entre la tabla del formulario %s y esta tabla %s de este campo no existe, "
                    "pero sin embargo se han indicado los campos de relación( %s, %s )",
                    curName,
                    self.tableName_,
                    self.fieldRelation_,
                    self.foreignField_,
                )
                logger.trace(
                    "FLTableDB : Creando automáticamente %s.%s --1M--> %s.%s",
                    curName,
                    self.foreignField_,
                    self.tableName_,
                    self.fieldRelation_,
                )
            else:
                logger.warning(
                    "FLTableDB : El campo ( %s ) indicado en la propiedad foreignField no se encuentra en la tabla ( %s )",
                    self.foreignField_,
                    curName,
                )
                pass

        rMD = testM1
        if not rMD:
            fMD = tmd_.field(self.fieldRelation_)
            if fMD is not None:
                rMD = pnrelationmetadata.PNRelationMetaData(
                    curName,
                    self.foreignField_,
                    pnrelationmetadata.PNRelationMetaData.RELATION_1M,
                    False,
                    False,
                    False,
                )
                fMD.addRelationMD(rMD)
                if DEBUG:
                    logger.trace(
                        "FLTableDB : Creando automáticamente %s.%s --1M--> %s.%s",
                        self.tableName_,
                        self.fieldRelation_,
                        curName,
                        self.foreignField_,
                    )

            else:
                if DEBUG:
                    logger.warning(
                        "FLTableDB : El campo ( %s ) indicado en la propiedad fieldRelation no se encuentra en la tabla ( %s )",
                        self.fieldRelation_,
                        self.tableName_,
                    )

        self.cursor_ = pnsqlcursor.PNSqlCursor(
            self.tableName_, True, self.cursor().db().connectionName(), self.cursorAux, rMD, self
        )
        if not self.cursor():
            self.cursor_ = self.cursorAux
            self.cursorAux = None

        else:
            self.cursor().setContext(self.cursorAux.context())
            if self.showed:
                try:
                    self.cursorAux.newBuffer.disconnect(self.refresh)
                except Exception:
                    pass

            self.cursorAux.newBuffer.connect(self.refresh)

        # Si hay cursorTopWidget no machaco el cursor de topWidget
        if (
            self.cursorAux
            and isinstance(self.topWidget, flformsearchdb.FLFormSearchDB)
            and not cursorTopWidget
        ):
            self.topWidget.setWindowTitle(self.cursor().metadata().alias())
            self.topWidget.setCursor(self.cursor())

        if own_tmd_ or tmd_ and not tmd_.inCache():
            del tmd_

    def cursor(self) -> "isqlcursor.ISqlCursor":  # type: ignore [override] # noqa F821
        """
        Return the cursor used by the component.

        return pnsqlcursor.PNSqlCursor object with the cursor containing the records to be used in the form
        """
        # if not self.cursor().buffer():
        #    self.cursor().refreshBuffer()
        return self.cursor_

    def tableName(self) -> str:
        """
        Return the name of the associated table.

        @return Name of the associated table
        """
        if not self.tableName_:
            raise Exception("tableName_ is empty!")
        return self.tableName_

    def setTableName(self, fT: str) -> None:
        """
        Set the name of the associated table.

        @param fT Name of the associated table
        """
        self.tableName_ = fT
        if self.topWidget:
            self.initCursor()
        else:
            self.initFakeEditor()

    def foreignField(self) -> Optional[str]:
        """
        Return the name of the foreign field.

        @return Field Name
        """
        return self.foreignField_

    def setForeignField(self, fN: str) -> None:
        """
        Set the name of the foreign field.

        @param fN Field name
        """
        self.foreignField_ = fN
        if self.topWidget:
            self.initCursor()
        else:
            self.initFakeEditor()

    def fieldRelation(self) -> Optional[str]:
        """
        Return the name of the related field.

        @return Field Name
        """
        return self.fieldRelation_

    def setFieldRelation(self, fN: str) -> None:
        """
        To set the name of the related field.

        @param fN Field name
        """
        self.fieldRelation_ = fN
        if self.topWidget:
            self.initCursor()
        else:
            self.initFakeEditor()

    def setReadOnly(self, mode: bool) -> None:
        """
        Set if the component is in read-only mode or not.
        """

        if self.tableRecords_:
            self.readonly_ = mode
            self.tableRecords_.setFLReadOnly(mode)
            self.readOnlyChanged.emit(mode)

        self.reqReadOnly_ = mode

    def readOnly(self) -> bool:
        """Return if the control is in read only mode."""

        return self.reqReadOnly_

    def setEditOnly(self, mode: bool) -> None:
        """
        Set if the component is in edit only mode or not.
        """
        if self.tableRecords_:
            self.editonly_ = mode
            self.tableRecords_.setEditOnly(mode)
            self.editOnlyChanged.emit(mode)

        self.reqEditOnly_ = mode

    def editOnly(self) -> bool:
        """Return if the control is in edit only mode."""
        return self.reqEditOnly_

    def setInsertOnly(self, mode: bool) -> None:
        """
        Set the component to insert only or not.
        """
        if self.tableRecords_:
            self.insertonly_ = mode
            self.tableRecords_.setInsertOnly(mode)
            self.insertOnlyChanged.emit(mode)

        self.reqInsertOnly_ = mode

    def insertOnly(self) -> bool:
        """Return if the control is in insert only mode."""
        return self.reqInsertOnly_

    def setInitSearch(self, iS: str) -> None:
        """
        Set the initial search filter.
        """
        self.initSearch_ = iS

    @decorators.BetaImplementation
    def setOrderCols(self, fields: List[str]):
        """
        Set the order of the columns in the table.

        @param fields List of the names of the fields sorted as you wish them to appear in the table from left to right
        """
        if not self.cursor() or not self.tableRecords_:
            return
        tMD = self.cursor().metadata()
        if not tMD:
            return

        if not self.showed:
            self.showWidget()

        fieldsList = []

        for f in fields:
            fmd = tMD.field(f)
            if fmd is not None:
                if fmd.visibleGrid():
                    fieldsList.append(f)

        hCount = self.cursor().model().columnCount()

        if len(fieldsList) > hCount:
            return

        i = 0
        for fi in fieldsList:
            _index = self.tableRecords_.logical_index_to_visual_index(
                self.tableRecords_.column_name_to_column_index(fi)
            )
            self.moveCol(_index, i)
            i = i + 1

        if not self.lineEditSearch:
            raise Exception("lineEditSearch is not defined!")

        self.setSortOrder(True)
        textSearch = self.lineEditSearch.text()
        self.refresh(True)

        if textSearch:
            self.refresh(False, True)

            try:
                self.lineEditSearch.textChanged.disconnect(self.filterRecords)
            except Exception:
                pass
            self.lineEditSearch.setText(textSearch)
            self.lineEditSearch.textChanged.connect(self.filterRecords)
            self.lineEditSearch.selectAll()
            # self.seekCursor()
            QtCore.QTimer.singleShot(0, self.tableRecords_.ensureRowSelectedVisible)
        else:
            self.refreshDelayed()

    @decorators.BetaImplementation
    def orderCols(self) -> List[str]:
        """
        Return the list of fields sorted by their columns in the table from left to right.
        """
        list_: List[str] = []

        if not self.cursor():
            return list_

        tMD = self.cursor().metadata()
        if not tMD:
            return list_

        if not self.showed:
            self.showWidget()

        model = self.cursor().model()

        if model:
            if not self.tableRecords_:
                raise Exception("tableRecords_ is not defined!")

            for column in range(model.columnCount()):
                alias_ = self.tableRecords_.model().headerData(
                    self.tableRecords_.visual_index_to_logical_index(column),
                    QtCore.Qt.Horizontal,
                    QtCore.Qt.DisplayRole,
                )
                list_.append(tMD.fieldAliasToName(alias_) or "")

        return list_

    def setFilter(self, f: str) -> None:
        """
        Set the table filter.

        @param f Where statement setting the filter
        """
        self.filter_ = f

    def filter(self) -> str:
        """
        Return the table filter.

        @return Filter
        """
        return self.filter_

    def findFilter(self) -> Optional[str]:
        """
        Return the filter of the table imposed in the Find.

        @return Filter
        """
        return self.tdbFilterLastWhere_

    def checkColumnEnabled(self) -> bool:
        """
        Return if the selection column is activated.
        """
        return self.checkColumnEnabled_

    def setCheckColumnEnabled(self, b: bool) -> None:
        """
        Set the activation status of the selection column.

        The change of status will not be effective until the next refresh.
        """
        self.checkColumnEnabled_ = b

    @decorators.BetaImplementation
    def aliasCheckColumn(self) -> Optional[str]:
        """
        Obtain the header label text for the selection column.
        """
        if not self.tableRecords_:
            raise Exception("tableRecords_ is not defined!")

        return self.tableRecords_.model().headerData(
            # self.tableRecords_.selectionModel().selectedColumns(),
            self.tableRecords_.currentColumn(),
            QtCore.Qt.Horizontal,
            QtCore.Qt.DisplayRole,
        )

    def setAliasCheckColumn(self, t: str) -> None:
        """
        Set the text of the header tag for the selection column.

        The change of the label text will not be effective until the next refresh
        """
        self.aliasCheckColumn_ = t

    def findHidden(self) -> bool:
        """
        Get if the search frame is hidden.
        """
        return self.findHidden_

    @decorators.Deprecated
    def setFindHidden(self, h: bool) -> None:
        """
        Hide or show the search frame.

        @param h TRUE hides it, FALSE shows it.
        """
        # if self.findHidden_ is not h:
        #    self.findHidden_ = h
        #    if h:
        #        self.tabControlLayout.hide()
        #    else:
        #        self.tabControlLayout.show()
        pass

    def filterHidden(self) -> bool:
        """
        Return if the frame for switching between data and filter is hidden.
        """
        return self.filterHidden_

    @decorators.Deprecated
    def setFilterHidden(self, h: bool) -> None:
        """
        Hide or show the frame to switch between data and filter.

        @param h TRUE hides it, FALSE shows it
        """
        # if self.filterHidden_ is not h:
        #    self.filterHidden_ = h
        #    if h:
        #        self.tabFilter.hide()
        #    else:
        #        self.tabFilter.show()
        pass

    def showAllPixmaps(self) -> bool:
        """
        Return if images of unselected lines are displayed.
        """
        return self.showAllPixmaps_

    def setShowAllPixmaps(self, s: bool) -> None:
        """
        Set if images of unselected lines are displayed.
        """
        self.showAllPixmaps_ = s

    def functionGetColor(self) -> Optional[str]:
        """
        Return the function that calculates the color of the cell.
        """
        return self.functionGetColor_

    def setFunctionGetColor(self, f: str) -> None:
        """
        Set the function that calculates the color of the cell.
        """
        self.functionGetColor_ = f

        # if self.tableRecords_ is not None:
        #    self.tableRecords().setFunctionGetColor("%s.%s" % (self.topWidget.name(), f))

    def setFilterRecordsFunction(self, fn: str) -> None:
        """
        Assign the function name to call when the filter changes.
        """
        self.tableDB_filterRecords_functionName_ = fn

    def setOnlyTable(self, on: bool = True) -> None:
        """
        Enable table only mode.
        """
        if self.tableRecords_:
            self.onlyTable_ = on
            self.tableRecords_.setOnlyTable(on)

        self.reqOnlyTable_ = on

    def onlyTable(self) -> bool:
        """
        Return if the control is in table only mode.
        """
        return self.reqOnlyTable_

    @decorators.NotImplementedWarn
    def setAutoSortColumn(self, on: bool = True):
        """
        Set auto sort mode.
        """
        self.autoSortColumn_ = on

    def autoSortColumn(self) -> bool:
        """Return if auto sort mode is enabled."""

        return self.autoSortColumn_

    def eventFilter(self, obj: QtCore.QObject, ev: QtCore.QEvent) -> bool:
        """
        Process user events.
        """
        if (
            not self.tableRecords_
            or not self.lineEditSearch
            or not self.comboBoxFieldToSearch
            or not self.comboBoxFieldToSearch2
            or not self.cursor()
        ):
            return super().eventFilter(obj, ev)

        if ev.type() == QtCore.QEvent.KeyPress:
            k = cast(QtGui.QKeyEvent, ev)

            if isinstance(obj, fldatatable.FLDataTable):

                if k.key() == QtCore.Qt.Key_F2:
                    self.comboBoxFieldToSearch.showPopup()
                    return True

            # if ev.type() == QtCore.QEvent.WindowUnblocked and isinstance(obj, fldatatable.FLDataTable):
            #    self.refreshDelayed()
            #    return True

            elif isinstance(obj, QtWidgets.QLineEdit):

                if k.key() == QtCore.Qt.Key_Enter or k.key() == QtCore.Qt.Key_Return:
                    self.tableRecords_.setFocus()
                    return True

                elif k.key() == QtCore.Qt.Key_Up:
                    self.comboBoxFieldToSearch.setFocus()
                    return True

                elif k.key() == QtCore.Qt.Key_Down:
                    self.tableRecords_.setFocus()
                    return True

                elif k.key() == QtCore.Qt.Key_F2:
                    self.comboBoxFieldToSearch.showPopup()
                    return True

                elif k.text() == "'" or k.text() == "\\":
                    return True

        if obj in (self.tableRecords_, self.lineEditSearch):
            return False
        else:
            return super().eventFilter(obj, ev)

    def showEvent(self, e: QtGui.QShowEvent) -> None:
        """
        Proccess show event.
        """
        super().showEvent(e)
        self.load()
        if not self.loaded():
            self.showWidget()

    def showWidget(self) -> None:
        """
        Show the widget.
        """
        if self.showed:
            return

        if not self.topWidget:
            self.initFakeEditor()
            self.showed = True
            return

        if not self.cursor():
            return

        self.showed = True

        # own_tmd = bool(self.tableName_)
        if self.tableName_:
            if not self.cursor().db().connManager().manager().existsTable(self.tableName_):
                tmd = self.cursor().db().connManager().manager().createTable(self.tableName_)
            else:
                tmd = self.cursor().db().connManager().manager().metadata(self.tableName_)

            if not tmd:
                return

        self.tableRecords()

        if not self.cursorAux:
            if not self.initSearch_:
                self.refresh(True, True)
                # if self.tableRecords_:
                #    QtCore.QTimer.singleShot(0, self.tableRecords_.ensureRowSelectedVisible)
            else:
                self.refresh(True)
                if self.tableRecords_ and self.tableRecords_.numRows() <= 0:

                    self.refresh(False, True)
                else:
                    self.refreshDelayed()

            if (
                not isinstance(self.topWidget, flformrecorddb.FLFormRecordDB)
                and self.lineEditSearch is not None
            ):
                self.lineEditSearch.setFocus()

        if self.cursorAux:
            if (
                isinstance(self.topWidget, flformrecorddb.FLFormRecordDB)
                and self.cursorAux.modeAccess() == pnsqlcursor.PNSqlCursor.Browse
            ):
                self.cursor().setEdition(False)
                self.setReadOnly(True)

            if self.initSearch_:
                self.refresh(True, True)
                if self.tableRecords_:
                    QtCore.QTimer.singleShot(0, self.tableRecords_.ensureRowSelectedVisible)
            else:
                self.refresh(True)
                if self.tableRecords_ and self.tableRecords_.numRows() <= 0:
                    self.refresh(False, True)
                else:
                    self.refreshDelayed()

        elif (
            isinstance(self.topWidget, flformrecorddb.FLFormRecordDB)
            and self.cursor().modeAccess() == pnsqlcursor.PNSqlCursor.Browse
            and tmd
            and not tmd.isQuery()
        ):
            self.cursor().setEdition(False)
            self.setReadOnly(True)

        # if own_tmd and tmd and not tmd.inCache():
        #    del tmd

    def createFLTableDBWidget(self) -> None:
        """Create all controls."""

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHeightForWidth(True)

        sizePolicyClean = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicyClean.setHeightForWidth(True)

        sizePolicyGB = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )

        self.dataLayout = QtWidgets.QHBoxLayout()  # Contiene tabData y tabFilters
        # self.dataLayout.setContentsMargins(0, 0, 0, 0)
        # self.dataLayout.setSizeConstraint(0)

        self.tabDataLayout = QtWidgets.QVBoxLayout()
        filterL = QtWidgets.QVBoxLayout()
        filterL.setSpacing(2)
        filterL.setContentsMargins(1, 2, 1, 2)
        if self.tabData:
            self.tabData.setSizePolicy(sizePolicyGB)
            self.tabData.setLayout(self.tabDataLayout)

        if self.tabFilter:
            self.tabFilter.setSizePolicy(sizePolicyGB)
            self.tabFilter.setLayout(filterL)

        # Fix para acercar el lineEdit con el fltable
        # self.tabData.setContentsMargins(0, 0, 0, 0)
        # self.tabFilter.setContentsMargins(0, 0, 0, 0)
        self.tabDataLayout.setContentsMargins(0, 0, 0, 0)
        # filterL.setContentsMargins(0, 0, 0, 0)

        # Contiene botones lateral (datos, filtros, odf)
        self.buttonsLayout = QtWidgets.QVBoxLayout()
        self.masterLayout = QtWidgets.QVBoxLayout()  # Contiene todos los layouts

        self.pbData = QtWidgets.QPushButton(self)
        self.pbData.setSizePolicy(sizePolicy)
        if self.iconSize is not None:
            self.pbData.setMinimumSize(self.iconSize)
        self.pbData.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pbData.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "fltable-data.png"))
        )
        self.pbData.setText("")
        self.pbData.setToolTip("Mostrar registros")
        self.pbData.setWhatsThis("Mostrar registros")
        self.buttonsLayout.addWidget(self.pbData)
        self.pbData.clicked.connect(self.activeTabData)

        self.pbFilter = QtWidgets.QPushButton(self)
        self.pbFilter.setSizePolicy(sizePolicy)
        if self.iconSize is not None:
            self.pbFilter.setMinimumSize(self.iconSize)
        self.pbFilter.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pbFilter.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "fltable-filter.png"))
        )
        self.pbFilter.setText("")
        self.pbFilter.setToolTip("Mostrar filtros")
        self.pbFilter.setWhatsThis("Mostrar filtros")
        self.buttonsLayout.addWidget(self.pbFilter)
        self.pbFilter.clicked.connect(self.activeTabFilter)

        self.pbOdf = QtWidgets.QPushButton(self)
        self.pbOdf.setSizePolicy(sizePolicy)
        if self.iconSize is not None:
            self.pbOdf.setMinimumSize(self.iconSize)
        self.pbOdf.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pbOdf.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "fltable-odf.png"))
        )
        self.pbOdf.setText("")
        self.pbOdf.setToolTip("Exportar a hoja de cálculo")
        self.pbOdf.setWhatsThis("Exportar a hoja de cálculo")
        self.buttonsLayout.addWidget(self.pbOdf)
        self.pbOdf.clicked.connect(self.exportToOds)
        if settings.config.value("ebcomportamiento/FLTableExport2Calc", "false") == "true":
            self.pbOdf.setDisabled(True)

        self.pbClean = QtWidgets.QPushButton(self)
        self.pbClean.setSizePolicy(sizePolicyClean)
        if self.iconSize is not None:
            self.pbClean.setMinimumSize(self.iconSize)
        self.pbClean.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pbClean.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "fltable-clean.png"))
        )
        self.pbClean.setText("")
        self.pbClean.setToolTip("Limpiar filtros")
        self.pbClean.setWhatsThis("Limpiar filtros")
        filterL.addWidget(self.pbClean)
        self.pbClean.clicked.connect(self.tdbFilterClear)

        spacer = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.buttonsLayout.addItem(spacer)

        self.comboBoxFieldToSearch = QtWidgets.QComboBox()
        self.comboBoxFieldToSearch2 = QtWidgets.QComboBox()
        # self.comboBoxFieldToSearch.addItem("*")
        # self.comboBoxFieldToSearch2.addItem("*")
        self.lineEditSearch = QtWidgets.QLineEdit()
        self.lineEditSearch.textChanged.connect(self.filterRecords)
        label1 = QtWidgets.QLabel()
        label2 = QtWidgets.QLabel()
        label1.setStyleSheet("border: 0px")
        label2.setStyleSheet("border: 0px")

        label1.setText("Buscar")
        label2.setText("en")

        if self.tabControlLayout is not None:
            control_frame = QtWidgets.QFrame()
            lay = QtWidgets.QHBoxLayout()
            control_frame.setFrameStyle(QtWidgets.QFrame.Raised)
            control_frame.setStyleSheet("QFrame { border: 1px solid black; }")
            lay.setContentsMargins(2, 2, 2, 2)
            lay.setSpacing(2)
            lay.addWidget(label1)
            lay.addWidget(self.lineEditSearch)
            lay.addWidget(label2)
            lay.addWidget(self.comboBoxFieldToSearch)
            lay.addWidget(self.comboBoxFieldToSearch2)
            control_frame.setLayout(lay)

            self.tabControlLayout.addWidget(control_frame)
            self.masterLayout.addLayout(self.tabControlLayout)

        self.masterLayout.addLayout(self.dataLayout)
        self.masterLayout.setSpacing(2)
        self.masterLayout.setContentsMargins(1, 2, 1, 2)
        self.setLayout(self.masterLayout)

        # Se añade data, filtros y botonera
        if self.tabData is not None:
            self.dataLayout.addWidget(self.tabData)
        if self.tabFilter is not None:
            self.dataLayout.addWidget(self.tabFilter)
            self.tabFilter.hide()

        self.dataLayout.addLayout(self.buttonsLayout)
        self.comboBoxFieldToSearch.currentIndexChanged.connect(self.putFirstCol)
        self.comboBoxFieldToSearch2.currentIndexChanged.connect(self.putSecondCol)

        self.tdbFilter = qtable.QTable()

        filterL.addWidget(self.tdbFilter)

    def tableRecords(self) -> fldatatable.FLDataTable:
        """
        Obtiene el componente tabla de registros.
        """
        if self.tableRecords_ is None:
            self.tableRecords_ = fldatatable.FLDataTable(self.tabData, "tableRecords")
            if self.tableRecords_ is not None:
                self.tableRecords_.setFocusPolicy(QtCore.Qt.StrongFocus)
                self.setFocusProxy(self.tableRecords_)
                if self.tabDataLayout is not None:
                    self.tabDataLayout.addWidget(self.tableRecords_)
                self.setTabOrder(self.tableRecords_, self.lineEditSearch)
                self.setTabOrder(self.lineEditSearch, self.comboBoxFieldToSearch)
                self.setTabOrder(self.comboBoxFieldToSearch, self.comboBoxFieldToSearch2)
                if self.lineEditSearch is not None:
                    self.lineEditSearch.installEventFilter(self)
                self.tableRecords_.installEventFilter(self)

                if self.autoSortColumn_:
                    self.tableRecords_.header().sectionClicked.connect(self.switchSortOrder)

        t_cursor = self.tableRecords_.cursor_
        if (
            self.cursor()
            and self.cursor() is not t_cursor
            and self.cursor().metadata()
            and (
                not t_cursor
                or (
                    t_cursor
                    and t_cursor.metadata()
                    and t_cursor.metadata().name() != self.cursor().metadata().name()
                )
            )
        ):
            self.setTableRecordsCursor()

        return self.tableRecords_

    def setTableRecordsCursor(self) -> None:
        """
        Assign the current cursor of the component to the record table.
        """

        if self.tableRecords_ is None:
            self.tableRecords_ = fldatatable.FLDataTable(self.tabData, "tableRecords")
            if self.tableRecords_ is not None:
                self.tableRecords_.setFocusPolicy(QtCore.Qt.StrongFocus)
                self.setFocusProxy(self.tableRecords_)
                if self.tabDataLayout is not None:
                    self.tabDataLayout.addWidget(self.tableRecords_)
                self.setTabOrder(self.tableRecords_, self.lineEditSearch)
                self.setTabOrder(self.lineEditSearch, self.comboBoxFieldToSearch)
                self.setTabOrder(self.comboBoxFieldToSearch, self.comboBoxFieldToSearch2)
                self.tableRecords_.installEventFilter(self)

                if self.lineEditSearch is not None:
                    self.lineEditSearch.installEventFilter(self)

        if self.checkColumnEnabled_:
            try:
                self.tableRecords_.clicked.disconnect(self.tableRecords_.setChecked)
            except Exception:
                logger.exception("setTableRecordsCursor: Error disconnecting setChecked signal")
            self.tableRecords_.clicked.connect(self.tableRecords_.setChecked)

        t_cursor = self.tableRecords_.cursor_
        if t_cursor is not self.cursor():
            self.tableRecords_.setFLSqlCursor(self.cursor())
            if t_cursor:
                self.tableRecords_.recordChoosed.disconnect(self.recordChoosedSlot)
                t_cursor.newBuffer.disconnect(self.currentChangedSlot)

            self.tableRecords_.recordChoosed.connect(self.recordChoosedSlot)
            self.cursor().newBuffer.connect(self.currentChangedSlot)

    @decorators.pyqtSlot()
    def recordChoosedSlot(self) -> None:
        """Perform operations when selecting a record."""
        if isinstance(self.topWidget, flformsearchdb.FLFormSearchDB) and self.topWidget.inExec_:
            self.topWidget.accept()
        else:
            self.cursor().chooseRecord()

    @decorators.pyqtSlot()
    def currentChangedSlot(self) -> None:
        """Emit current changed signal."""
        self.currentChanged.emit()

    def currentRow(self) -> int:
        """Return current row index."""

        return self.cursor().at()

    def refreshTabData(self) -> None:
        """
        Refresh the data tab by applying the filter.
        """
        if self.filter_ is not None and self.tdbFilterLastWhere_ is not None:
            self.filter_ = self.filter_.replace(self.tdbFilterLastWhere_, "")

        tdbWhere: Optional[str] = self.tdbFilterBuildWhere()
        # if not tdbWhere == self.tdbFilterLastWhere_:
        self.tdbFilterLastWhere_ = tdbWhere

        self.refresh(False, True)

    def refreshTabFilter(self) -> None:
        """
        Refresh the filter tab.
        """
        if self.tabFilterLoaded:
            return

        horizHeader = self.tableRecords().horizontalHeader()
        if not horizHeader:
            return

        hCount = horizHeader.count() - self.sortColumn_
        if self.tdbFilter and self.cursor():
            tMD = self.cursor().metadata()
            if tMD is None:
                return

            field = None
            # type = None
            # len = None
            partInteger = None
            partDecimal = None
            rX = None
            ol = None

            self.tdbFilter.setSelectionMode(QtWidgets.QTableWidget.NoSelection)
            self.tdbFilter.setNumCols(5)

            _notVisibles = 0
            for f in tMD.fieldList():
                if not f.visibleGrid():
                    _notVisibles = _notVisibles + 1

            self.tdbFilter.setNumRows(hCount - _notVisibles)
            self.tdbFilter.setColumnReadOnly(0, True)
            util = flutil.FLUtil()
            self.tdbFilter.setColumnLabels(",", self.tr("Campo,Condición,Valor,Desde,Hasta"))

            self.mapCondType.insert(self.All, self.tr("Todos"))
            self.mapCondType.insert(self.Contains, self.tr("Contiene Valor"))
            self.mapCondType.insert(self.Starts, self.tr("Empieza por Valor"))
            self.mapCondType.insert(self.End, self.tr("Acaba por Valor"))
            self.mapCondType.insert(self.Equal, self.tr("Igual a Valor"))
            self.mapCondType.insert(self.Dist, self.tr("Distinto de Valor"))
            self.mapCondType.insert(self.Greater, self.tr("Mayor que Valor"))
            self.mapCondType.insert(self.Less, self.tr("Menor que Valor"))
            self.mapCondType.insert(self.FromTo, self.tr("Desde - Hasta"))
            self.mapCondType.insert(self.Null, self.tr("Vacío"))
            self.mapCondType.insert(self.NotNull, self.tr("No Vacío"))
            i = 0
            # for headT in hCount:
            _linea = 0

            while i < hCount:
                _label = (
                    self.cursor()
                    .model()
                    .headerData(i + self.sortColumn_, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
                )
                _alias = tMD.fieldAliasToName(_label)
                if _alias is None:
                    i = i + 1
                    continue

                field = tMD.field(_alias)

                if field is None:
                    i = i + 1
                    continue

                if not field.visibleGrid():
                    i = i + 1
                    continue

                self.tdbFilter.setText(_linea, 0, _label)

                type_ = field.type()
                len_ = field.length()
                partInteger = field.partInteger()
                partDecimal = field.partDecimal()
                rX = field.regExpValidator()
                ol = field.hasOptionsList()

                cond = QtWidgets.QComboBox(self)
                if not type_ == "pixmap":
                    condList = [
                        self.tr("Todos"),
                        self.tr("Igual a Valor"),
                        self.tr("Distinto de Valor"),
                        self.tr("Vacío"),
                        self.tr("No Vacío"),
                    ]
                    if not type_ == "bool":
                        condList = [
                            self.tr("Todos"),
                            self.tr("Igual a Valor"),
                            self.tr("Distinto de Valor"),
                            self.tr("Vacío"),
                            self.tr("No Vacío"),
                            self.tr("Contiene Valor"),
                            self.tr("Empieza por Valor"),
                            self.tr("Acaba por Valor"),
                            self.tr("Mayor que Valor"),
                            self.tr("Menor que Valor"),
                            self.tr("Desde - Hasta"),
                        ]
                    cond.insertItems(len(condList), condList)
                    self.tdbFilter.setCellWidget(_linea, 1, cond)

                j = 2
                while j < 5:
                    if type_ in ("uint", "int", "double", "string", "stringlist", "timestamp"):
                        if ol:
                            editor_qcb = QtWidgets.QComboBox(self)
                            olTranslated = []
                            olNoTranslated = field.optionsList()
                            for z in olNoTranslated:
                                olTranslated.append(util.translate("Metadata", z))

                            editor_qcb.insertItems(len(olTranslated), olTranslated)

                            self.tdbFilter.setCellWidget(_linea, j, editor_qcb)
                        else:

                            editor_le = QtWidgets.QLineEdit(self)
                            if type_ == "double":

                                editor_le.setValidator(
                                    fldoublevalidator.FLDoubleValidator(
                                        0, pow(10, partInteger) - 1, partDecimal, editor_le
                                    )
                                )
                                editor_le.setAlignment(QtCore.Qt.AlignRight)
                            elif type_ in ("uint", "int"):
                                if type_ == "uint":

                                    editor_le.setValidator(
                                        fluintvalidator.FLUIntValidator(
                                            0, pow(10, partInteger) - 1, editor_le
                                        )
                                    )
                                else:

                                    editor_le.setValidator(
                                        flintvalidator.FLIntValidator(
                                            pow(10, partInteger) - 1 * (-1),
                                            pow(10, partInteger) - 1,
                                            editor_le,
                                        )
                                    )

                                editor_le.setAlignment(QtCore.Qt.AlignRight)
                            else:  # string, stringlist, timestamp
                                if len_ > 0:
                                    editor_le.setMaxLength(len_)
                                    if rX:
                                        editor_le.setValidator(
                                            QtGui.QRegExpValidator(QtCore.QRegExp(rX), editor_le)
                                        )

                                editor_le.setAlignment(QtCore.Qt.AlignLeft)

                            self.tdbFilter.setCellWidget(_linea, j, editor_le)

                    elif type_ == "serial":

                        editor_se = flspinbox.FLSpinBox()
                        editor_se.setMaxValue(pow(10, partInteger) - 1)
                        self.tdbFilter.setCellWidget(_linea, j, editor_se)

                    elif type_ == "pixmap":

                        editor_px = QtWidgets.QLineEdit(self)
                        self.tdbFilter.setRowReadOnly(i, True)
                        self.tdbFilter.setCellWidget(_linea, j, editor_px)

                    elif type_ == "date":

                        editor_de = fldateedit.FLDateEdit(self, _label)
                        editor_de.setOrder(fldateedit.FLDateEdit.DMY)
                        editor_de.setAutoAdvance(True)
                        editor_de.setCalendarPopup(True)
                        editor_de.setSeparator("-")
                        da = QtCore.QDate()
                        editor_de.setDate(da.currentDate())
                        self.tdbFilter.setCellWidget(_linea, j, editor_de)

                    elif type_ == "time":

                        editor_te = fltimeedit.FLTimeEdit(self)
                        timeNow = QtCore.QTime.currentTime()
                        editor_te.setTime(timeNow)
                        self.tdbFilter.setCellWidget(_linea, j, editor_te)

                    elif type_ in (pnfieldmetadata.PNFieldMetaData.Unlock, "bool"):

                        editor_cb = flcheckbox.FLCheckBox(self)
                        self.tdbFilter.setCellWidget(_linea, j, editor_cb)

                    j += 1

                i += 1
                _linea += 1

        k = 0

        while k < 5:
            if self.tdbFilter:
                self.tdbFilter.adjustColumn(k)
            k += 1

        self.tabFilterLoaded = True  # Con esto no volvemos a cargar y reescribir el filtro

    def decodeCondType(self, strCondType: str) -> int:
        """
        Obtain the enumeration corresponding to a condition for the filter from its literal.
        """
        i = 0
        while i < len(self.mapCondType):
            if strCondType == self.mapCondType[i]:
                return i

            i = i + 1

        return self.All

    def tdbFilterBuildWhere(self) -> Optional[str]:
        """
        Build the filter clause in SQL from the contents of the values defined in the filter tab.
        """
        if not self.topWidget:
            return None

        if self.tdbFilter is None:
            return None

        rCount = self.tdbFilter.numRows()
        # rCount = self.cursor().model().columnCount()
        if not rCount or not self.cursor():
            return None

        tMD = self.cursor().metadata()
        if not tMD:
            return None

        field = None
        cond = None
        type = None
        condType = None
        fieldName = None
        condValue: str = ""
        where: str = ""
        fieldArg = ""
        arg2 = ""
        arg4 = ""

        ol = None

        for i in range(rCount):
            if self.tdbFilter is None:
                break
            fieldName = tMD.fieldAliasToName(self.tdbFilter.text(i, 0))
            if fieldName is None:
                raise Exception("fieldName could not be resolved!")

            field = tMD.field(fieldName)
            if field is None:
                continue

            cond = self.tdbFilter.cellWidget(i, 1)
            if cond is None:
                continue

            condType = self.decodeCondType(cond.currentText())
            if condType == self.All:
                continue

            if tMD.isQuery():
                qry = (
                    self.cursor()
                    .db()
                    .connManager()
                    .manager()
                    .query(self.cursor().metadata().query(), self.cursor())
                )

                if qry:
                    list_ = qry.fieldList()

                    qField = None
                    for qField in list_:
                        if qField.endswith(".%s" % fieldName):
                            break

                    fieldName = qField
            else:
                fieldName = tMD.name() + "." + fieldName

            fieldArg = fieldName or ""
            arg2 = ""
            arg4 = ""
            type = field.type()
            ol = field.hasOptionsList()

            if type in ("string", "stringlist", "timestamp"):
                fieldArg = "UPPER(%s)" % fieldName

            if type in ("uint", "int", "double", "string", "stringlist", "timestamp"):
                if ol:
                    if condType == self.FromTo:
                        editorOp1 = self.tdbFilter.cellWidget(i, 3)
                        editorOp2 = self.tdbFilter.cellWidget(i, 4)
                        arg2 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type, editorOp1.currentText, True)
                        )
                        arg4 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type, editorOp2.currentText, True)
                        )
                    else:
                        editorOp1 = self.tdbFilter.cellWidget(i, 2)
                        arg2 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type, editorOp1.currentText, True)
                        )
                else:
                    if condType == self.FromTo:
                        editorOp1 = self.tdbFilter.cellWidget(i, 3)
                        editorOp2 = self.tdbFilter.cellWidget(i, 4)
                        arg2 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type, editorOp1.text(), True)
                        )
                        arg4 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type, editorOp2.text(), True)
                        )
                    else:
                        editorOp1 = self.tdbFilter.cellWidget(i, 2)
                        arg2 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type, editorOp1.text(), True)
                        )

            if type == "serial":
                if condType == self.FromTo:
                    editorOp1 = self.tdbFilter.cellWidget(i, 3)
                    editorOp2 = self.tdbFilter.cellWidget(i, 4)
                    arg2 = editorOp1.value()
                    arg4 = editorOp2.value()
                else:

                    editorOp1 = flspinbox.FLSpinBox(self.tdbFilter.cellWidget(i, 2))
                    arg2 = editorOp1.value()

            if type == "date":
                util = flutil.FLUtil()
                if condType == self.FromTo:
                    editorOp1 = self.tdbFilter.cellWidget(i, 3)
                    editorOp2 = self.tdbFilter.cellWidget(i, 4)
                    arg2 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(type, util.dateDMAtoAMD(str(editorOp1.text())))
                    )
                    arg4 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(type, util.dateDMAtoAMD(str(editorOp2.text())))
                    )
                else:
                    editorOp1 = self.tdbFilter.cellWidget(i, 2)
                    arg2 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(type, util.dateDMAtoAMD(str(editorOp1.text())))
                    )

            if type == "time":
                if condType == self.FromTo:
                    editorOp1 = self.tdbFilter.cellWidget(i, 3)
                    editorOp2 = self.tdbFilter.cellWidget(i, 4)
                    arg2 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(type, editorOp1.time().toString(QtCore.Qt.ISODate))
                    )
                    arg4 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(type, editorOp2.time().toString(QtCore.Qt.ISODate))
                    )
                else:
                    editorOp1 = self.tdbFilter.cellWidget(i, 2)
                    arg2 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(type, editorOp1.time().toString(QtCore.Qt.ISODate))
                    )

            if type in ("unlock", "bool"):
                editorOp1 = self.tdbFilter.cellWidget(i, 2)
                checked_ = False
                if editorOp1.isChecked():
                    checked_ = True
                arg2 = self.cursor().db().connManager().manager().formatValue(type, checked_)

            if where:
                where += " AND"

            condValue = " " + fieldArg
            if arg2 is None:
                arg2 = ""
            if condType == self.Contains:
                condValue += " LIKE '%" + arg2.replace("'", "") + "%'"
            elif condType == self.Starts:
                condValue += " LIKE '" + arg2.replace("'", "") + "%'"
            elif condType == self.End:
                condValue += " LIKE '%%" + arg2.replace("'", "") + "'"
            elif condType == self.Equal:
                condValue += " = " + str(arg2)
            elif condType == self.Dist:
                condValue += " <> " + str(arg2)
            elif condType == self.Greater:
                condValue += " > " + str(arg2)
            elif condType == self.Less:
                condValue += " < " + str(arg2)
            elif condType == self.FromTo:
                condValue += " >= " + str(arg2) + " AND " + fieldArg + " <= " + str(arg4)
            elif condType == self.Null:
                condValue += " IS NULL "
            elif condType == self.NotNull:
                condValue += " IS NOT NULL "

            where += condValue

        return where

    @decorators.BetaImplementation
    def initFakeEditor(self) -> None:
        """
        Initialize a false and non-functional editor.

        This is used when the form is being edited with the designer and not
        You can display the actual editor for not having a connection to the database.
        Create a very schematic preview of the editor, but enough to
        See the position and approximate size of the actual editor.
        """
        if not self.fakeEditor_:
            self.fakeEditor_ = QtWidgets.QTextEdit(self.tabData)

            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
            )
            sizePolicy.setHeightForWidth(True)

            self.fakeEditor_.setSizePolicy(sizePolicy)
            self.fakeEditor_.setTabChangesFocus(True)
            self.fakeEditor_.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.setFocusProxy(self.fakeEditor_)
            if not self.tabDataLayout:
                raise Exception("self.tabDataLayout is not defined!")
            self.tabDataLayout.addWidget(self.fakeEditor_)
            self.setTabOrder(self.fakeEditor_, self.lineEditSearch)
            self.setTabOrder(self.fakeEditor_, self.comboBoxFieldToSearch)
            self.fakeEditor_.show()

            prty = ""
            if self.tableName_:
                prty = prty + "tableName: %s\n" % self.tableName_
            if self.foreignField_:
                prty = prty + "foreignField: %s\n" % self.foreignField_
            if self.fieldRelation_:
                prty = prty + "fieldRelation: %s\n" % self.fieldRelation_

            self.fakeEditor_.setText(prty)

    @decorators.pyqtSlot()
    @decorators.pyqtSlot(bool)
    @decorators.pyqtSlot(bool, bool)
    def refresh(self, *args) -> None:
        """
        Update the recordset.
        """
        refreshHead: bool = False
        refreshData: bool = True

        if len(args) == 1:
            if isinstance(args[0], list):
                refreshHead = args[0][0]
                refreshData = args[0][1]
            else:
                refreshHead = args[0]

        elif len(args) == 2:
            refreshHead = args[0]
            refreshData = args[1]

        if not self.cursor() or not self.tableRecords_:
            return

        tMD = self.cursor().metadata()
        if not tMD:
            return
        if not self.tableName_:
            self.tableName_ = tMD.name()

        if self.checkColumnEnabled_:
            if not self.checkColumnVisible_:
                fieldCheck = tMD.field(self.fieldNameCheckColumn_)
                if fieldCheck is None:
                    self.fieldNameCheckColumn_ = "%s_check_column" % tMD.name()

                    if self.fieldNameCheckColumn_ not in tMD.fieldNames():
                        fieldCheck = pnfieldmetadata.PNFieldMetaData(
                            self.fieldNameCheckColumn_,
                            self.tr(self.aliasCheckColumn_),
                            True,
                            False,
                            pnfieldmetadata.PNFieldMetaData.Check,
                            0,
                            False,
                            True,
                            True,
                            0,
                            0,
                            False,
                            False,
                            False,
                            None,
                            False,
                            None,
                            True,
                            False,
                            False,
                        )
                        tMD.addFieldMD(fieldCheck)
                    else:
                        fieldCheck = tMD.field(self.fieldNameCheckColumn_)

                if fieldCheck is None:
                    raise Exception("fieldCheck is empty!")

                self.tableRecords().cur.model().updateColumnsCount()
                self.tableRecords().header().reset()
                self.tableRecords().header().swapSections(
                    self.tableRecords().column_name_to_column_index(fieldCheck.name()),
                    self.sortColumn_,
                )
                self.checkColumnVisible_ = True
                self.setTableRecordsCursor()
                self.sortColumn_ = 1
                self.sortColumn2_ = 2
                self.sortColumn3_ = 3

                # for i in enumerate(buffer_.count()):
                #    buffer_.setGenerated(i, True)

        else:
            self.setTableRecordsCursor()
            self.sortColumn_ = 0
            self.sortColumn2_ = 1
            self.sortColumn3_ = 2
            self.checkColumnVisible_ = False

        self.tableRecords_.setFunctionGetColor(
            self.functionGetColor(), getattr(self.topWidget, "iface", None)
        )

        if refreshHead:
            if not self.tableRecords().header().isHidden():
                self.tableRecords().header().hide()

            model = self.cursor().model()
            for column in range(model.columnCount()):
                field = model.metadata().indexFieldObject(column)
                if not field.visibleGrid() or (
                    field.type() == "check" and not self.checkColumnEnabled_
                ):
                    self.tableRecords_.setColumnHidden(column, True)
                else:
                    self.tableRecords_.setColumnHidden(column, False)

            if self.autoSortColumn_:
                s = []
                field_1 = self.tableRecords_.visual_index_to_field(self.sortColumn_)
                field_2 = self.tableRecords_.visual_index_to_field(self.sortColumn2_)
                field_3 = self.tableRecords_.visual_index_to_field(self.sortColumn3_)
                if field_1:
                    s.append("%s %s" % (field_1.name(), "ASC" if self.orderAsc_ else "DESC"))
                if field_2:
                    s.append("%s %s" % (field_2.name(), "ASC" if self.orderAsc_ else "DESC"))
                if field_3:
                    s.append("%s %s" % (field_3.name(), "ASC" if self.orderAsc_ else "DESC"))

                id_mod = (
                    self.cursor()
                    .db()
                    .connManager()
                    .managerModules()
                    .idModuleOfFile("%s.mtd" % self.cursor().metadata().name())
                )
                function_qsa = "%s.tableDB_setSort_%s" % (id_mod, self.cursor().metadata().name())

                vars: List[Any] = []
                vars.append(s)
                if field_1:
                    vars.append(field_1.name())
                    vars.append(self.orderAsc_)
                if field_2:
                    vars.append(field_2.name())
                    vars.append(self.orderAsc2_)
                if field_3:
                    vars.append(field_3.name())
                    vars.append(self.orderAsc3_)

                ret = application.PROJECT.call(function_qsa, vars, None, False)
                logger.debug("functionQSA: %s -> %r" % (function_qsa, ret))
                if ret and not isinstance(ret, bool):
                    if isinstance(ret, str):
                        ret = [ret]
                    if isinstance(ret, list):
                        s = ret

                self.tableRecords_.setSort(", ".join(s))

            if model:
                if self.comboBoxFieldToSearch is None:
                    raise Exception("comboBoxFieldSearch is not defined!")

                if self.comboBoxFieldToSearch2 is None:
                    raise Exception("comboBoxFieldSearch2 is not defined!")

                try:
                    self.comboBoxFieldToSearch.currentIndexChanged.disconnect(self.putFirstCol)
                    self.comboBoxFieldToSearch2.currentIndexChanged.disconnect(self.putSecondCol)
                except Exception:
                    logger.error("Se ha producido un problema al desconectar")
                    return

                self.comboBoxFieldToSearch.clear()
                self.comboBoxFieldToSearch2.clear()

                # cb1 = None
                # cb2 = None
                for column in range(model.columnCount()):
                    visual_column = self.tableRecords_.header().logicalIndex(column)
                    if visual_column is not None:
                        field = model.metadata().indexFieldObject(visual_column)
                        if not field.visibleGrid():
                            continue
                        #    self.tableRecords_.setColumnHidden(column, True)
                        # else:
                        self.comboBoxFieldToSearch.addItem(
                            model.headerData(
                                visual_column, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole
                            )
                        )
                        self.comboBoxFieldToSearch2.addItem(
                            model.headerData(
                                visual_column, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole
                            )
                        )

                self.comboBoxFieldToSearch.addItem("*")
                self.comboBoxFieldToSearch2.addItem("*")
                self.comboBoxFieldToSearch.setCurrentIndex(self.sortColumn_)
                self.comboBoxFieldToSearch2.setCurrentIndex(self.sortColumn2_)
                self.comboBoxFieldToSearch.currentIndexChanged.connect(self.putFirstCol)
                self.comboBoxFieldToSearch2.currentIndexChanged.connect(self.putSecondCol)

            else:
                self.comboBoxFieldToSearch.addItem("*")
                self.comboBoxFieldToSearch2.addItem("*")

            self.tableRecords_.header().show()

        if refreshData or self.sender():
            finalFilter = self.filter_
            if self.tdbFilterLastWhere_:
                if not finalFilter:
                    finalFilter = self.tdbFilterLastWhere_
                else:
                    finalFilter = "%s AND %s" % (finalFilter, self.tdbFilterLastWhere_)

            self.tableRecords_.setPersistentFilter(finalFilter)
            self.tableRecords_.setShowAllPixmaps(self.showAllPixmaps_)
            self.tableRecords_.refresh()

        if self.initSearch_:
            try:
                self.lineEditSearch.textChanged.disconnect(self.filterRecords)
            except Exception:
                pass
            self.lineEditSearch.setText(self.initSearch_)
            self.lineEditSearch.textChanged.connect(self.filterRecords)
            self.lineEditSearch.selectAll()
            self.initSearch_ = None
            # self.seekCursor()

        if not self.readonly_ == self.reqReadOnly_ or (
            self.tableRecords_ and not self.readonly_ == self.tableRecords_.flReadOnly()
        ):
            self.setReadOnly(self.reqReadOnly_)

        if not self.editonly_ == self.reqEditOnly_ or (
            self.tableRecords_ and not self.editonly_ == self.tableRecords_.editOnly()
        ):
            self.setEditOnly(self.reqEditOnly_)

        if not self.insertonly_ == self.reqInsertOnly_ or (
            self.tableRecords_ and not self.insertonly_ == self.tableRecords_.insertOnly()
        ):
            self.setInsertOnly(self.reqInsertOnly_)

        if not self.onlyTable_ == self.reqOnlyTable_ or (
            self.tableRecords_ and not self.onlyTable_ == self.tableRecords_.onlyTable()
        ):
            self.setOnlyTable(self.reqOnlyTable_)

        if self.tableRecords_ and self.tableRecords_.isHidden():
            self.tableRecords_.show()

        # QtCore.QTimer.singleShot(50, self.setSortOrder)

    def refreshDelayed(self, msec: int = 5, refreshData: bool = True) -> None:
        """
        Update the recordset with a delay.

        Accept a lapse of time in milliseconds, activating the internal timer for
        to perform the final refresh upon completion of said lapse.

        @param msec Amount of lapsus time, in milliseconds.
        """

        self._refreshData = True if refreshData else False
        QtCore.QTimer.singleShot(msec, self.refreshDelayed2)
        # self.seekCursor()

    def refreshDelayed2(self) -> None:
        """Refresh the data when the time ends."""
        row = self.currentRow()
        self.refresh(False, self._refreshData)
        self._refreshData = False
        if row > -1:
            self.setCurrentRow(row)

    @decorators.pyqtSlot(bool)
    def insertRecord(self, wait: bool = True) -> None:
        """Call method FLSqlCursor.insertRecord."""

        w = cast(QtWidgets.QWidget, self.sender())
        # if (w and (not self.cursor() or self.reqReadOnly_ or self.reqEditOnly_ or self.reqOnlyTable_ or (self.cursor().cursorRelation()
        #      and self.cursor().cursorRelation().isLocked()))):
        relationLock = False
        cur_relation = self.cursor().cursorRelation()
        if cur_relation is not None:
            relationLock = cur_relation.isLocked()

        if w and (
            not self.cursor()
            or self.reqReadOnly_
            or self.reqEditOnly_
            or self.reqOnlyTable_
            or relationLock
        ):
            w.setDisabled(True)
            return

        if self.cursor():
            self.cursor().insertRecord(wait)

    @decorators.pyqtSlot(bool)
    def editRecord(self, wait: bool = True) -> None:
        """
        Call method FLSqlCursor.editRecord.
        """
        w = cast(QtWidgets.QWidget, self.sender())
        cur_relation = self.cursor().cursorRelation()

        if (
            w
            and not isinstance(w, fldatatable.FLDataTable)
            and (
                not self.cursor()
                or self.reqReadOnly_
                or self.reqEditOnly_
                or self.reqOnlyTable_
                or (cur_relation and cur_relation.isLocked())
            )
        ):
            w.setDisabled(True)
            return

        if self.cursor():
            self.cursor().editRecord()

    @decorators.pyqtSlot(bool)
    def browseRecord(self, wait: bool = True) -> None:
        """
        Call method FLSqlCursor.browseRecord.
        """

        w = cast(QtWidgets.QWidget, self.sender())

        if (
            w
            and not isinstance(w, fldatatable.FLDataTable)
            and (not self.cursor() or self.reqOnlyTable_)
        ):
            w.setDisabled(True)
            return

        if self.cursor():
            self.cursor().browseRecord(wait)

    @decorators.pyqtSlot(bool)
    def deleteRecord(self, wait: bool = True) -> None:
        """
        Call method FLSqlCursor.deleteRecord.
        """
        w = cast(QtWidgets.QWidget, self.sender())

        cur_relation = self.cursor().cursorRelation()

        if (
            w
            and not isinstance(w, fldatatable.FLDataTable)
            and (
                not self.cursor()
                or self.reqReadOnly_
                or self.reqInsertOnly_
                or self.reqEditOnly_
                or self.reqOnlyTable_
                or (cur_relation and cur_relation.isLocked())
            )
        ):
            w.setDisabled(True)
            return

        if self.cursor():
            self.cursor().deleteRecord(wait)

    @decorators.pyqtSlot()
    def copyRecord(self):
        """
        Call method FLSqlCursor.copyRecord.
        """
        w = cast(QtWidgets.QWidget, self.sender())

        cur_relation = self.cursor().cursorRelation()

        if (
            w
            and not isinstance(w, fldatatable.FLDataTable)
            and (
                not self.cursor()
                or self.reqReadOnly_
                or self.reqEditOnly_
                or self.reqOnlyTable_
                or (cur_relation and cur_relation.isLocked())
            )
        ):
            w.setDisabled(True)
            return

        if self.cursor():
            self.cursor().copyRecord()

    @decorators.pyqtSlot(int)
    @decorators.pyqtSlot(str)
    def putFirstCol(self, col: Union[int, str]) -> None:
        """
        Place the column first by passing the name of the field.

        This slot is connected to the search combo box
        of the component. When we select a field it is placed
        as the first column and the table is rearranged with this column.
        In this way we will always have the table sorted by
        the field in which we want to search.

        @param c Field name, this column exchanges its position with the first column
        @return False if the field does not exist
        @author Friday@xmarts.com.mx
        @author InfoSiAL, S.L.
        """
        if not self.tableRecords_:
            raise Exception("tableRecords_ is not defined!")

        col_index_: int
        if isinstance(col, str):
            col_index_ = self.tableRecords_.logical_index_to_visual_index(
                self.tableRecords_.column_name_to_column_index(col)
            )
        else:
            col_index_ = col

        _index = self.tableRecords_.visual_index_to_column_index(col_index_)

        if _index is None or _index < 0:
            return
        self.moveCol(_index, self.sortColumn_)
        self.tableRecords_.sortByColumn(
            self.sortColumn_,
            QtCore.Qt.AscendingOrder if self.orderAsc_ else QtCore.Qt.DescendingOrder,
        )

    @decorators.pyqtSlot(int)
    @decorators.pyqtSlot(str)
    def putSecondCol(self, col: Union[int, str]) -> None:
        """
        Place the column as second by passing the name of the field.

        @author Silix - dpinelo
        """
        if not self.tableRecords_:
            raise Exception("tableRecords_ is not defined!")

        col_index_: int
        if isinstance(col, str):
            col_index_ = self.tableRecords_.logical_index_to_visual_index(
                self.tableRecords_.column_name_to_column_index(col)
            )
        else:
            col_index_ = col

        _index = self.tableRecords_.visual_index_to_column_index(col_index_)

        if _index is None or _index < 0:
            return

        self.moveCol(_index, self.sortColumn2_)

    @decorators.BetaImplementation
    def moveCol(self, from_: int, to: int, firstSearch: bool = True) -> None:
        """
        Move a column from one source field to the column in another destination field.

        @param from Name of the source column field
        @param to Name of the destination column field
        @param firstSearch dpinelo: Indicates if columns are moved considering that this function
        called or not, from the main search and filtering combo
        """
        if from_ < 0 or to < 0:
            return

        tMD = self.cursor().metadata()
        if not tMD:
            return

        if not self.tableRecords_:
            raise Exception("tableRecords_ is not defined!")

        self.tableRecords_.hide()

        textSearch = self.lineEditSearch.text()

        field = self.cursor().metadata().indexFieldObject(to)

        if to == 0:  # Si ha cambiado la primera columna
            try:
                self.comboBoxFieldToSearch.currentIndexChanged.disconnect(self.putFirstCol)
            except Exception:
                logger.error("Se ha producido un problema al desconectar")
                return

            self.comboBoxFieldToSearch.setCurrentIndex(from_)
            self.comboBoxFieldToSearch.currentIndexChanged.connect(self.putFirstCol)

            # Actializamos el segundo combo
            try:
                self.comboBoxFieldToSearch2.currentIndexChanged.disconnect(self.putSecondCol)
            except Exception:
                pass
            # Falta mejorar
            if (
                self.comboBoxFieldToSearch.currentIndex()
                == self.comboBoxFieldToSearch2.currentIndex()
            ):
                self.comboBoxFieldToSearch2.setCurrentIndex(
                    self.tableRecords_._h_header.logicalIndex(self.sortColumn_)
                )
            self.comboBoxFieldToSearch2.currentIndexChanged.connect(self.putSecondCol)

        if to == 1:  # Si es la segunda columna ...
            try:
                self.comboBoxFieldToSearch2.currentIndexChanged.disconnect(self.putSecondCol)
            except Exception:
                pass
            self.comboBoxFieldToSearch2.setCurrentIndex(from_)
            self.comboBoxFieldToSearch2.currentIndexChanged.connect(self.putSecondCol)

            if (
                self.comboBoxFieldToSearch.currentIndex()
                == self.comboBoxFieldToSearch2.currentIndex()
            ):
                try:
                    self.comboBoxFieldToSearch.currentIndexChanged.disconnect(self.putFirstCol)
                except Exception:
                    pass
                if (
                    self.comboBoxFieldToSearch.currentIndex()
                    == self.comboBoxFieldToSearch2.currentIndex()
                ):
                    self.comboBoxFieldToSearch.setCurrentIndex(
                        self.tableRecords_._h_header.logicalIndex(self.sortColumn2_)
                    )
                self.comboBoxFieldToSearch.currentIndexChanged.connect(self.putFirstCol)

        if not textSearch:
            textSearch = self.cursor().valueBuffer(field.name())

        # self.refresh(True)

        if textSearch:
            self.refresh(False, True)
            try:
                self.lineEditSearch.textChanged.disconnect(self.filterRecords)
            except Exception:
                pass
            self.lineEditSearch.setText(str(textSearch))
            self.lineEditSearch.textChanged.connect(self.filterRecords)
            self.lineEditSearch.selectAll()
            # self.seekCursor()
            QtCore.QTimer.singleShot(0, self.tableRecords_.ensureRowSelectedVisible)
        else:
            self.refreshDelayed()

        self.tableRecords_.header().swapSections(from_, to)

        self.refresh(True, False)

    # @decorators.BetaImplementation
    # def seekCursor(self) -> None:
    #    """
    #    Position the cursor on a valid record.
    #    """
    #    return
    # textSearch = self.lineEditSearch.text()
    # if not textSearch:
    #     return
    #
    # if not self.cursor():
    #     return
    #
    # # fN = self.sortField_.name()
    # textSearch.replace("%", "")

    # if "'" not in textSearch and "\\" not in textSearch:
    #     sql = self.cursor().executedQuery() + " LIMIT 1"
    #   """
    #       #QSqlQuery qry(sql, cursor_->db()->db()); #FIXME
    #       if (qry.first()) {
    # QString v(qry.value(0).toString());
    # int pos = -1;
    # if (!v.upper().startsWith(textSearch.upper()))
    #   pos = cursor_->atFromBinarySearch(fN, textSearch, orderAsc_);
    # if (pos == -1)
    #   pos = cursor_->atFromBinarySearch(fN, v, orderAsc_);
    # cursor_->seek(pos, false, true);
    # """

    def setEnabled(self, b: bool) -> None:
        """
        Set read only True or False.
        """
        self.setReadOnly(not b)

    def setColumnWidth(self, field: str, w: int) -> None:
        """
        Set the width of a column.

        @param field Name of the database field corresponding to the column
        @param w Column width
        """
        if self.tableRecords_:
            # col = self.tableRecords_.column_name_to_column_index(field) if isinstance(field, str) else field
            self.tableRecords_.setColWidth(field, w)

    def setCurrentRow(self, r: int) -> None:
        """
        Select the indicated row.

        @param r Index of the row to select
        """
        t = self.tableRecords_
        if t is None:
            return

        t.selectRow(r)
        t.scrollTo(t.cur.model().index(r, 0))

    @decorators.NotImplementedWarn
    def columnWidth(self, c: int) -> None:
        """
        Return Column width.
        """
        pass

    @decorators.NotImplementedWarn
    def setRowHeight(self, row: int, h: int) -> None:
        """
        Set the height of a row.

        @param row Row order number, starting at 0
        @param h High in the row
        """
        pass

    @decorators.NotImplementedWarn
    def rowHeight(self, row: int) -> None:
        """
        Return height in the row.
        """
        pass

    def exportToOds(self) -> None:
        """
        Export to an ODS spreadsheet and view it.
        """
        if not self.cursor():
            return

        cursor = pnsqlcursor.PNSqlCursor(self.cursor().curName())
        filter_ = self.cursor().curFilter()
        if not filter_:
            filter_ = "1 = 1"
        if self.cursor().sort():
            filter_ += " ORDER BY %s" % self.cursor().sort()
        cursor.select(filter_)
        from pineboolib.q3widgets.messagebox import MessageBox as QMessageBox

        if settings.config.value("ebcomportamiento/FLTableExport2Calc", False):
            QMessageBox.information(
                self.topWidget,
                self.tr("Opción deshabilitada"),
                self.tr("Esta opción ha sido deshabilitada por el administrador"),
                QMessageBox.Ok,
            )
            return

        mtd = cursor.metadata()
        if not mtd:
            return

        tdb = self.tableRecords()
        if not hasattr(tdb, "cursor"):
            return

        # hor_header = tdb.horizontalHeader()
        title_style = [aqods.AQOdsStyle.Align_center, aqods.AQOdsStyle.Text_bold]
        border_bot = aqods.AQOdsStyle.Border_bottom
        border_right = aqods.AQOdsStyle.Border_right
        border_left = aqods.AQOdsStyle.Border_left
        italic = aqods.AQOdsStyle.Text_italic
        ods_gen = aqods.AQOdsGenerator()
        spread_sheet = aqods.AQOdsSpreadSheet(ods_gen)
        sheet = aqods.AQOdsSheet(spread_sheet, mtd.alias())
        tdb_num_rows = cursor.size()
        tdb_num_cols = len(mtd.fieldNames())

        util = flutil.FLUtil()
        id_pix = 0
        pd = util.createProgressDialog("Procesando", tdb_num_rows)
        util.setProgress(1)
        row = aqods.AQOdsRow(sheet)
        row.addBgColor(aqods.AQOdsColor(0xE7E7E7))
        for i in range(tdb_num_cols):
            field = mtd.indexFieldObject(tdb.visual_index_to_logical_index(i))
            if field is not None and field.visibleGrid():
                row.opIn(title_style)
                row.opIn(border_bot)
                row.opIn(border_left)
                row.opIn(border_right)
                row.opIn(field.alias())

        row.close()

        # cur = tdb.cursor()
        # cur_row = tdb.currentRow()

        cursor.first()

        for r in range(tdb_num_rows):
            if pd.wasCanceled():
                break

            row = aqods.AQOdsRow(sheet)
            for c in range(tdb_num_cols):
                # idx = tdb.indexOf(c)  # Busca si la columna se ve
                # if idx == -1:
                #    continue

                field = mtd.indexFieldObject(tdb.visual_index_to_logical_index(c))
                if field is not None and field.visibleGrid():
                    val = cursor.valueBuffer(field.name())
                    if field.type() == "double":
                        row.setFixedPrecision(mtd.fieldPartDecimal(field.name()))
                        row.opIn(float(val))

                    elif field.type() == "date":
                        if val is not None:
                            val = str(val)
                            if val.find("T") > -1:
                                val = val[0 : val.find("T")]

                            row.opIn(val)
                        else:
                            row.coveredCell()

                    elif field.type() in ("bool", "unlock"):
                        str_ = self.tr("Sí") if val else self.tr("No")
                        row.opIn(italic)
                        row.opIn(str_)

                    elif field.type() == "pixmap":
                        if val:
                            if val.find("cacheXPM") > -1:
                                pix = QtGui.QPixmap(val)
                                if not pix.isNull():

                                    pix_name = "pix%s_" % id_pix
                                    id_pix += 1
                                    row.opIn(
                                        aqods.AQOdsImage(
                                            pix_name,
                                            round((pix.width() * 2.54) / 98, 2) * 20,
                                            round((pix.height() * 2.54) / 98, 2) * 20,
                                            0,
                                            0,
                                            val,
                                        )
                                    )
                                else:
                                    row.coveredCell()

                            else:
                                row.coveredCell()
                        else:
                            row.coveredCell()

                    else:
                        if isinstance(val, list):
                            val = ",".join(val)

                        if val:
                            row.opIn(str(val))
                        else:
                            row.coveredCell()
            row.close()
            if not r % 4:
                util.setProgress(r)

            cursor.next()

        # cur.seek(cur_row)
        sheet.close()
        spread_sheet.close()

        util.setProgress(tdb_num_rows)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        file_name = "%s/%s%s.ods" % (
            application.PROJECT.tmpdir,
            mtd.name(),
            QtCore.QDateTime.currentDateTime().toString("ddMMyyyyhhmmsszzz"),
        )
        ods_gen.generateOds(file_name)
        if not application.PROJECT.debug_level == 1000:  # test
            sysbasetype.SysBaseType.openUrl(file_name)

        QtWidgets.QApplication.restoreOverrideCursor()
        util.destroyProgressDialog()

    def switchSortOrder(self, col: int = 0) -> None:
        """
        Switch the direction of the table records sorting, from ascending to descending and vice versa.

        Records are always sorted by the first column.
        If the autoSortColumn property is TRUE.
        """
        if not self.autoSortColumn_:
            return
        if self.tableRecords_:
            if self.tableRecords_.logical_index_to_visual_index(
                col
            ) == self.tableRecords_.visual_index_to_column_index(self.sortColumn_):

                self.orderAsc_ = not self.orderAsc_

            self.setSortOrder(self.orderAsc_, self.sortColumn_)

    @decorators.pyqtSlot(str)
    def filterRecords(self, p: str) -> None:
        """
        Filter the records in the table using the first field, according to the given pattern.

        This slot is connected to the component search text box,
        taking the content of this as a standard for filtering.

        @param p Character string with filtering pattern
        """
        if not self.cursor().model():
            return
        bFilter: Any = None
        if not self.tableRecords_:
            raise Exception("tableRecords_ is not defined!")

        # if p:
        #    p = "%s%%" % p

        refreshData = False
        # if p.endswith("%"): refreshData = True

        msec_refresh = 400
        colidx = self.tableRecords_.visual_index_to_logical_index(self.sortColumn_)
        if colidx is None:
            raise Exception("Unexpected: Column not found")
        field = self.cursor().model().metadata().indexFieldObject(colidx)
        bFilter = self.cursor().db().connManager().manager().formatAssignValueLike(field, p, True)

        idMod = (
            self.cursor()
            .db()
            .connManager()
            .managerModules()
            .idModuleOfFile("%s.mtd" % self.cursor().metadata().name())
        )
        functionQSA = idMod + ".tableDB_filterRecords_" + self.cursor().metadata().name()

        vargs = []
        vargs.append(self.cursor().metadata().name())
        vargs.append(p)
        vargs.append(field.name())
        vargs.append(bFilter)

        if functionQSA:
            msec_refresh = 200
            ret = None
            try:

                ret = application.PROJECT.call(functionQSA, vargs, None, False)
                logger.debug("functionQSA:%s:", functionQSA)
            except Exception:
                pass
            else:
                if ret is not isinstance(ret, bool):
                    bFilter = ret
                else:
                    if p == "":
                        bFilter = None

        self.refreshDelayed(msec_refresh, refreshData)
        if bFilter:
            self.filter_ = bFilter
        else:
            self.filter_ = ""

    def setSortOrder(
        self, ascending: Union[bool, int] = True, col_order: Optional[int] = None
    ) -> None:
        """Set sort columns order."""
        if isinstance(ascending, int):
            ascending = True if ascending == 1 else False

        order = QtCore.Qt.AscendingOrder if ascending else QtCore.Qt.DescendingOrder

        col = col_order if col_order is not None else self.sortColumn_

        if col == 0:
            self.orderAsc_ = ascending
        elif col == 1:
            self.orderAsc2_ = ascending
        elif col == 2:
            self.orderAsc3_ = ascending

        if self.tableRecords_:
            while True:

                column = self.tableRecords_.header().logicalIndex(col)
                if not self.tableRecords_.isColumnHidden(column):
                    break
                col += 1
            self.tableRecords_.sortByColumn(column, order)

    def isSortOrderAscending(self) -> bool:
        """Return if the order of the first column is ascending."""

        return self.orderAsc_

    def setActionName(self, name: str):
        """Set action Name to the cursor (Deprecated)."""
        pass

    def activeTabData(self, b: bool) -> None:
        """
        Activate the data table.
        """
        # if (self.topWidget and not self.tabTable.visibleWidget() == self.tabData):
        if self.tabFilter is not None:
            self.tabFilter.hide()
        if self.tabData is not None:
            self.tabData.show()
        self.refreshTabData()
        # self.tabTable.raiseWidget(self.tabData)

    def activeTabFilter(self, b: bool) -> None:
        """
        Activate the filter table.
        """
        # if (self.topWidget and not self.tabTable.visibleWidget() == self.tabFilter):
        if self.tabData is not None:
            self.tabData.hide()
        if self.tabFilter is not None:
            self.tabFilter.show()
        self.refreshTabFilter()
        # self.tabTable.raiseWidget(self.tabFilter)

    def tdbFilterClear(self) -> None:
        """
        Clean and initialize the filter.
        """
        if not self.topWidget:
            return

        self.tabFilterLoaded = False
        self.refreshTabFilter()

    """
    Señal emitida cuando se refresca por cambio de filtro
    """
    refreshed = QtCore.pyqtSignal()

    """
    Señal emitida cuando se establece si el componente es o no de solo lectura.
    """
    readOnlyChanged = QtCore.pyqtSignal(bool)

    """
    Señal emitida cuando se establece si el componente es o no de solo edición.
    """
    editOnlyChanged = QtCore.pyqtSignal(bool)

    """
    Señal emitida cuando se establece si el componente es o no de solo inserción.
    """
    insertOnlyChanged = QtCore.pyqtSignal(bool)

    """
    Señal emitida cuando se establece cambia el registro seleccionado.
    """
    currentChanged = QtCore.pyqtSignal()

    def primarysKeysChecked(self) -> List[Any]:
        """Return a list of the primary keys checked."""
        return self.tableRecords().primarysKeysChecked()

    def clearChecked(self) -> None:
        """Empty the list of primary keys checked."""

        self.tableRecords().clearChecked()

    def setPrimaryKeyChecked(self, name: str, b: bool) -> None:
        """Set a primary key cheked and add to the cheked list."""

        self.tableRecords().setPrimaryKeyChecked(name, b)
