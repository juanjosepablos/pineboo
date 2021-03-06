# -*- coding: utf-8 -*-
"""
Main Eneboo-alike UI.
"""
from PyQt5 import QtWidgets, QtCore, QtGui, QtXml

from pineboolib.core import settings
from pineboolib.core.utils import utils_base

from pineboolib.q3widgets import qmessagebox

from pineboolib.fllegacy.aqsobjects import aqsobjectfactory

from pineboolib.fllegacy import flformdb, flapplication, systype

from pineboolib import logging, application


from typing import Any, Dict, Optional, List, cast, Union


qsa_sys = systype.SysType()
logger = logging.getLogger("mainForm_%s" % __name__)


class DockListView(QtCore.QObject):
    """DockListWiew class."""

    w_: QtWidgets.QDockWidget
    lw_: QtWidgets.QTreeWidget
    ag_: QtWidgets.QActionGroup
    _name: str
    set_visible = QtCore.pyqtSignal(bool)
    Close = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None, name: str = "dockListView", title: str = "") -> None:
        """Initialize the DockListView instance."""

        super(DockListView, self).__init__(parent)
        if parent is None:
            return
        self.AQS = aqsobjectfactory.AQS
        self._name = name
        self.w_ = QtWidgets.QDockWidget(name, parent)
        self.w_.setObjectName("%sListView" % name)
        self.lw_ = QtWidgets.QTreeWidget(self.w_)
        self.lw_.setObjectName(self._name)
        # this.lw_.addColumn("");
        # this.lw_.addColumn("");
        self.lw_.setColumnCount(2)
        self.lw_.setHeaderLabels(["", ""])
        self.lw_.headerItem().setHidden(True)
        # this.lw_.setSorting(-1);
        # this.lw_.rootIsDecorated = true;
        # this.lw_.setColumnWidthMode(1, 0);
        self.lw_.hideColumn(1)
        # self.lw_.headerItem().hide()
        # self.lw_.headerItem().setResizeEnabled(false, 1)

        self.w_.setWidget(self.lw_)
        self.w_.setWindowTitle(title)

        """
        w.resizeEnabled = true;
        w.closeMode = true;
        w.setFixedExtentWidth(300);
        """

        self.lw_.doubleClicked.connect(self.activateAction)

    def writeState(self) -> None:
        """Save the state and geometry."""

        if self.w_ is None:
            raise Exception("self.w_ is empty!")

        settings = aqsobjectfactory.AQSettings()
        key = "MainWindow/%s/" % self.w_.objectName()
        # FIXME
        # settings.writeEntry("%splace" % key, self.w_.place())  # Donde está emplazado

        settings.writeEntry("%svisible" % key, self.w_.isVisible())
        settings.writeEntry("%sx" % key, self.w_.x())
        settings.writeEntry("%sy" % key, self.w_.y())
        settings.writeEntry("%swidth" % key, self.w_.width())
        settings.writeEntry("%sheight" % key, self.w_.height())
        # FIXME
        # settings.writeEntry("%soffset", key, self.offset())
        # area = self.area()
        # settings.writeEntry("%sindex" % key, area.findDockWindow(self.w_) if area else None)

    def readState(self) -> None:
        """Read the state and geometry."""

        if self.w_ is None:
            raise Exception("self.w_ is empty!")

        if self.lw_ is None:
            raise Exception("self.lw_ is empty!")

        settings = aqsobjectfactory.AQSettings()
        key = "MainWindow/%s/" % self.w_.objectName()
        # FIXME
        # place = settings.readNumEntry("%splace" % key, self.AQS.InDock)
        # if place == self.AQS.OutSideDock:
        #    self.w_.setFloating(True)
        #    self.w_.move(settings.readNumEntry("%sx" % key, self.w_.x()),
        #                 settings.readNumEntry("%sy" % key, self.w_.y()))

        # self.w_.offset = settings.readNumEntry("%soffset" % key, self.offset)
        # index = settings.readNumEntry("%sindex" % key, None)
        # FIXME
        # if index is not None:
        #    area = w.area()
        #    if area:
        #        area.moveDockWindow(w, index)

        width = settings.readNumEntry("%swidth" % key, self.w_.width())
        height = settings.readNumEntry("%sheight" % key, self.w_.height())
        self.lw_.resize(width, height)
        # self.w_.resize(width, height)

        if not application.PROJECT.DGI.mobilePlatform():
            visible = settings.readBoolEntry("%svisible" % key, True)
            if visible:
                self.w_.show()

            else:
                self.w_.hide()

            self.set_visible.emit(not self.w_.isHidden())
        else:
            self.w_.hide()
            self.set_visible.emit(False)
            self.w_.close()

    def initFromWidget(self, w) -> None:
        """Initialize the internal widget."""

        self.w_ = w
        self.lw_ = w.widget()
        if self.lw_ and self.lw_.doubleClicked:
            self.lw_.doubleClicked.connect(self.activateAction)

    def change_state(self, s: bool) -> None:
        """Change the display status."""
        if self.w_ is None:
            raise Exception("not initialized")
        if s:
            self.w_.show()
        else:
            self.w_.close()

    def activateAction(self, item) -> None:
        """Activate the action associated with the active item."""

        if item is None or not self.ag_:
            return

        action_name = item.sibling(item.row(), 1).data()
        if action_name == "":
            return

        ac: QtWidgets.QAction = cast(
            QtWidgets.QAction, self.ag_.findChild(QtWidgets.QAction, action_name)
        )
        if ac:
            ac.triggered.emit()

    def update(
        self, action_group: Optional[QtWidgets.QActionGroup] = None, reverse: bool = False
    ) -> None:
        """Update available items."""
        if not action_group:
            return

        self.ag_ = action_group

        if not self.lw_:
            return

        self.lw_.clear()

        self.buildListView(self.lw_, self.AQS.toXml(self.ag_), self.ag_, reverse)

    def buildListView(self, parent_item, parent_element, ag, reverse: bool) -> None:
        """Build the tree of available options."""

        this_item = None
        node = (
            parent_element.lastChild().toElement()
            if reverse
            else parent_element.firstChild().toElement()
        )
        while not node.isNull():
            if node.attribute("objectName") in ("", "separator"):  # Pasamos de este
                node = (
                    node.previousSibling().toElement()
                    if reverse
                    else node.nextSibling().toElement()
                )
                continue
            class_name = node.attribute("class")
            if class_name.startswith("QAction"):
                if class_name == "QActionGroup":
                    act_group = ag.findChild(QtWidgets.QActionGroup, node.attribute("objectName"))
                    if act_group and not act_group.isVisible():
                        node = (
                            node.previousSibling().toElement()
                            if reverse
                            else node.nextSibling().toElement()
                        )
                        continue

                    group_name = node.attribute("objectName")
                    if (
                        group_name not in ("pinebooActionGroup")
                        and not group_name.endswith("Actions")
                        and not group_name.startswith(("pinebooAg"))
                    ) or group_name.endswith("MoreActions"):

                        this_item = QtWidgets.QTreeWidgetItem(parent_item)
                        this_item.setText(0, group_name)

                    else:
                        this_item = parent_item

                    self.buildListView(this_item, node, ag, reverse)
                    node = (
                        node.previousSibling().toElement()
                        if reverse
                        else node.nextSibling().toElement()
                    )
                    continue

                if node.attribute("objectName") not in (
                    "pinebooActionGroup",
                    "pinebooActionGroup_actiongroup_name",
                ):

                    action_name = node.attribute("objectName")
                    ac = ag.findChild(QtWidgets.QAction, action_name)

                    action_group = ag.findChild(
                        QtWidgets.QActionGroup, parent_element.attribute("objectName")
                    )
                    if action_group is not None:  # ¢heck if is visible
                        ac_orig = action_group.findChild(QtWidgets.QAction, action_name)
                        if ac_orig and not ac_orig.isVisible():
                            ac = None

                    if ac is not None:

                        if action_name.endswith("actiongroup_name"):
                            this_item = (
                                parent_item
                                if isinstance(parent_item, QtWidgets.QTreeWidgetItem)
                                else None
                            )
                        else:
                            this_item = QtWidgets.QTreeWidgetItem(parent_item)

                        if this_item is not None:
                            this_item.setIcon(0, ac.icon())
                            this_item.setText(1, action_name)
                            this_item.setText(0, node.attribute("text").replace("&", ""))

                self.buildListView(this_item, node, ag, reverse)

            node = node.previousSibling().toElement() if reverse else node.nextSibling().toElement()


