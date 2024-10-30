#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

"""Doc"""

import sys

sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import enum
import logging

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.const import DATA_DIR, DOWNLOAD_DIR
from avin.core import TinkoffData
from avin.gui.custom import Font, Icon, Palette, Spacer
from avin.gui.data_moex import MoexMenu
from avin.gui.data_tinkoff import TinkoffMenu
from avin.utils import Cmd

logger = logging.getLogger("LOGGER")


class ToolBar(QtWidgets.QToolBar):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__createMenu()
        self.__configButtons()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setIconSize(QtCore.QSize(32, 32))
        p = self.palette()
        p.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#484848"))
        self.setPalette(p)
        self.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.btn_moex = QtWidgets.QToolButton()
        self.btn_tinkoff = QtWidgets.QToolButton()
        self.addWidget(self.btn_moex)
        self.addWidget(self.btn_tinkoff)
        self.addWidget(Spacer(self))

    # }}}
    def __createMenu(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu_moex = MoexMenu(parent=self.btn_moex)
        self.menu_tinkoff = TinkoffMenu(parent=self.btn_tinkoff)

    # }}}
    def __configButtons(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__configButtons()")
        # self.btn_moex.setContentsMargins(0, 0, 0, 0)
        self.btn_moex.setText("MOEX")
        self.btn_moex.setMenu(self.menu_moex)
        self.btn_moex.setPopupMode(
            QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
        )
        # self.btn_tinkoff.setContentsMargins(0, 0, 0, 0)
        self.btn_tinkoff.setText("Tinkoff")
        self.btn_tinkoff.setMenu(self.menu_tinkoff)
        self.btn_tinkoff.setPopupMode(
            QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
        )


# }}}
# }}}
class IData(QtWidgets.QTreeWidgetItem):  # {{{
    def __init__(self, name: str, path: str, parent=None):  # {{{
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        if Cmd.isFile(path):
            self.__createFileItem(name, path)
        elif Cmd.isDir(path):
            self.__createDirItem(name, path)
        types = (
            Tree.Type.DIR,
            Tree.Type.DATA,
            Tree.Type.TINKOFF,
            Tree.Type.ANALYTIC,
        )
        if self.type in types:
            self.__createChilds()

    # }}}
    def __createChilds(self):  # {{{
        # logger.debug(f"{self.__class__.__name__}.__createChilds()")
        dir_path = self.path
        dirs_files = Cmd.contents(dir_path, full_path=True)
        for path in dirs_files:
            name = Cmd.name(path)
            item = IData(name, path)
            self.addChild(item)

    # }}}
    def __createDirItem(self, name: str, path: str):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createDirItem()")
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsAutoTristate
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        types = {
            "analytic": Tree.Type.ANALYTIC,
            "1M": Tree.Type.DATA,
            "5M": Tree.Type.DATA,
            "1H": Tree.Type.DATA,
            "D": Tree.Type.DATA,
        }
        self.__type = types.get(name, Tree.Type.DIR)
        self.setIcon(Tree.Column.Name, Icon.DIR)
        self.setText(Tree.Column.Name, name)
        self.setText(Tree.Column.Type, self.__type.name.lower())
        self.setText(Tree.Column.Path, path)

    # }}}
    def __createFileItem(self, name: str, path: str):  # {{{
        # logger.debug(f"{self.__class__.__name__}.__createFileItem()")
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsAutoTristate
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(Tree.Column.Name, name)
        self.setText(Tree.Column.Path, path)
        if name == "asset":
            self.__type = Tree.Type.ASSET
            self.setIcon(Tree.Column.Name, Icon.ASSET)
            self.setText(Tree.Column.Type, Tree.Type.ASSET.name.lower())
        elif name == "timeframe":
            self.__type = Tree.Type.TIMEFRAME
            self.setIcon(Tree.Column.Name, Icon.TIMEFRAME)
            self.setText(Tree.Column.Type, Tree.Type.TIMEFRAME.name.lower())
        elif path.endswith(".csv"):
            self.__type = Tree.Type.CSV
            self.setIcon(Tree.Column.Name, Icon.CSV)
            self.setText(Tree.Column.Type, Tree.Type.CSV.name.lower())
        elif path.endswith(".json"):
            self.__type = Tree.Type.JSON
            self.setIcon(Tree.Column.Name, Icon.JSON)
            self.setText(Tree.Column.Type, Tree.Type.JSON.name.lower())
        elif path.endswith(".zip"):
            self.__type = Tree.Type.ARCHIVE
            self.setIcon(Tree.Column.Name, Icon.ARCHIVE)
            self.setText(Tree.Column.Type, Tree.Type.ARCHIVE.name.lower())
        elif path.endswith(".sh"):
            self.__type = Tree.Type.SCRIPT
            self.setIcon(Tree.Column.Name, Icon.SCRIPT)
            self.setText(Tree.Column.Type, Tree.Type.SCRIPT.name.lower())
        elif path.endswith(".txt"):
            self.__type = Tree.Type.TXT
            self.setIcon(Tree.Column.Name, Icon.TXT)
            self.setText(Tree.Column.Type, Tree.Type.TXT.name.lower())
        else:
            self.__type = Tree.Type.FILE
            self.setIcon(Tree.Column.Name, Icon.FILE)
            self.setText(Tree.Column.Type, Tree.Type.FILE.name.lower())

    # }}}
    @property  # name# {{{
    def name(self):
        return self.text(Tree.Column.Name)

    # }}}
    @property  # path# {{{
    def path(self):
        return self.text(Tree.Column.Path)

    # }}}
    @property  # type# {{{
    def type(self):
        return self.__type


# }}}
# }}}
class Tree(QtWidgets.QTreeWidget):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0
        Type = 1
        Path = 2

    # }}}
    class Type(enum.Enum):  # {{{
        DATA = enum.auto()
        ANALYTIC = enum.auto()
        TINKOFF = enum.auto()
        ARCHIVE = enum.auto()
        ASSET = enum.auto()
        ASSET_LIST = enum.auto()
        TIMEFRAME = enum.auto()
        FILE = enum.auto()
        DIR = enum.auto()
        BIN = enum.auto()
        CONFIG = enum.auto()
        CSV = enum.auto()
        JSON = enum.auto()
        MARKDOWN = enum.auto()
        SCRIPT = enum.auto()
        TXT = enum.auto()

    # }}}
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__createMenu()
        self.__connect()
        self.__dirs = list()
        self.thread = None

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(Tree.Column.Name, Qt.SortOrder.AscendingOrder)
        self.setColumnWidth(Tree.Column.Name, 250)
        self.setColumnWidth(Tree.Column.Type, 80)
        self.setColumnWidth(Tree.Column.Path, 100)
        self.setFont(Font.MONO)

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.__refresh = QtGui.QAction("Refresh")
        self.__open = QtGui.QAction("Open as text")
        self.__show = QtGui.QAction("Show in explorer")
        self.__delete = QtGui.QAction(Icon.DELETE, "Delete...")

    # }}}
    def __createMenu(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.__refresh)
        self.menu.addAction(self.__open)
        self.menu.addAction(self.__show)
        self.menu.addAction(self.__delete)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.__refresh.triggered.connect(self.__onRefresh)
        self.__open.triggered.connect(self.__onOpenFile)
        self.__show.triggered.connect(self.__onShowInExplorer)
        self.__delete.triggered.connect(self.__onDelete)

    # }}}
    def __resetActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.menu.actions():
            i.setEnabled(False)

    # }}}
    def __setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.__refresh.setEnabled(True)
        elif item.type == Tree.Type.DIR:
            self.__refresh.setEnabled(True)
            self.__show.setEnabled(True)
            self.__delete.setEnabled(True)
        else:
            self.__refresh.setEnabled(True)
            self.__open.setEnabled(True)
            self.__show.setEnabled(True)
            self.__delete.setEnabled(True)

    # }}}
    def __selectUserData(self, item: IData):  # {{{
        logger.debug(f"{self.__class__.__name__}.__selectUserData()")
        for i in range(item.childCount()):
            child = item.child(i)
            if child.type == Tree.Type.DIR:
                self.__selectUserData(child)
            if child.type == Tree.Type.DATA:
                self.selected.append(child)

    # }}}
    @QtCore.pyqtSlot()  # __onRefresh# {{{
    def __onRefresh(self):
        logger.debug(f"{self.__class__.__name__}.__onRefresh()")
        self.clear()
        for i in self.__dirs:
            self.addDir(i)

    # }}}
    @QtCore.pyqtSlot()  # __onOpenFile# {{{
    def __onOpenFile(self):
        logger.debug(f"{self.__class__.__name__}.__openFile()")
        item = self.currentItem()
        path = item.path
        command = ("xfce4-terminal", "-x", "nvim", path)
        Cmd.subprocess(command)

    # }}}
    @QtCore.pyqtSlot()  # __onShowInExplorer# {{{
    def __onShowInExplorer(self):
        logger.debug(f"{self.__class__.__name__}.__showInExplorer()")
        item = self.currentItem()
        path = item.path
        command = ("thunar", path)
        Cmd.subprocess(command)

    # }}}
    @QtCore.pyqtSlot()  # __onDelete# {{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.delete")
        archives, tinkoff, data, analytic = self.delete_dialog.exec()
        if not (archives or tinkoff or data or analytic):
            return
        elif self.thread is not None:
            self.info_dialog.info(
                "Data manager is busy now, wait for complete task"
            )
        else:
            td = TinkoffData()
            self.thread = TDelete(td, archives, tinkoff, data, analytic)
            self.thread.finished.connect(self.__threadFinished)
            self.thread.start()

    # }}}
    def contextMenuEvent(self, e):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.itemAt(e.pos())
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    # }}}
    def addDir(self, dir_path):  # {{{
        logger.debug(f"{self.__class__.__name__}.addDir({dir_path})")
        self.__dirs.append(dir_path)
        name = Cmd.name(dir_path)
        top_level_dir = IData(name, dir_path)
        self.addTopLevelItem(top_level_dir)


# }}}
# }}}
class DataWidget(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__initUI()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tool_bar = ToolBar(self)
        self.data_tree = Tree(self)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.tool_bar)
        vbox.addWidget(self.data_tree)
        vbox.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")
        self.data_tree.addDir(DOWNLOAD_DIR)
        self.data_tree.addDir(DATA_DIR)


# }}}
# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = DataWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())
