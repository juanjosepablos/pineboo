"""Main module for starting up Pineboo."""
import gc
import sys
from optparse import Values
from typing import List, Type, Optional, TYPE_CHECKING
from types import TracebackType

from PyQt5 import QtCore, QtWidgets

from pineboolib import logging
from pineboolib.core.utils.utils_base import is_deployed
from pineboolib.core import settings
from pineboolib.loader.dlgconnect.conn_dialog import show_connection_dialog
from pineboolib.loader.options import parse_options
from pineboolib.loader.dgi import load_dgi
from pineboolib.loader.connection import config_dbconn, connect_to_db
from pineboolib.loader.connection import DEFAULT_SQLITE_CONN, IN_MEMORY_SQLITE_CONN
from pineboolib import plugins
from pineboolib import application
from pineboolib.application.parsers.qsaparser import pytnyzer

if TYPE_CHECKING:
    from pineboolib.loader import projectconfig  # noqa: F401

LOGGER = logging.getLogger(__name__)


def startup_no_x() -> None:
    """Start Pineboo with no GUI."""
    startup(enable_gui=False)


def startup_framework(conn: Optional["projectconfig.ProjectConfig"] = None) -> None:
    """Start Pineboo project like framework."""
    if conn is None:
        raise Exception("conn is empty!")

    qapp = QtWidgets.QApplication(sys.argv + ["-platform", "offscreen"])
    init_logging()
    init_cli(catch_ctrl_c=False)
    pytnyzer.STRICT_MODE = False
    application.PROJECT.load_version()
    application.PROJECT.setDebugLevel(1000)
    application.PROJECT.set_app(qapp)
    dgi = load_dgi("qt", None)
    application.PROJECT.init_dgi(dgi)
    conn_ = connect_to_db(conn)
    main_conn_established = application.PROJECT.init_conn(connection=conn_)

    if not main_conn_established:
        raise Exception("No main connection was established. Aborting Pineboo load.")

    application.PROJECT.no_python_cache = True
    application.PROJECT.run()
    application.PROJECT.conn_manager.managerModules().loadIdAreas()
    application.PROJECT.conn_manager.managerModules().loadAllIdModules()
    application.PROJECT.load_modules()


def startup(enable_gui: bool = None) -> None:
    """Start up pineboo."""
    # FIXME: No hemos cargado pineboo aún. No se pueden usar métodos internos.
    from pineboolib.core.utils.check_dependencies import check_dependencies_cli

    if not check_dependencies_cli(
        {"ply": "python3-ply", "PyQt5.QtCore": "python3-pyqt5", "Python": "Python"}
    ):
        sys.exit(32)

    min_python = (3, 6)
    if sys.version_info < min_python:
        sys.exit("Python %s.%s or later is required.\n" % min_python)

    options = parse_options()
    if enable_gui is not None:
        options.enable_gui = enable_gui
    trace_loggers: List[str] = []
    if options.trace_loggers:
        trace_loggers = options.trace_loggers.split(",")

    init_logging(logtime=options.log_time, loglevel=options.loglevel, trace_loggers=trace_loggers)

    if options.enable_profiler:
        ret = exec_main_with_profiler(options)
    else:
        ret = exec_main(options)
    # setup()
    # exec_()
    gc.collect()
    print("Closing Pineboo...")
    if ret:
        sys.exit(ret)
    else:
        sys.exit(0)


def init_logging(
    loglevel: int = logging.INFO, logtime: bool = False, trace_loggers: List[str] = []
) -> None:
    """Initialize pineboo logging."""
    # ---- LOGGING -----
    log_format = "%(levelname)s: %(name)s: %(message)s"

    if logtime:
        log_format = "%(asctime)s - %(levelname)s: %(name)s: %(message)s"

    app_loglevel = logging.TRACE if trace_loggers else loglevel
    if trace_loggers:
        logging.Logger.set_pineboo_default_level(loglevel)

    logging.basicConfig(format=log_format, level=app_loglevel)
    # LOGGER.info("LOG LEVEL: %s", loglevel)
    disable_loggers = ["PyQt5.uic.uiparser", "PyQt5.uic.properties", "blib2to3.pgen2.driver"]
    for loggername in disable_loggers:
        modlogger = logging.getLogger(loggername)
        modlogger.setLevel(logging.WARN)

    for loggername in trace_loggers:
        modlogger = logging.getLogger(loggername)
        modlogger.setLevel(logging.TRACE)