class MainForm(QtWidgets.QMainWindow):
    """
    Create Eneboo-alike UI.
    """

    MAX_RECENT = 10
    app_ = None
    ag_menu_: Optional[QtWidgets.QActionGroup]
    ag_rec_: Optional[QtWidgets.QActionGroup]
    ag_mar_: Optional[QtWidgets.QActionGroup]
    dck_mod_: DockListView
    dck_rec_: DockListView
    dck_mar_: DockListView
    tw_: QtWidgets.QTabWidget
    w_: QtWidgets.QMainWindow
    # tw_corner = None  # deprecated
    act_sig_map_: QtCore.QSignalMapper
    initialized_mods_: List[str]
    main_widgets_: Dict[str, QtWidgets.QWidget] = {}
    debugLevel: int
    # lista_tabs_ = []

    def __init__(self) -> None:
        """Construct Eneboo-alike UI."""
        super().__init__()

        self.qsa_sys = systype.SysType()
        self.AQS = aqsobjectfactory.AQS
        self.ag_menu_ = None
        self.ag_rec_ = None
        self.ag_mar_ = None

    def eventFilter(self, o: QtCore.QObject, e: QtCore.QEvent) -> bool:
        """Process GUI events."""

        if isinstance(e, self.AQS.ContextMenu):
            if o == getattr(self.dck_mod_, "w_", None):
                return self.addMarkFromItem(self.dck_mod_.lw_.currentItem(), e.globalPos())
            elif o == getattr(self.dck_rec_, "w_", None):
                return self.addMarkFromItem(self.dck_rec_.lw_.currentItem(), e.globalPos())
            elif o == getattr(self.dck_mar_, "w_", None):
                return self.removeMarkFromItem(self.dck_mar_.lw_.currentItem(), e.globalPos())

            # pinebooMenu = self.w_.child("pinebooMenu")
            # pinebooMenu.exec_(e.globalPos)
            return True

        elif isinstance(e, self.AQS.Close):
            if isinstance(o, MainForm):
                self.w_.setDisabled(True)
                ret = self.exit()
                if not ret:
                    self.w_.setDisabled(False)
                    e.ignore()

                return True

            elif isinstance(o, QtWidgets.QDockWidget):
                cast(QtCore.pyqtSignal, o.topLevelChanged).emit(False)

        elif isinstance(e, self.AQS.Show):
            if isinstance(o, flformdb.FLFormDB):
                return True

        return False

    def createUi(self, ui_file: str) -> None:
        """Create UI from file path."""

        mng = application.PROJECT.conn_manager.managerModules()
        self.w_ = cast(QtWidgets.QMainWindow, mng.createUI(ui_file, None, self))
        self.w_.setObjectName("container")

    def exit(self) -> bool:
        """Process exit events."""
        res = qmessagebox.QMessageBox.information(
            "¿ Quiere salir de la aplicación ?",
            qmessagebox.QMessageBox.Yes,
            qmessagebox.QMessageBox.No,
            None,
            "Pineboo",
        )
        doExit = True if res == qmessagebox.QMessageBox.Yes else False
        if doExit:
            self.writeState()
            self.w_.removeEventFilter(self.w_)
            self.removeAllPages()

        return doExit

    def writeStateModule(self) -> None:
        """Write settings for modules."""

        pass

    def writeState(self) -> None:
        """Save settings."""

        w = self.w_

        if self.dck_rec_ is None:
            raise Exception("Recent dockListView is missing!")

        if self.dck_mod_ is None:
            raise Exception("Modules dockListView is missing!")

        if self.dck_mar_ is None:
            raise Exception("BookMarks dockListView is missing!")

        self.dck_mod_.writeState()
        self.dck_rec_.writeState()
        self.dck_mar_.writeState()

        settings = aqsobjectfactory.AQSettings()
        key = "MainWindow/"

        settings.writeEntry("%smaximized" % key, w.isMaximized())
        settings.writeEntry("%sx" % key, w.x())
        settings.writeEntry("%sy" % key, w.y())
        settings.writeEntry("%swidth" % key, w.width())
        settings.writeEntry("%sheight" % key, w.height())

        key += "%s/" % application.PROJECT.conn_manager.database()

        open_actions = []

        for i in range(self.tw_.count()):
            open_actions.append(cast(flformdb.FLFormDB, self.tw_.widget(i)).idMDI())

        settings.writeEntryList("%sopenActions" % key, open_actions)
        settings.writeEntry("%scurrentPageIndex" % key, self.tw_.currentIndex())

        recent_actions = []
        root_recent = self.dck_rec_.lw_.invisibleRootItem()
        count_recent = root_recent.childCount()
        for i in range(count_recent):
            recent_actions.append(root_recent.child(i).text(1))
        settings.writeEntryList("%srecentActions" % key, recent_actions)

        mark_actions = []
        root_mark = self.dck_mar_.lw_.invisibleRootItem()
        count_mark = root_mark.childCount()
        for i in range(count_mark):
            mark_actions.append(root_mark.child(i).text(1))
        settings.writeEntryList("%smarkActions" % key, mark_actions)

    def readState(self) -> None:
        """Read settings."""
        w = self.w_

        if self.dck_rec_ is None:
            raise Exception("Recent dockListView is missing!")

        if self.dck_mod_ is None:
            raise Exception("Modules dockListView is missing!")

        if self.dck_mar_ is None:
            raise Exception("BookMarks dockListView is missing!")

        self.dck_mod_.readState()
        self.dck_rec_.readState()
        self.dck_mar_.readState()

        settings = aqsobjectfactory.AQSettings()
        key = "MainWindow/"

        maximized = settings.readBoolEntry("%smaximized" % key)

        if not maximized:
            x = settings.readNumEntry("%sx" % key)
            y = settings.readNumEntry("%sy" % key)
            if self.qsa_sys.osName() == "MACX" and y < 20:
                y = 20
            w.move(x, y)
            w.resize(
                settings.readNumEntry("%swidth" % key, w.width()),
                settings.readNumEntry("%sheight" % key, w.height()),
            )
        else:
            w.showMaximized()

        self.loadTabs()

    def loadTabs(self) -> None:
        """Load tabs."""
        if self.ag_menu_:

            settings = aqsobjectfactory.AQSettings()
            key = "MainWindow/%s/" % application.PROJECT.conn_manager.database()

            open_actions = settings.readListEntry("%sopenActions" % key)
            i = 0

            if self.tw_ is None:
                raise Exception("tw_ is empty!")

            for i in range(self.tw_.count()):
                self.tw_.widget(i).close()

            for open_action in open_actions:
                action = cast(
                    QtWidgets.QAction, self.ag_menu_.findChild(QtWidgets.QAction, open_action)
                )
                if not action or not action.isVisible():
                    continue
                module_name = application.PROJECT.conn_manager.managerModules().idModuleOfFile(
                    "%s.ui" % action.objectName()
                )
                if module_name:
                    self.initModule(module_name)

                self.addForm(open_action, action.icon().pixmap(16, 16))

            idx = settings.readNumEntry("%scurrentPageIndex" % key)
            if idx > 0 and idx < len(self.tw_):
                self.tw_.setCurrentWidget(self.tw_.widget(idx))

            recent_actions = settings.readListEntry("%srecentActions" % key)
            for recent in reversed(recent_actions):
                self.addRecent(
                    cast(QtWidgets.QAction, self.ag_menu_.findChild(QtWidgets.QAction, recent))
                )

            mark_actions = settings.readListEntry("%smarkActions" % key)
            for mark in reversed(mark_actions):
                self.addMark(
                    cast(QtWidgets.QAction, self.ag_menu_.findChild(QtWidgets.QAction, mark))
                )

    def init(self) -> None:
        """Initialize UI."""
        self.w_.statusBar().hide()
        self.main_widgets_ = {}
        self.initialized_mods_ = []
        self.act_sig_map_ = QtCore.QSignalMapper(self.w_)
        self.act_sig_map_.setObjectName("pinebooActSignalMap")
        self.act_sig_map_.mapped[str].connect(self.triggerAction)  # type: ignore
        self.initTabWidget()
        self.initHelpMenu()
        self.initConfigMenu()
        self.initTextLabels()
        self.initDocks()
        self.initEventFilter()

    def initFromWidget(self, w: "QtWidgets.QMainWindow") -> None:
        """Initialize UI from a base widget."""
        self.w_ = w
        self.main_widgets_ = {}
        self.initialized_mods_ = []
        self.act_sig_map_ = QtCore.QSignalMapper(self.w_)
        self.act_sig_map_.setObjectName("pinebooActSignalMap")
        self.tw_ = cast(QtWidgets.QTabWidget, w.findChild(QtWidgets.QTabWidget, "tabWidget"))
        self.agMenu_ = cast(
            QtWidgets.QActionGroup, w.findChild(QtWidgets.QActionGroup, "pinebooActionGroup")
        )
        self.dck_mod_ = DockListView()
        self.dck_mod_.initFromWidget(
            cast(
                QtWidgets.QDockWidget,
                self.w_.findChild(QtWidgets.QDockWidget, "pinebooDockModulesListView"),
            )
        )
        self.dck_rec_ = DockListView()
        self.dck_rec_.initFromWidget(
            cast(
                QtWidgets.QDockWidget,
                self.w_.findChild(QtWidgets.QDockWidget, "pinebooDockRecentListView"),
            )
        )
        self.dck_mar_ = DockListView()
        self.dck_mar_.initFromWidget(
            cast(
                QtWidgets.QDockWidget,
                self.w_.findChild(QtWidgets.QDockWidget, "pinebooDockMarksListView"),
            )
        )
        self.initEventFilter()

    def initEventFilter(self) -> None:
        """Install event filters."""
        # w = self.w_
        # self.w_.eventFilterFunction = (
        #    "flapplication.flapplication.aqApp.Script.mainWindow_.eventFilter"
        # )

        # self.w_.allow_events = [self.AQS.ContextMenu, self.AQS.Close]

        self.w_.installEventFilter(self)
        if self.dck_mod_ and self.dck_mod_.w_:
            self.dck_mod_.w_.installEventFilter(self)
        if self.dck_rec_ and self.dck_rec_.w_:
            self.dck_rec_.w_.installEventFilter(self)
        if self.dck_mar_ and self.dck_mar_.w_:
            self.dck_mar_.w_.installEventFilter(self)

    def initModule(self, module: str) -> None:
        """Initialize main module."""
        if module in self.main_widgets_:
            mwi = self.main_widgets_[module]
            mwi.setObjectName(module)
            flapplication.aqApp.setObjectName(module)
            mwi.show()

        if module not in self.initialized_mods_:
            self.initialized_mods_.append(module)
            flapplication.aqApp.call("%s.iface.init" % module, [], None, False)

        mng = flapplication.aqApp.db().managerModules()
        mng.setActiveIdModule(module)

    def removeCurrentPage(self, n: Optional[int] = None) -> None:
        """Close tab."""
        if self.tw_ is None:
            raise Exception("Not initialized.")
        if n is None:
            widget = self.tw_.currentWidget()
        else:
            widget = self.tw_.widget(n)

        if not widget:
            return

        if widget.__class__.__name__ == "FLFormDB":
            widget.close()

    def removeAllPages(self) -> None:
        """Close all tabs."""
        if self.tw_ is None:
            raise Exception("Not initialized.")

        # if len(tw):
        #    self.tw_corner.hide()

        for i in range(self.tw_.count()):
            self.tw_.widget(i).close()

    def addForm(self, action_name: str, icono: "QtGui.QPixmap") -> None:
        """Add new tab."""

        if self.tw_ is None:
            raise Exception("tw_ is empty!")

        for i in range(self.tw_.count()):
            form = self.tw_.widget(i)
            if isinstance(form, flformdb.FLFormDB):
                if form.action().name() == action_name:
                    self.tw_.widget(i).close()

        fm = aqsobjectfactory.AQFormDB(action_name, self.tw_)
        fm.setMainWidget()
        if not fm.mainWidget():
            return
        if self.ag_menu_:
            self.tw_.addTab(
                fm,
                cast(
                    QtWidgets.QAction, self.ag_menu_.findChild(QtWidgets.QAction, action_name)
                ).icon(),
                fm.windowTitle(),
            )
        fm.setIdMDI(action_name)
        fm.show()

        self.tw_.setCurrentWidget(fm)
        fm.installEventFilter(self.w_)

    def addRecent(self, action: QtWidgets.QAction) -> None:
        """Add new entry to recent list."""
        if not action:
            return

        if not self.ag_rec_:
            self.ag_rec_ = QtWidgets.QActionGroup(self.w_)

        check_max = True

        new_ag_rec_ = QtWidgets.QActionGroup(self.w_)
        new_ag_rec_.setObjectName("pinebooAgRec")

        self.cloneAction(action, new_ag_rec_)

        for ac in self.ag_rec_.actions():
            if ac.objectName() == action.objectName():
                check_max = False
                continue

            self.cloneAction(ac, new_ag_rec_)

        self.ag_rec_ = new_ag_rec_
        if self.dck_rec_ is None:
            return
        lw = self.dck_rec_.lw_
        if lw is None:
            return
        if check_max and lw.topLevelItemCount() >= self.MAX_RECENT:
            last_name = lw.topLevelItem(lw.topLevelItemCount() - 1).text(1)
            ac = cast(QtWidgets.QAction, self.ag_rec_.findChild(QtWidgets.QAction, last_name))
            if ac:
                self.ag_rec_.removeAction(ac)
                del ac

        self.dck_rec_.update(self.ag_rec_)

    def addMark(self, action: QtWidgets.QAction) -> None:
        """Add new entry to Mark list."""
        if not action:
            return

        if not self.ag_mar_:
            self.ag_mar_ = QtWidgets.QActionGroup(self.w_)

        new_ag_mar = QtWidgets.QActionGroup(self.w_)
        new_ag_mar.setObjectName("pinebooAgMar")

        for ac in self.ag_mar_.actions():
            if ac.objectName() == action.objectName():
                continue

            self.cloneAction(ac, new_ag_mar)

        self.cloneAction(action, new_ag_mar)

        self.ag_mar_ = new_ag_mar
        if self.dck_mar_:
            self.dck_mar_.update(self.ag_mar_, True)

    def addMarkFromItem(self, item: Any, pos: QtCore.QPoint) -> bool:
        """Add a new item to the Bookmarks docket."""

        if not item:
            return False

        if item.text(1) is None:
            return True

        popMenu = QtWidgets.QMenu()
        popMenu.move(pos)
        popMenu.addAction(self.tr("Añadir Marcadores"))
        res = popMenu.exec_()
        if res and self.ag_menu_ is not None:
            ac = cast(QtWidgets.QAction, self.ag_menu_.findChild(QtWidgets.QAction, item.text(1)))
            if ac and not ac.objectName().endswith("actiongroup_name"):
                self.addMark(ac)

        return True

    def removeMarkFromItem(self, item: Any, pos: QtCore.QPoint) -> bool:
        """Add a new item to the Bookmarks docket."""
        if not item or not self.ag_mar_ or self.dck_mar_ is None:
            return False
        if self.dck_mar_.lw_ is None or self.dck_mar_.lw_.invisibleRootItem().childCount() == 0:
            return False
        if item.text(1) is None:
            return True

        popMenu = QtWidgets.QMenu()
        popMenu.move(pos)
        popMenu.addAction(self.tr("Eliminar Marcador"))
        res = popMenu.exec_()
        if res:
            ac = cast(QtWidgets.QAction, self.ag_mar_.findChild(QtWidgets.QAction, item.text(1)))
            if ac and self.ag_mar_:
                self.ag_mar_.removeAction(ac)
                del ac
                self.dck_mar_.update(self.ag_mar_)

        return True

    def updateMenu(self, action_group: "QtWidgets.QActionGroup", parent: Any) -> None:
        """Update the modules menu with the available options."""
        object_list = cast(
            List[Union[QtWidgets.QAction, QtWidgets.QActionGroup]], action_group.children()
        )
        for obj_ in object_list:
            o_name = obj_.objectName()
            if not getattr(obj_, "isVisible", None) or not obj_.isVisible():
                continue
            if isinstance(obj_, QtWidgets.QActionGroup):
                new_parent = parent

                ac_obj = cast(
                    QtWidgets.QAction,
                    obj_.findChild(QtWidgets.QAction, "%s_actiongroup_name" % o_name),
                )
                if ac_obj:
                    if not o_name.endswith("Actions") or o_name.endswith("MoreActions"):
                        new_parent = parent.addMenu(ac_obj.icon(), ac_obj.text())
                        new_parent.triggered.connect(ac_obj.trigger)

                self.updateMenu(obj_, new_parent)
                continue

            elif o_name.endswith("_actiongroup_name"):
                continue

            elif o_name == "separator":
                a_ = parent.addAction("")
                a_.setSeparator(True)
            else:
                if isinstance(obj_, QtWidgets.QAction):
                    if self.ag_menu_:
                        obj_real = cast(
                            QtWidgets.QAction,
                            self.ag_menu_.findChild(QtWidgets.QAction, obj_.objectName()),
                        )
                        if obj_real is not None:
                            obj_ = obj_real  # Fix invalid QActions
                    a_ = parent.addAction(obj_.text())
                    a_.setIcon(obj_.icon())
                    a_.triggered.connect(obj_.trigger)
                else:
                    continue

            a_.setObjectName(o_name)

    def updateMenuAndDocks(self) -> None:
        """Update the main menu and dockers."""
        # FIXME: Duplicated piece of code
        self.updateActionGroup()
        pinebooMenu = cast(QtWidgets.QMenu, self.w_.findChild(QtWidgets.QMenu, "menuPineboo"))
        pinebooMenu.clear()

        if self.ag_menu_ is None:
            raise Exception("ag_menu_ is empty!")

        self.updateMenu(self.ag_menu_, pinebooMenu)

        flapplication.aqApp.setMainWidget(self.w_)

        if self.ag_menu_ is None:
            raise Exception("ag_menu_ is empty!")

        if not self.ag_rec_:
            self.ag_rec_ = QtWidgets.QActionGroup(self.w_)

        if not self.ag_mar_:
            self.ag_mar_ = QtWidgets.QActionGroup(self.w_)

        if self.dck_rec_ is None:
            raise Exception("Recent dockListView is missing!")

        if self.dck_mod_ is None:
            raise Exception("Modules dockListView is missing!")

        if self.dck_mar_ is None:
            raise Exception("BookMarks dockListView is missing!")

        self.dck_mod_.update(self.ag_menu_)
        self.dck_rec_.update(self.ag_rec_)
        self.dck_mar_.update(self.ag_mar_)
        cast(
            QtWidgets.QAction, self.w_.findChild(QtWidgets.QAction, "aboutQtAction")
        ).triggered.connect(flapplication.aqApp.aboutQt)
        cast(
            QtWidgets.QAction, self.w_.findChild(QtWidgets.QAction, "aboutPinebooAction")
        ).triggered.connect(flapplication.aqApp.aboutPineboo)
        cast(
            QtWidgets.QAction, self.w_.findChild(QtWidgets.QAction, "fontAction")
        ).triggered.connect(flapplication.aqApp.chooseFont)
        cast(QtWidgets.QAction, self.w_.findChild(QtWidgets.QMenu, "style")).triggered.connect(
            flapplication.aqApp.showStyles
        )
        cast(
            QtWidgets.QAction, self.w_.findChild(QtWidgets.QAction, "helpIndexAction")
        ).triggered.connect(flapplication.aqApp.helpIndex)
        cast(
            QtWidgets.QAction, self.w_.findChild(QtWidgets.QAction, "urlPinebooAction")
        ).triggered.connect(flapplication.aqApp.urlPineboo)

    def updateActionGroup(self) -> None:
        """Update the available actions."""

        if self.ag_menu_:
            list_ = self.ag_menu_.children()
            for obj in list_:
                if isinstance(obj, QtWidgets.QAction):
                    self.ag_menu_.removeAction(obj)
                    del obj

            self.ag_menu_.deleteLater()
            del self.ag_menu_

        self.ag_menu_ = QtWidgets.QActionGroup(self.w_)
        self.ag_menu_.setObjectName("pinebooActionGroup")
        ac_name = QtWidgets.QAction(self.ag_menu_)
        ac_name.setObjectName("pinebooActionGroup_actiongroup_name")
        ac_name.setText(self.tr("Menú"))

        mng = flapplication.aqApp.db().managerModules()
        areas = mng.listIdAreas()

        if self.act_sig_map_ is None:
            raise Exception("self.act_sig_map_ is empty!")

        for area in areas:
            if not self.qsa_sys.isDebuggerEnabled() and area == "sys":
                break
            ag = QtWidgets.QActionGroup(self.ag_menu_)
            ag.setObjectName(area)
            ag_action = QtWidgets.QAction(ag)
            ag_action.setObjectName("%s_actiongroup_name" % ag.objectName())
            ag_action.setText(mng.idAreaToDescription(ag.objectName()))
            ag_action.setIcon(QtGui.QIcon(self.AQS.pixmap_fromMimeSource("folder.png")))

            modules = mng.listIdModules(ag.objectName())
            for module in modules:
                if module == "sys" and self.qsa_sys.isUserBuild():
                    continue
                ac: Union[QtWidgets.QAction, QtWidgets.QActionGroup] = QtWidgets.QActionGroup(ag)
                ac.setObjectName(module)
                if self.qsa_sys.isQuickBuild():
                    if module == "sys":
                        continue
                actions = self.widgetActions("%s.ui" % ac.objectName(), ac)

                if not actions:
                    # ac.setObjectName("")
                    ac.deleteLater()
                    ac = QtWidgets.QAction(ag)
                    if ac:
                        ac.setObjectName(module)

                ac_action = QtWidgets.QAction(ac)
                ac_action.setObjectName("%s_actiongroup_name" % ac.objectName())
                ac_action.setText(mng.idModuleToDescription(ac.objectName()))
                ac_action.setIcon(self.iconSet16x16(mng.iconModule(ac.objectName())))

                ac_action.triggered.connect(self.act_sig_map_.map)
                self.act_sig_map_.setMapping(
                    ac_action, "triggered():initModule():%s_actiongroup_name" % ac.objectName()
                )
                if ac.objectName() == "sys" and ag.objectName() == "sys":
                    if self.qsa_sys.isDebuggerMode():
                        staticLoad = QtWidgets.QAction(ag)
                        staticLoad.setObjectName("staticLoaderSetupAction")
                        staticLoad.setText(self.tr("Configurar carga estática"))
                        staticLoad.setIcon(
                            QtGui.QIcon(self.AQS.pixmap_fromMimeSource("folder_update.png"))
                        )
                        staticLoad.triggered.connect(self.act_sig_map_.map)
                        self.act_sig_map_.setMapping(
                            staticLoad,
                            "triggered():staticLoaderSetup():%s" % staticLoad.objectName(),
                        )

                        reInit = QtWidgets.QAction(ag)
                        reInit.setObjectName("reinitAction")
                        reInit.setText(self.tr("Recargar scripts"))
                        reInit.setIcon(QtGui.QIcon(self.AQS.pixmap_fromMimeSource("reload.png")))
                        reInit.triggered.connect(self.act_sig_map_.map)
                        self.act_sig_map_.setMapping(
                            reInit, "triggered():reinit():%s" % reInit.objectName()
                        )

        shConsole = QtWidgets.QAction(self.ag_menu_)
        shConsole.setObjectName("shConsoleAction")
        shConsole.setText(self.tr("Mostrar Consola de mensajes"))
        shConsole.setIcon(QtGui.QIcon(self.AQS.pixmap_fromMimeSource("consola.png")))
        shConsole.triggered.connect(self.act_sig_map_.map)
        self.act_sig_map_.setMapping(
            shConsole, "triggered():shConsole():%s" % shConsole.objectName()
        )

        exit = QtWidgets.QAction(self.ag_menu_)
        exit.setObjectName("exitAction")
        exit.setText(self.tr("&Salir"))
        exit.setIcon(QtGui.QIcon(self.AQS.pixmap_fromMimeSource("exit.png")))
        exit.triggered.connect(self.act_sig_map_.map)
        self.act_sig_map_.setMapping(exit, "triggered():exit():%s" % exit.objectName())

    def initTabWidget(self) -> None:
        """Initialize the TabWidget."""
        self.tw_ = cast(QtWidgets.QTabWidget, self.w_.findChild(QtWidgets.QTabWidget, "tabWidget"))
        if self.tw_ is None:
            raise Exception("no tabWidget found")
        self.tw_.setTabsClosable(True)
        self.tw_.tabCloseRequested[int].connect(self.removeCurrentPage)  # type: ignore
        self.tw_.removeTab(0)
        """
        tb = self.tw_corner = QToolButton(tw, "tabWidgetCorner")
        tb.autoRaise = False
        tb.setFixedSize(16, 16)
        tb.setIconSet(self.iconset16x16(self.AQS.pixmap_fromMimeSource("file_close.png")))
        tb.clicked.connect(self.removeCurrentPage)
        tw.setCornerWidget(tb, self.AQS.TopRight)
        self.AQS.toolTip_add(tb, self.tr("Cerrar pestaña"))
        tb.hide()
        """

    def initHelpMenu(self) -> None:
        """Initialize help menu."""

        aboutQt = cast(QtWidgets.QAction, self.w_.findChild(QtWidgets.QAction, "aboutQtAction"))
        aboutQt.setIcon(self.iconSet16x16(self.AQS.pixmap_fromMimeSource("aboutqt.png")))
        # aboutQt.triggered.connect(flapplication.aqApp.aboutQt)

        aboutPineboo = cast(
            QtWidgets.QAction, self.w_.findChild(QtWidgets.QAction, "aboutPinebooAction")
        )
        aboutPineboo.setIcon(
            self.iconSet16x16(self.AQS.pixmap_fromMimeSource("pineboo-logo-32.png"))
        )
        # aboutPineboo.triggered.connect(flapplication.aqApp.aboutPineboo)

        helpIndex = cast(QtWidgets.QAction, self.w_.findChild(QtWidgets.QAction, "helpIndexAction"))
        helpIndex.setIcon(self.iconSet16x16(self.AQS.pixmap_fromMimeSource("help_index.png")))
        # helpIndex.triggered.connect(flapplication.aqApp.helpIndex)

        urlPineboo = cast(
            QtWidgets.QAction, self.w_.findChild(QtWidgets.QAction, "urlPinebooAction")
        )
        urlPineboo.setIcon(self.iconSet16x16(self.AQS.pixmap_fromMimeSource("pineboo-logo-32.png")))
        # urlPineboo.triggered.connect(flapplication.aqApp.urlPineboo)

    def initConfigMenu(self) -> None:
        """Initialize config menu."""
        font = cast(QtWidgets.QAction, self.w_.findChild(QtWidgets.QAction, "fontAction"))
        font.setIcon(self.iconSet16x16(self.AQS.pixmap_fromMimeSource("font.png")))
        # font.triggered.connect(flapplication.aqApp.chooseFont)

        style = cast(QtWidgets.QMenu, self.w_.findChild(QtWidgets.QMenu, "style"))

        flapplication.aqApp.initStyles()
        style.setIcon(self.iconSet16x16(self.AQS.pixmap_fromMimeSource("estilo.png")))
        # style.triggered.connect(flapplication.aqApp.showStyles)

    def initTextLabels(self) -> None:
        """Initialize the tags in the mainForm base."""

        text_label = cast(QtWidgets.QLabel, self.w_.findChild(QtWidgets.QLabel, "tLabel"))
        text_label2 = cast(QtWidgets.QLabel, self.w_.findChild(QtWidgets.QLabel, "tLabel2"))
        texto = aqsobjectfactory.AQUtil.sqlSelect("flsettings", "valor", "flkey='verticalName'")
        if texto and texto != "False":
            text_label.setText(texto)

        if aqsobjectfactory.AQUtil.sqlSelect("flsettings", "valor", "flkey='PosInfo'") == "True":
            text_ = "%s@%s" % (self.qsa_sys.nameUser(), self.qsa_sys.nameBD())
            if self.qsa_sys.osName() == "MACX":
                text_ += "     "

            text_label2.setText(text_)

    def initDocks(self) -> None:
        """Initialize the 3 available docks."""

        self.dck_mar_ = DockListView(self.w_, "pinebooDockMarks", self.tr("Marcadores"))
        self.w_.addDockWidget(self.AQS.DockLeft, self.dck_mar_.w_)
        self.dck_rec_ = DockListView(self.w_, "pinebooDockRecent", self.tr("Recientes"))
        self.w_.addDockWidget(self.AQS.DockLeft, self.dck_rec_.w_)
        self.dck_mod_ = DockListView(self.w_, "pinebooDockModules", self.tr("Módulos"))
        self.w_.addDockWidget(self.AQS.DockLeft, self.dck_mod_.w_)

        windowMenu = cast(QtWidgets.QMenu, self.w_.findChild(QtWidgets.QMenu, "windowMenu"))
        sub_menu = windowMenu.addMenu(self.tr("&Vistas"))

        docks = cast(List[DockListView], self.w_.findChildren(DockListView))
        for dock in docks:
            ac = sub_menu.addAction(dock.w_.windowTitle())
            ac.setCheckable(True)
            # FIXME: Comprobar si estoy visible o no
            # ac.setChecked(dock.w_.isVisible())
            dock.set_visible.connect(ac.setChecked)
            ac.triggered.connect(dock.change_state)
            cast(QtCore.pyqtSignal, dock.w_.topLevelChanged).connect(ac.setChecked)
            # dock.w_.Close.connect(ac.setChecked)

    def cloneAction(self, act, parent) -> Any:
        """Clone one action into another."""

        ac = QtWidgets.QAction(parent)
        ac.setObjectName(act.objectName())
        ac.setText(act.text())
        ac.setStatusTip(act.statusTip())
        ac.setToolTip(act.toolTip())
        ac.setWhatsThis(act.whatsThis())
        ac.setEnabled(act.isEnabled())
        ac.setVisible(act.isVisible())
        ac.triggered.connect(act.trigger)
        ac.toggled.connect(act.toggle)
        if not act.icon().isNull():
            ac.setIcon(self.iconSet16x16(act.icon().pixmap(16, 16)))

        return ac

    def addWidgetActions(self, node, action_group, wi) -> None:
        """Add actions belonging to a widget."""
        actions = node.elementsByTagName("action")
        if len(actions) == 0:
            actions = node.elementsByTagName("addaction")
        hide_group = True
        for i in range(len(actions)):
            item = actions.at(i).toElement()
            action_widget = wi.findChild(QtWidgets.QAction, item.attribute("name"))
            if action_widget is None:
                continue

            if action_widget.isVisible():
                hide_group = False

            prev = item.previousSibling().toElement()
            if not prev.isNull() and prev.tagName() == "separator":
                sep_ = action_group.addAction("separator")
                sep_.setObjectName("separator")
                sep_.setSeparator(True)
                # actGroup.addSeparator()

            self.cloneAction(action_widget, action_group)

        if hide_group:
            action_group.setVisible(False)

    def widgetActions(self, ui_file: str, parent: Any) -> Any:
        """Collect the actions provided by a widget."""
        mng = flapplication.aqApp.db().managerModules()
        doc = QtXml.QDomDocument()
        cc = mng.contentCached(ui_file)
        if not cc or not doc.setContent(cc):
            if cc:
                logger.warning("No se ha podido cargar %s" % (ui_file))
            return None

        w = mng.createUI(ui_file)
        if w is None:
            raise Exception("Failed to create UI from %r" % ui_file)
        if not isinstance(w, QtWidgets.QMainWindow):
            if w:
                self.main_widgets_[w.objectName()] = w

            return None

        w.setObjectName(parent.objectName())

        if flapplication.aqApp.acl_:
            flapplication.aqApp.acl_.process(w)

        # flapplication.aqApp.setMainWidget(w)

        # if (self.qsa_sys.isNebulaBuild()):
        #    w.show()

        w.hide()

        reduced = settings.config.value("ebcomportamiento/ActionsMenuRed", False)
        root = doc.documentElement().toElement()
        ag = QtWidgets.QActionGroup(parent)
        ag.setObjectName("%sActions" % parent.objectName())

        if root.attribute("version") == "3.3":
            bars = root.namedItem("toolbars").toElement()
            menu = root.namedItem("menubar").toElement()
            items = menu.elementsByTagName("item")

        else:
            widgets = root.elementsByTagName("widget")
            for widget in range(widgets.size()):
                if widgets.item(widget).toElement().attribute("class") == "QToolBar":
                    bars = widgets.item(widget).toElement()
                elif widgets.item(widget).toElement().attribute("class") == "QMenuBar":
                    menu_ = widgets.item(widget)
                    items = menu_.toElement().elementsByTagName("widget")

        if not reduced:
            self.addWidgetActions(bars, ag, w)

        if len(items) > 0:
            if not reduced:
                sep_ = ag.addAction("separator")
                sep_.setObjectName("separator")
                sep_.setSeparator(True)

                menu_ag = QtWidgets.QActionGroup(ag)
                menu_ag.setObjectName("%sMore" % ag.objectName())
                menu_ag_name = QtWidgets.QAction(menu_ag)
                menu_ag_name.setObjectName("%s_actiongroup_name" % ag.objectName())
                menu_ag_name.setText(self.tr("Mas"))
                menu_ag_name.setIcon(QtGui.QIcon(self.AQS.pixmap_fromMimeSource("plus.png")))
            else:
                menu_ag = QtWidgets.QActionGroup(ag)
                menu_ag.setObjectName(ag.objectName())

            for i in range(len(items)):
                itn = items.at(i).toElement()
                if itn.parentNode().toElement().tagName() == "item":
                    continue

                sub_menu_ag = QtWidgets.QActionGroup(menu_ag)

                if root.attribute("version") == "3.3":
                    text = itn.attribute("text")
                else:
                    text = itn.text()

                if not reduced:
                    sub_menu_ag.setObjectName("%sActions" % menu_ag.objectName())

                else:
                    sub_menu_ag.setObjectName(text)

                sub_menu_ag_name = QtWidgets.QAction(sub_menu_ag)
                sub_menu_ag_name.setObjectName("%s_actiongroup_name" % sub_menu_ag.objectName())
                sub_menu_ag_name.setText(self.qsa_sys.toUnicode(text, "iso-8859-1"))

                self.addWidgetActions(itn, sub_menu_ag, w)

        conns = root.namedItem("connections").toElement()
        connections = conns.elementsByTagName("connection")
        mapped_list: List[str] = []
        for i in range(connections.length()):
            itn = connections.at(i).toElement()
            sender = itn.namedItem("sender").toElement().text()
            ac = ag.findChild(QtWidgets.QAction, sender)
            if ac:

                signal = itn.namedItem("signal").toElement().text()
                if signal in ["activated()", "triggered()"]:
                    signal_fix = "triggered"
                    signal = "triggered()"

                slot = itn.namedItem("slot").toElement().text()
                if self.act_sig_map_ is not None:
                    map_name = "%s:%s:%s" % (signal, slot, ac.objectName())
                    if map_name not in mapped_list:
                        getattr(ac, signal_fix).connect(self.act_sig_map_.map)
                        self.act_sig_map_.setMapping(ac, map_name)
                        mapped_list.append(map_name)
                # getattr(ac, signal).connect(self.act_sig_map_.map)
                # ac.triggered.connect(self.triggerAction)

                # print("Guardando señales  %s:%s:%s de %s" % (signal, slot, ac.name, ac))

        # flapplication.aqApp.setMainWidget(None)
        w.close()
        return ag

    def iconSet16x16(self, pix: "QtGui.QPixmap") -> "QtGui.QIcon":
        """Reduce the size of a pixmap to 16 * 16."""

        p_ = QtGui.QPixmap(pix)
        # img_ = p_.convertToImage()
        # img_.smoothScale(16, 16)
        # ret = QtGui.QIconSet(QPixmap(img_))
        img_ = QtGui.QImage(p_)
        if not img_.isNull():
            img_ = img_.scaled(16, 16)
        ret = QtGui.QIcon(QtGui.QPixmap(img_))
        return ret

    def show(self) -> None:
        """Show the mainform."""

        super(MainForm, self).show()
        self.activateWindow()

    def initScript(self) -> None:
        """Startup process."""

        flapplication.aqApp.main_widget_ = self

        mw = self
        mw.createUi(utils_base.filedir("plugins/mainform/eneboo/mainform.ui"))

        mw.init()

        mw.updateMenuAndDocks()
        mw.initModule("sys")
        mw.show()
        mw.readState()

    def reinitSript(self) -> None:
        """Re-start process."""
        main_wid = flapplication.aqApp.mainWidget() if self.w_ is None else self.w_
        if main_wid is None or main_wid.objectName() != "container":
            return

        mw = self
        # mw.initFormWidget(main_wid)
        mw.writeState()
        mw.removeAllPages()
        cast(
            QtWidgets.QAction, mw.w_.findChild(QtWidgets.QAction, "aboutQtAction")
        ).triggered.disconnect(flapplication.aqApp.aboutQt)
        cast(
            QtWidgets.QAction, mw.w_.findChild(QtWidgets.QAction, "aboutPinebooAction")
        ).triggered.disconnect(flapplication.aqApp.aboutPineboo)
        mw.updateMenuAndDocks()
        mw.initModule("sys")
        mw.readState()

    def triggerAction(self, signature: str) -> None:
        """Start a process according to a given pattern."""
        mw = self
        sgt = signature.split(":")
        # ok = True
        if mw.ag_menu_ is None:
            raise Exception("Not initialized")
        ac: Optional[QtWidgets.QAction] = cast(
            QtWidgets.QAction, mw.ag_menu_.findChild(QtWidgets.QAction, sgt[2])
        )
        if ac is None:
            logger.debug("triggerAction: Action not Found: %s" % signature)
            return

        signal = sgt[0]
        if signal == "triggered()":
            if not ac.isVisible() or not ac.isEnabled():
                return
        else:
            logger.debug("triggerAction: Unhandled signal: %s" % signature)
            return

        fn_ = sgt[1]
        if fn_ == "initModule()":
            mw.initModule(ac.objectName().replace("_actiongroup_name", ""))

        elif fn_ == "openDefaultForm()":
            mw.addForm(ac.objectName(), ac.icon().pixmap(16, 16))
            mw.addRecent(ac)

        elif fn_ == "execDefaultScript()":
            mw.addRecent(ac)
            flapplication.aqApp.execMainScript(ac.objectName())

        elif fn_ == "loadModules()":
            self.qsa_sys.loadModules()

        elif fn_ == "exportModules()":
            self.qsa_sys.exportModules()

        elif fn_ == "importModules()":
            self.qsa_sys.importModules()

        elif fn_ == "updatePineboo()":
            self.qsa_sys.updatePineboo()

        elif fn_ == "staticLoaderSetup()":
            flapplication.aqApp.staticLoaderSetup()

        elif fn_ == "reinit()":
            self.qsa_sys.reinit()

        elif fn_ == "mrProper()":
            self.qsa_sys.Mr_Proper()

        elif fn_ == "shConsole()":
            flapplication.aqApp.showConsole()

        elif fn_ == "exit()":
            self.close()

        else:
            logger.debug("tiggerAction: Unhandled slot : %s" % signature)

    @classmethod
    def setDebugLevel(self, q: int) -> None:
        """Specify debug level."""

        self.debugLevel = q

    def child(self, name: str) -> Optional[QtCore.QObject]:
        """Find a child widget."""

        return self.w_.findChild(QtWidgets.QWidget, name)

    def setCaptionMainWidget(self, value) -> None:
        """Set application title."""

        self.setWindowTitle("Pineboo %s - %s" % (application.PROJECT.version, value))


mainWindow: MainForm
# mainWindow = MainForm()
