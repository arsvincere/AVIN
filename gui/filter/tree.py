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

from avin.core import Filter
from avin.utils import logger
from gui.custom import Css, Dialog, Menu
from gui.filter.item import FilterItem


class FilterTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()
        self.__createMenus()
        self.__connect()

        self.__current_item = None

    # }}}
    def __iter__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__iter__()")

        all_items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            all_items.append(item)

        return iter(all_items)

    # }}}

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")

        self.__current_item = self.itemAt(e.pos())
        self.menu.setVisibleActions(self.__current_item)
        self.menu.exec(QtGui.QCursor.pos())

        return e.ignore()

    # }}}
    def addFilter(self, f: Filter) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.addFilter()")

        item = FilterItem(f)
        self.addTopLevelItem(item)

    # }}}
    def removeFilter(self, f: Filter) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeFilter()")

        for item in self:
            if item.filter.name == f.name:
                index = self.indexFromItem(item).row()
                self.takeTopLevelItem(index)

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config style
        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        # config header
        labels = list()
        for l in FilterItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(FilterItem.Column.Name, Qt.SortOrder.AscendingOrder)

        # config width
        self.setColumnWidth(FilterItem.Column.Name, 180)
        self.setMinimumWidth(200)

    # }}}
    def __createMenus(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.menu = _FilterMenu(parent=self)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.menu.new.triggered.connect(self.__onNew)
        self.menu.edit.triggered.connect(self.__onEdit)
        self.menu.copy.triggered.connect(self.__onCopy)
        self.menu.rename.triggered.connect(self.__onRename)
        self.menu.delete.triggered.connect(self.__onDelete)

    # }}}

    @QtCore.pyqtSlot()  # __onNew# {{{
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")

        name = Dialog.name("Enter filter name")
        if not name:
            return

        f = Filter.new(name)
        if f is not None:
            self.addFilter(f)

    # }}}
    @QtCore.pyqtSlot()  # __onEdit# {{{
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onEdit()")

        f = self.__current_item.filter
        Filter.edit(f)

    # }}}
    @QtCore.pyqtSlot()  # __onCopy# {{{
    def __onCopy(self):
        logger.debug(f"{self.__class__.__name__}.__onCopy()")

        new_name = Dialog.name("New name...")
        if not new_name:
            return

        f = self.__current_item.filter
        copy = Filter.copy(f, new_name)
        if copy is not None:
            self.addFilter(copy)

    # }}}
    @QtCore.pyqtSlot()  # __onRename# {{{
    def __onRename(self):
        logger.debug(f"{self.__class__.__name__}.__onRename()")

        # enter new name
        new_name = Dialog.name("New name...")
        if not new_name:
            return

        f = self.__current_item.filter
        renamed = Filter.rename(f, new_name)

        if renamed is not None:
            self.removeFilter(f)
            self.addFilter(renamed)

    # }}}
    @QtCore.pyqtSlot()  # __onDelete# {{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.delete()")

        if not Dialog.confirm():
            return

        f = self.__current_item.filter

        # delete filter
        Filter.delete(f)

        # delete item from tree
        self.removeFilter(f)

    # }}}


# }}}
class _FilterMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Menu.__init__(self, parent=parent)

        self.new = QtGui.QAction("New", self)
        self.edit = QtGui.QAction("Edit", self)
        self.copy = QtGui.QAction("Copy", self)
        self.rename = QtGui.QAction("Rename", self)
        self.delete = QtGui.QAction("Delete", self)

        self.addAction(self.new)
        self.addAction(self.edit)
        self.addAction(self.copy)
        self.addAction(self.rename)
        self.addAction(self.delete)

    # }}}

    def setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")

        # disable all actions
        for i in self.actions():
            i.setEnabled(False)

        # # enable availible for this item
        if item is None:
            self.new.setEnabled(True)
        elif isinstance(item, FilterItem):
            self.new.setEnabled(True)
            self.edit.setEnabled(True)
            self.copy.setEnabled(True)
            self.rename.setEnabled(True)
            self.delete.setEnabled(True)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = FilterTree()
    w.show()
    sys.exit(app.exec())