def exec_main_with_profiler(options: Values) -> int:
    """Enable profiler."""
    import cProfile
    import pstats
    import io
    from pstats import SortKey  # type: ignore

    profile = cProfile.Profile()
    profile.enable()
    ret = exec_main(options)
    profile.disable()
    string_io = io.StringIO()
    sortby = SortKey.TIME
    print_stats = pstats.Stats(profile, stream=string_io).sort_stats(sortby)
    print_stats.print_stats(40)
    print(string_io.getvalue())
    return ret


def init_cli(catch_ctrl_c: bool = True) -> None:
    """Initialize singletons, signal handling and exception handling."""

    def _excepthook(
        type_: Type[BaseException], value: BaseException, traceback: TracebackType
    ) -> None:
        import traceback as pytback

        pytback.print_exception(type_, value, traceback)

    # PyQt 5.5 o superior aborta la ejecución si una excepción en un slot()
    # no es capturada dentro de la misma; el programa falla con SegFault.
    # Aunque esto no debería ocurrir, y se debería prevenir lo máximo posible
    # es bastante incómodo y genera problemas graves para detectar el problema.
    # Agregamos sys.excepthook para controlar esto y hacer que PyQt5 no nos
    # dé un segfault, aunque el resultado no sea siempre correcto:
    sys.excepthook = _excepthook
    # -------------------
    if catch_ctrl_c:
        # Fix Control-C / KeyboardInterrupt for PyQt:
        import signal

        signal.signal(signal.SIGINT, signal.SIG_DFL)

    # FIXME: Order of import is REALLY important here. FIX.
    # from pineboolib.fllegacy.aqsobjects import aqsobjectfactory
    #
    # aqsobjectfactory.AQUtil = aqsobjectfactory.AQUtil_class()
    # aqsobjectfactory.AQS = aqsobjectfactory.AQS_class()

    from pineboolib.fllegacy import flapplication

    flapplication.aqApp = flapplication.FLApplication()

    from pineboolib.qsa import qsa

    qsa.aqApp = flapplication.aqApp
    # from pineboolib import pncontrolsfactory
    #
    # pncontrolsfactory.System = pncontrolsfactory.System_class()
    # pncontrolsfactory.qsa_sys = pncontrolsfactory.SysType()


def init_gui() -> None:
    """Create GUI singletons."""
    from pineboolib.plugins.mainform.eneboo import eneboo
    from pineboolib.plugins.mainform.eneboo_mdi import eneboo_mdi

    eneboo.mainWindow = eneboo.MainForm()
    eneboo_mdi.mainWindow = eneboo_mdi.MainForm()


def setup_gui(app: QtWidgets.QApplication, options: Values) -> None:
    """Configure GUI app."""
    from pineboolib.core.utils.utils_base import filedir
    from PyQt5 import QtGui

    noto_fonts = [
        "NotoSans-BoldItalic.ttf",
        "NotoSans-Bold.ttf",
        "NotoSans-Italic.ttf",
        "NotoSans-Regular.ttf",
    ]
    for fontfile in noto_fonts:
        QtGui.QFontDatabase.addApplicationFont(filedir("./core/fonts/Noto_Sans", fontfile))

    style_app: str = settings.config.value("application/style", "Fusion")
    app.setStyle(style_app)  # type: ignore

    default_font = settings.config.value("application/font", None)
    if default_font is None:
        font = QtGui.QFont("Noto Sans", 9)
        font.setBold(False)
        font.setItalic(False)
    else:
        # FIXME: FLSettings.readEntry does not return an array
        font = QtGui.QFont(
            default_font[0], int(default_font[1]), int(default_font[2]), default_font[3] == "true"
        )

    app.setFont(font)


