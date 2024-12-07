#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin.data import DataInfo
from avin.utils import logger
from gui.custom import Css
from gui.data.item import DataInfoItem, InstrumentItem


class DataInfoTree(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()

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
    def selectedData(self) -> DataInfo:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectedInstruments()")

        selected = list()
        for i in range(self.topLevelItemCount()):
            instrument_item = self.topLevelItem(i)
            for j in range(instrument_item.childCount()):
                data_item = instrument_item.child(j)
                if (
                    data_item.checkState(DataInfoItem.Column.DataType)
                    == Qt.CheckState.Checked
                ):
                    selected.append(data_item.info)

        data_info = DataInfo(selected)
        return data_info

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config style
        self.setStyleSheet(Css.TREE)

        # config header
        column = InstrumentItem.Column
        labels = list()
        for i in column:
            labels.append(i.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # column width
        self.setColumnWidth(column.Ticker, 150)
        self.setColumnWidth(column.Name, 150)
        self.setColumnWidth(column.Figi, 150)
        self.setColumnWidth(column.Exchange, 130)
        self.setColumnWidth(column.AssetType, 100)
        self.setMinimumWidth(700)

        # other options
        self.setSortingEnabled(True)
        self.sortByColumn(column.Ticker, Qt.SortOrder.AscendingOrder)

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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = DataInfoTree()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
