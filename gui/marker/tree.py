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

from avin.utils import logger
from gui.custom import Css, Dialog, Menu
from gui.marker.item import MarkItem
from gui.marker.mark import Mark, MarkList


class MarkTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()
        self.__createMenus()
        self.__connect()

        self.thread = None

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

        self.marker_menu.setVisibleActions(self.__current_item)
        self.marker_menu.exec(QtGui.QCursor.pos())

        return e.ignore()

    # }}}
    def setMarkList(self, mark_list: MarkList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setMarkList()")

        self.clear()
        for mark in mark_list:
            self.addMark(mark)

    # }}}
    def addMark(self, mark: Mark) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.addMark()")

        item = MarkItem(mark)
        self.addTopLevelItem(item)

    # }}}
    def removeMark(self, mark: Mark) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeMark()")

        for item in self:
            if item.mark.name == mark.name:
                index = self.indexFromItem(item).row()
                self.takeTopLevelItem(index)

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config header
        labels = list()
        for l in MarkItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(MarkItem.Column.Filter, Qt.SortOrder.AscendingOrder)

        # config width
        self.setColumnWidth(MarkItem.Column.Filter, 250)
        self.setColumnWidth(MarkItem.Column.Shape, 50)
        self.setMinimumWidth(320)

        # config style
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __createMenus(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.marker_menu = _MarkMenu(self)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.marker_menu.new.triggered.connect(self.__onNew)
        self.marker_menu.edit.triggered.connect(self.__onEdit)
        self.marker_menu.delete.triggered.connect(self.__onDelete)

    # }}}

    @QtCore.pyqtSlot()  # __onNew# {{{
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")

    # }}}
    @QtCore.pyqtSlot()  # __onEdit# {{{
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onEdit()")

        item = self.__current_item

    # }}}
    @QtCore.pyqtSlot()  # __onDelete# {{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.delete()")

        if not Dialog.confirm():
            return

        item = self.__current_item

    # }}}


# }}}
class _MarkMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Menu.__init__(self, parent=parent)

        self.new = QtGui.QAction("New", self)
        self.edit = QtGui.QAction("Edit", self)
        self.delete = QtGui.QAction("Delete", self)

        self.addAction(self.new)
        self.addAction(self.edit)
        self.addAction(self.delete)

    # }}}

    def setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.setVisibleActions()")

        # disable all actions
        for i in self.actions():
            i.setEnabled(False)

        # # enable availible for this item
        if item is None:
            self.new.setEnabled(True)
        elif isinstance(item, MarkItem):
            self.new.setEnabled(True)
            self.edit.setEnabled(True)
            self.delete.setEnabled(True)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MarkerTree()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