def init_testing() -> None:
    """Initialize Pineboo for testing purposes."""
    settings.config.set_value("application/dbadmin_enabled", True)

    if application.PROJECT.dgi is not None:
        from pineboolib.application.database import pnconnectionmanager

        del application.PROJECT._conn_manager
        application.PROJECT._conn_manager = pnconnectionmanager.PNConnectionManager()

    else:
        qapp = QtWidgets.QApplication(sys.argv + ["-platform", "offscreen"])

        init_logging()  # NOTE: Use pytest --log-level=0 for debug
        init_cli(catch_ctrl_c=False)

        pytnyzer.STRICT_MODE = False
        application.PROJECT.load_version()
        application.PROJECT.setDebugLevel(1000)
        application.PROJECT.set_app(qapp)
        dgi = load_dgi("qt", None)

        application.PROJECT.init_dgi(dgi)

    conn = connect_to_db(IN_MEMORY_SQLITE_CONN)
    main_conn_established = application.PROJECT.init_conn(connection=conn)

    if not main_conn_established:
        raise Exception("No main connection was established. Aborting Pineboo load.")

    application.PROJECT.no_python_cache = True
    if application.PROJECT.run():

        # Necesario para que funcione isLoadedModule ¿es este el mejor sitio?
        application.PROJECT.conn_manager.managerModules().loadIdAreas()
        application.PROJECT.conn_manager.managerModules().loadAllIdModules()

        application.PROJECT.load_modules()
    else:
        raise Exception("Project initialization failed!")


def finish_testing() -> None:
    """Clear data from pineboo project."""
    # import time

    application.PROJECT.conn_manager.manager().cleanupMetaData()
    application.PROJECT.actions = {}
    application.PROJECT.areas = {}
    application.PROJECT.modules = {}
    application.PROJECT.tables = {}
    if application.PROJECT.main_window:
        application.PROJECT.main_window.initialized_mods_ = []

    # application.PROJECT.conn.execute_query("DROP DATABASE %s" % IN_MEMORY_SQLITE_CONN.database)
    application.PROJECT.conn_manager.finish()
    # application.PROJECT.conn_manager.mainConn().driver_ = None
    # application.PROJECT.conn_manager.conn.close()
    # application.PROJECT.conn.conn = None
    # del application.PROJECT._conn_manager
    # application.PROJECT._conn_manager = None
    # time.sleep(0.5)  # Wait until database close ends

    from pineboolib.application import qsadictmodules
    import shutil
    import os

    try:
        shutil.rmtree(application.PROJECT.tmpdir)
    except Exception:
        LOGGER.warning(
            "No se ha podido borrar %s al limpiar cambios del test", application.PROJECT.tmpdir
        )
        pass
    qsadictmodules.QSADictModules.clean_all()
    if not os.path.exists(application.PROJECT.tmpdir):
        os.mkdir(application.PROJECT.tmpdir)
    # needed for delete older virtual database.

    # conn = connect_to_db(IN_MEMORY_SQLITE_CONN)
    # application.PROJECT.init_conn(connection=conn)
    # application.PROJECT.run()


