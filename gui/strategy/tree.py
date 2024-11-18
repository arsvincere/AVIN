#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.config import Usr
from avin.core import StrategyList
from avin.utils import Cmd, logger
from gui.custom import Css, Dialog
from gui.strategy.item import ConfigItem, StrategyItem, VersionItem


class StrategyTree(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__createActions()
        self.__createMenu()
        self.__config()
        self.__connect()

    # }}}

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug("Tree.contextMenuEvent(e)")
        item = self.itemAt(e.pos())
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    # }}}
    def setStrategyList(self, slist: StrategyList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setStrategyList()")

        self.clear()
        for strategy in slist:
            item = StrategyItem(strategy, self)
            self.addTopLevelItem(item)

        self.__current_slist = slist

    # }}}
    def currentStrategyList(self) -> StrategyList:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentStrategyList()")

        return self.__current_alist

    # }}}

    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.__new = QtGui.QAction("New", self)
        self.__copy = QtGui.QAction("Copy", self)
        self.__edit = QtGui.QAction("Edit", self)
        self.__rename = QtGui.QAction("Rename", self)
        self.__delete = QtGui.QAction("Delete", self)

    # }}}
    def __createMenu(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenu()")

        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.__new)
        self.menu.addAction(self.__copy)
        self.menu.addAction(self.__edit)
        self.menu.addAction(self.__rename)
        self.menu.addAction(self.__delete)
        self.menu.setStyleSheet(Css.MENU)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config header
        labels = list()
        for l in StrategyItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(
            StrategyItem.Column.Name, Qt.SortOrder.AscendingOrder
        )

        # config width
        self.setColumnWidth(StrategyItem.Column.Name, 150)

        # config style
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__new.triggered.connect(self.__onNew)
        self.__copy.triggered.connect(self.__onCopy)
        self.__edit.triggered.connect(self.__onEdit)
        self.__rename.triggered.connect(self.__onRename)
        self.__delete.triggered.connect(self.__onDelete)

    # }}}
    def __setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")

        # disable all actions
        for i in self.menu.actions():
            i.setEnabled(False)

        # enable availible for this item
        if item is None:
            self.__new.setEnabled(True)
        elif isinstance(item, StrategyItem):
            self.__new.setEnabled(True)
            self.__rename.setEnabled(True)
            self.__delete.setEnabled(True)
        elif isinstance(item, ConfigItem):
            self.__edit.setEnabled(True)
        elif isinstance(item, VersionItem):
            self.__copy.setEnabled(True)
            self.__edit.setEnabled(True)
            self.__rename.setEnabled(True)
            self.__delete.setEnabled(True)

    # }}}

    @QtCore.pyqtSlot()  # __onNew{{{
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")

        name = Dialog.name("Enter strategy name")
        if not name:
            return

        new_strategy_item = StrategyItem.new(name)
        if new_strategy_item:
            self.addTopLevelItem(new_strategy_item)
        else:
            Dialog.error("Name alreade exist, creation canceled.")

    # }}}
    @QtCore.pyqtSlot()  # __onCopy{{{
    def __onCopy(self):
        logger.debug(f"{self.__class__.__name__}.__onCopy()")

        new_name = Dialog.name("New name...")
        if not new_name:
            return

        item = self.currentItem()
        new_version_item = VersionItem.copy(item, new_name)
        if new_version_item:
            strategy_item = item.parent()
            strategy_item.addChild(new_version_item)
        else:
            Dialog.error("Name alreade exist, coping canceled.")

    # }}}
    @QtCore.pyqtSlot()  # __onRename{{{
    def __onRename(self):
        logger.debug(f"{self.__class__.__name__}.__onRename()")

        new_name = Dialog.name("New name...")
        if not new_name:
            return

        item = self.currentItem()
        match item.__class__.__name__:
            case "StrategyItem":
                StrategyItem.rename(item, new_name)
            case "VersionItem":
                VersionItem.rename(item, new_name)

    # }}}
    @QtCore.pyqtSlot()  # __onEdit{{{
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onEdit()")

        item = self.currentItem()
        assert isinstance(item, (VersionItem, ConfigItem))

        command = (
            Usr.TERMINAL,
            *Usr.OPT,
            Usr.EXEC,
            Usr.EDITOR,
            item.path,
        )
        Cmd.subprocess(command)

    # }}}
    @QtCore.pyqtSlot()  # __onDelete{{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.__onDelete()")
        if not Dialog.confirm():
            return

        item = self.currentItem()
        match item.__class__.__name__:
            case "StrategyItem":
                index = self.indexFromItem(item).row()
                self.takeTopLevelItem(index)
                StrategyItem.delete(item)
            case "VersionItem":
                strategy_item = item.parent()
                index = strategy_item.indexOfChild(item)
                strategy_item.takeChild(index)
                VersionItem.delete(item)

    # }}}


# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = StrategyTree()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
