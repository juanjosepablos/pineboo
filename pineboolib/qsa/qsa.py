# -*- coding: utf-8 -*-
"""
QSA Emulation module.

This file should be imported at top of QS converted files.
"""

import re  # noqa: F401

from pineboolib.fllegacy import flapplication

from pineboolib.core.utils.utils_base import ustr, filedir  # noqa: F401
from pineboolib.application.types import QString, String  # noqa: F401
from pineboolib.application.types import boolean as Boolean  # noqa: F401
from pineboolib.application.types import function as Function  # noqa: F401
from pineboolib.application.types import object_ as Object  # noqa: F401

from pineboolib.application.types import File, Dir, Array, Date, AttributeDict  # noqa: F401
from pineboolib.application.types import FileStatic, DirStatic  # noqa: F401

from .input import Input  # noqa: F401
from .utils import switch, qsaRegExp, RegExp, Math, parseFloat, parseString, parseInt  # noqa: F401
from .utils import startTimer, killTimer, debug, isnan, replace, isNaN, length, text  # noqa: F401
from .utils import format_exc, Number, killTimers, Sort, splice  # noqa: F401
from .dictmodules import Application, from_project  # noqa: F401

# QT
from .pncontrolsfactory import QComboBox, QTable, QLayoutWidget, QToolButton  # noqa: F401
from .pncontrolsfactory import QTabWidget, QLabel, QGroupBox, QListView, QImage  # noqa: F401
from .pncontrolsfactory import QTextEdit, QLineEdit, QDateEdit, QTimeEdit  # noqa: F401
from .pncontrolsfactory import QCheckBox, QWidget, QMessageBox, QDialog, QDateTime  # noqa: F401
from .pncontrolsfactory import QVBoxLayout, QHBoxLayout, QFrame, QMainWindow  # noqa: F401
from .pncontrolsfactory import QMenu, QToolBar, QAction, QDataView, QByteArray  # noqa: F401
from .pncontrolsfactory import QMdiArea, QEventLoop, QActionGroup, QInputDialog  # noqa: F401
from .pncontrolsfactory import QApplication, QStyleFactory, QFontDialog, QTextStream  # noqa: F401
from .pncontrolsfactory import QMdiSubWindow, QSizePolicy, QProgressDialog  # noqa: F401
from .pncontrolsfactory import QFileDialog, QTreeWidget, QTreeWidgetItem  # noqa: F401
from .pncontrolsfactory import QTreeWidgetItemIterator, QListWidgetItem, QObject  # noqa: F401
from .pncontrolsfactory import QListViewWidget, QSignalMapper, QPainter, QBrush  # noqa: F401
from .pncontrolsfactory import QKeySequence, QIcon, QColor, QDomDocument, QIconSet  # noqa: F401
from .pncontrolsfactory import QPushButton, QSpinBox, QRadioButton, QPixmap  # noqa: F401
from .pncontrolsfactory import QButtonGroup, QToolBox, QSize, QDockWidget, QDir  # noqa: F401
from .pncontrolsfactory import QPopupMenu, QBuffer, QHButtonGroup, QVButtonGroup  # noqa: F401
from .pncontrolsfactory import QHttp, QHttpResponseHeader, QHttpRequestHeader  # noqa: F401

# FL
from .pncontrolsfactory import FLDomDocument, FLDomElement, FLDomNode  # noqa: F401
from .pncontrolsfactory import FLDomNodeList, FLLineEdit, FLTimeEdit, FLDateEdit  # noqa: F401
from .pncontrolsfactory import FLPixmapView, FLDataTable, FLCheckBox  # noqa: F401
from .pncontrolsfactory import FLTextEditOutput, FLSpinBox, FLTableDB, FLFieldDB  # noqa: F401
from .pncontrolsfactory import FLFormDB, FLFormRecordDB, FLFormSearchDB  # noqa: F401
from .pncontrolsfactory import FLDoubleValidator, FLIntValidator, FLUIntValidator  # noqa: F401
from .pncontrolsfactory import FLCodBar, FLWidget, FLWorkSpace, FLPosPrinter  # noqa: F401
from .pncontrolsfactory import FLSqlQuery, FLSqlCursor, FLNetwork, FLSerialPort  # noqa: F401
from .pncontrolsfactory import FLApplication, FLVar, FLSmtpClient, FLTable  # noqa: F401
from .pncontrolsfactory import FLListViewItem, FLReportViewer, FLUtil, FLSettings  # noqa: F401
from .pncontrolsfactory import FLScriptEditor, FLReportEngine, FLJasperEngine  # noqa: F401

# QSA
from .pncontrolsfactory import FileDialog, Color, Label, Line, CheckBox, Dialog  # noqa: F401
from .pncontrolsfactory import ComboBox, TextEdit, LineEdit, MessageBox, RadioButton  # noqa: F401
from .pncontrolsfactory import GroupBox, SpinBox, NumberEdit, DateEdit, TimeEdit  # noqa: F401
from .pncontrolsfactory import Picture, Rect, Size, Pixmap, Font  # noqa: F401


# AQS
from .pncontrolsfactory import AQS, AQUnpacker, AQSettings, AQSqlQuery  # noqa: F401
from .pncontrolsfactory import AQSqlCursor, AQUtil, AQSql, AQSmtpClient  # noqa: F401
from .pncontrolsfactory import AQSignalMapper, AQSSProject, AQObjectQueryList  # noqa: F401
from .pncontrolsfactory import AQSButtonGroup  # noqa: F401

from pineboolib.core.utils.utils_base import is_deployed as __is_deployed

if not __is_deployed():
    # FIXME: No module named 'xml.sax.expatreader' in deploy
    from .pncontrolsfactory import AQOdsGenerator, AQOdsSpreadSheet, AQOdsSheet  # noqa: F401
    from .pncontrolsfactory import AQOdsRow, AQOdsColor, AQOdsStyle, AQOdsImage  # noqa: F401

from .pncontrolsfactory import AQBoolFlagState, AQBoolFlagStateList  # noqa: F401


from .pncontrolsfactory import FormDBWidget  # noqa: F401
from pineboolib.application.process import Process, ProcessStatic  # noqa: F401
from .pncontrolsfactory import SysType, sys, System  # noqa: F401


QFile = File
util = FLUtil
print_ = print
QSProject = AQSSProject()

undefined = None
LogText = 0
RichText = 1
aqApp: flapplication.FLApplication
