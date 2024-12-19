#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum
import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin.gui.custom import (
    Font,
    Icon,
    ToolButton,
)


class Tree(QtWidgets.QTreeWidget):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0

    # }}}
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()

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
        self.setFont(Font.MONO)


# }}}


# }}}
class IndicatorDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserIndicators()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tree = Tree(self)
        self.search_line = QtWidgets.QLineEdit(self)
        self.btn_search = ToolButton(Icon.SEARCH, self)
        self.btn_apply = ToolButton(Icon.APPLY, self)
        self.btn_cancel = ToolButton(Icon.CANCEL, self)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.btn_search)
        hbox.addWidget(self.search_line)
        hbox.addStretch()
        hbox.addWidget(self.btn_apply)
        hbox.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.tree)
        self.setLayout(vbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_apply.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    # }}}
    def __loadUserIndicators(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserIndicators()")
        i = ExtremumHandler()
        self.__add(i)

    # }}}
    def __getSelected(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__getSelected()")
        selected = list()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(Tree.Column.Name) == Qt.CheckState.Checked:
                selected.append(item.handler)
        return selected

    # }}}
    def __add(self, indicator):  # {{{
        logger.debug(f"{self.__class__.__name__}.__add()")
        item = indicator.item
        self.tree.addTopLevelItem(item)

    # }}}
    def chooseIndicator(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserIndicators()")
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            selected = self.__getSelected()
            return selected
        else:
            return False


# }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ChartWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
