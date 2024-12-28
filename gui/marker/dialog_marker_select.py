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
from gui.custom import Css, Dialog, Icon, Label, Menu, Spacer, ToolButton
from gui.marker.dialog_marker_edit import MarkerEditDialog
from gui.marker.item import MarkItem
from gui.marker.mark import Mark, MarkList


class MarkerSelectDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserMarks()

    # }}}

    def selectMarks(self) -> MarkList | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectMarks()")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        selected = MarkList("selected")
        for item in self.__mark_tree:
            if item.isChecked():
                selected.add(item.mark)

        return selected

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.STYLE)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__tool_bar = _ToolBar(self)
        self.__mark_tree = _MarkTree(self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.__tool_bar)
        vbox.addWidget(self.__mark_tree)

        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__tool_bar.btn_cancel.clicked.connect(self.reject)
        self.__tool_bar.btn_ok.clicked.connect(self.accept)

    # }}}
    def __loadUserMarks(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserMarks()")

        mark_list = MarkList.load("mark_list")

        self.__mark_tree.setMarkList(mark_list)

    # }}}


# }}}


class _ToolBar(QtWidgets.QToolBar):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__createWidgets()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        title = Label("| Select marks:", parent=self)
        title.setStyleSheet(Css.TITLE)
        self.addWidget(title)
        self.addWidget(Spacer())

        self.btn_ok = ToolButton(Icon.OK, "Ok", parent=self)
        self.btn_cancel = ToolButton(Icon.CANCEL, "Cancel", parent=self)
        self.addWidget(self.btn_ok)
        self.addWidget(self.btn_cancel)

    # }}}


# }}}
class _MarkTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()
        self.__createMenus()
        self.__connect()

        self.__mark_list = None

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
        self.__mark_list = mark_list

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
        self.marker_menu.remove.triggered.connect(self.__onRemove)
        self.marker_menu.delete.triggered.connect(self.__onDelete)

    # }}}

    @QtCore.pyqtSlot()  # __onNew# {{{
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")

        dial = MarkerEditDialog()
        mark = dial.newMark()
        if mark is not None:
            # add mark in MarkList
            self.__mark_list.add(mark)
            MarkList.save(self.__mark_list)

            # add mark in tree
            self.addMark(mark)

    # }}}
    @QtCore.pyqtSlot()  # __onEdit# {{{
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onEdit()")

        mark = self.__current_item.mark
        dial = MarkerEditDialog()
        edited = dial.editMark(mark)

        if edited is not None:
            # add mark in MarkList
            self.__mark_list.remove(mark)
            self.__mark_list.add(edited)
            MarkList.save(self.__mark_list)

            # add mark in tree
            self.removeMark(mark)
            self.addMark(edited)

    # }}}
    @QtCore.pyqtSlot()  # __onRemove# {{{
    def __onRemove(self):
        logger.debug(f"{self.__class__.__name__}.__onRemove()")

        mark = self.__current_item.mark
        self.__mark_list.remove(mark)
        self.removeMark(mark)

    # }}}
    @QtCore.pyqtSlot()  # __onDelete# {{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.__onDelete()")

        if not Dialog.confirm():
            return

        mark = self.__current_item.mark

        self.__mark_list.remove(mark)
        MarkList.save(self.__mark_list)

        self.removeMark(mark)

    # }}}


# }}}
class _MarkMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Menu.__init__(self, parent=parent)

        self.new = QtGui.QAction("New", self)
        self.edit = QtGui.QAction("Edit", self)
        self.remove = QtGui.QAction("Remove", self)
        self.delete = QtGui.QAction("Delete", self)

        self.addAction(self.new)
        self.addAction(self.edit)
        self.addAction(self.remove)
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
            self.remove.setEnabled(True)
            self.delete.setEnabled(True)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MarkerSelectDialog()
    w.show()
    sys.exit(app.exec())