def exec_main(options: Values) -> int:
    """
    Exec main program.

    Handles optionlist and help.
    Also initializes all the objects
    """
    # FIXME: This function should not initialize the program

    # -------------------

    # import pineboolib.pnapplication
    # from pineboolib.core.utils.utils_base import filedir
    # from pineboolib.pnsqldrivers import PNSqlDrivers

    init_cli()

    # TODO: Refactorizar función en otras más pequeñas

    pytnyzer.STRICT_MODE = False

    application.PROJECT.setDebugLevel(options.debug_level)

    application.PROJECT.options = options
    if options.enable_gui:
        app_ = QtWidgets.QApplication
        app_.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

        application.PROJECT.set_app(app_(sys.argv))
        setup_gui(application.PROJECT.app, options)
    else:
        application.PROJECT.set_app(QtWidgets.QApplication(sys.argv + ["-platform", "offscreen"]))

    if options.trace_debug:
        from pineboolib.core.utils.utils_base import traceit

        # "sys.settrace" function could lead to arbitrary code execution
        sys.settrace(traceit)  # noqa: DUO111

    if options.trace_signals:
        from .utils import monkey_patch_connect

        monkey_patch_connect()

    if options.orm_disabled:
        settings.config.set_value("ebcomportamiento/orm_enabled", False)

    if options.enable_dbadmin:
        settings.config.set_value("application/dbadmin_enabled", True)

    if options.enable_quick:
        settings.config.set_value("application/dbadmin_enabled", False)

    if options.main_form:
        settings.config.set_value("ebcomportamiento/main_form_name", options.main_form)

    application.PROJECT.load_version()

    if is_deployed():
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        from pineboolib.core.utils.utils_base import download_files

        download_files()

    dgi = load_dgi(options.dgi, options.dgi_parameter)
    if options.enable_gui:
        init_gui()

    if dgi.useDesktop() and not options.enable_gui:
        LOGGER.info(
            "Selected DGI <%s> is not compatible with <pineboo-core>. Use <pineboo> instead"
            % options.dgi
        )

    if not dgi.useDesktop() and options.enable_gui:
        LOGGER.info(
            "Selected DGI <%s> does not need graphical interface. Use <pineboo-core> for better results"
            % options.dgi
        )

    if not dgi.useMLDefault():
        # When a particular DGI doesn't want the standard init, we stop loading here
        # and let it take control of the remaining pieces.
        return dgi.alternativeMain(options)

    configdb = config_dbconn(options)
    LOGGER.debug(configdb)
    application.PROJECT.init_dgi(dgi)

    from pineboolib.fllegacy.flapplication import aqApp

    lang = QtCore.QLocale().name()[:2]
    if lang == "C":
        lang = "es"
    aqApp.loadTranslationFromModule("sys", lang)

    if not configdb and dgi.useDesktop() and dgi.localDesktop():
        if not dgi.mobilePlatform():

            configdb = show_connection_dialog(application.PROJECT.app)
            if configdb is None:
                return 2
        else:
            settings.config.set_value("application/dbadmin_enabled", True)
            configdb = DEFAULT_SQLITE_CONN

    if not configdb:
        raise ValueError("No connection given. Nowhere to connect. Cannot start.")

    conn = connect_to_db(configdb)
    main_conn_established = application.PROJECT.init_conn(connection=conn)
    if not main_conn_established:
        LOGGER.warning("No main connection was provided. Aborting Pineboo load.")
        return -99

    settings.settings.set_value("DBA/lastDB", conn.DBName())

    application.PROJECT.no_python_cache = options.no_python_cache

    # if options.test:
    #    return 0 if application.PROJECT.test() else 1

    # if dgi.useDesktop():
    # FIXME: What is happening here? Why dynamic load?
    # import importlib  # FIXME: Delete dynamic import and move this code between Project and DGI plugins

    # application.PROJECT.main_form = (
    #    importlib.import_module(
    #        "pineboolib.plugins.mainform.%s.%s"
    #        % (application.PROJECT.main_form_name, application.PROJECT.main_form_name)
    #    )
    #    if dgi.localDesktop()
    #    else dgi.mainForm()
    # )
    main_form_name = settings.config.value("ebcomportamiento/main_form_name", "eneboo")

    main_form = getattr(plugins.mainform, main_form_name, None)
    if main_form is None:
        settings.config.set_value("ebcomportamiento/main_form_name", "eneboo")
        raise Exception(
            "mainForm %s does not exits!!.Use 'pineboo --main_form eneboo' to restore default mainForm"
            % main_form_name
        )
    else:
        application.PROJECT.main_form = getattr(main_form, main_form_name)

    application.PROJECT.main_window = getattr(application.PROJECT.main_form, "mainWindow", None)
    main_form_ = getattr(application.PROJECT.main_form, "MainForm", None)
    if main_form_ is not None:
        main_form_.setDebugLevel(options.debug_level)

    application.PROJECT.message_manager().send("splash", "show")

    application.PROJECT.run()

    from pineboolib.application.acls import pnaccesscontrollists

    acl = pnaccesscontrollists.PNAccessControlLists()
    acl.init()

    if acl._access_control_list:
        aqApp.set_acl(acl)

    # conn = application.PROJECT.conn_manager.mainConn()

    # if not conn:
    #    LOGGER.warning("No connection was provided. Aborting Pineboo load.")
    #    return -99

    if settings.config.value("ebcomportamiento/orm_enabled", False) and not settings.config.value(
        "ebcomportamiento/orm_parser_disabled", False
    ):
        from pineboolib.application.parsers.mtdparser.pnmtdparser import mtd_parse

        for table in conn.tables("Tables"):
            mtd_parse(table)

    # Necesario para que funcione isLoadedModule ¿es este el mejor sitio?
    application.PROJECT.conn_manager.managerModules().loadIdAreas()
    application.PROJECT.conn_manager.managerModules().loadAllIdModules()

    application.PROJECT.load_modules()

    # FIXME: move this code to pineboo.application
    application.PROJECT.message_manager().send(
        "splash", "showMessage", ["Cargando traducciones ..."]
    )
    aqApp.loadTranslations()

    from .init_project import init_project

    ret = init_project(
        dgi,
        options,
        application.PROJECT,
        application.PROJECT.main_form if dgi.useDesktop() else None,
        application.PROJECT.app,
    )
    return ret
