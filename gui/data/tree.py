#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.utils import Cmd, logger
from gui.custom import Css, Font, Icon
from gui.data.item import DataInfoItem, InstrumentItem


class DataInfoTree(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        # self.__createActions()
        # self.__createMenu()
        # self.__connect()
        # self.__dirs = list()
        # self.thread = None

    # }}}
    def contextMenuEvent(self, e):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.itemAt(e.pos())
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    # }}}
    def add(self, info: DataInfo) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")

        instruments = info.getInstruments()
        for instrument in instruments:
            instr_item = InstrumentItem(instrument)
            self.addTopLevelItem(instr_item)

            for node in info[instrument]:
                node_item = DataInfoItem(node)
                instr_item.addChild(node_item)

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
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # header labels
        column = InstrumentItem.Column
        labels = list()
        for i in column:
            labels.append(i.name)
        self.setHeaderLabels(labels)

        # column width
        self.setColumnWidth(column.Ticker, 100)
        self.setColumnWidth(column.Name, 150)
        self.setColumnWidth(column.Figi, 150)
        self.setColumnWidth(column.Exchange, 100)
        self.setColumnWidth(column.AssetType, 100)
        self.setMinimumWidth(620)

        # other options
        self.setSortingEnabled(True)
        self.sortByColumn(column.Ticker, Qt.SortOrder.AscendingOrder)
        self.setStyleSheet(Css.STYLE)
        self.setFont(Font.MONO)

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
    def __findTopLevelItem(  # {{{
        self, info: UIBarDataInfo
    ) -> UIBarDataInfo | None:
        for i in range(self.topLevelItemCount()):
            top_item = self.topLevelItem(i)
            if top_item.info.instrument == info.instrument:
                return top_item

        return None

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = DataInfoTree()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
