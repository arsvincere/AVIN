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

from avin import logger
from gui.custom import (
    Css,
    Icon,
    Label,
    Spacer,
    ToolButton,
)
from gui.indicator.extremum import ExtremumIndicator


class IndicatorSelectDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserIndicators()

    # }}}

    def selectIndicators(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectIndicator()")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        selected = self.__tree.getSelected()
        return selected

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.DIALOG)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__toolbar = _ToolBar(self)
        self.__tree = _Tree(self)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__toolbar)
        vbox.addWidget(self.__tree)
        self.setLayout(vbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__toolbar.ok_btn.clicked.connect(self.accept)
        self.__toolbar.cancel_btn.clicked.connect(self.reject)

    # }}}
    def __loadUserIndicators(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserIndicators()")

        # full list of user indicators
        self.__indicators = [
            ExtremumIndicator(),
        ]

        # create items in tree
        for i in self.__indicators:
            self.__tree.addIndicator(i)

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

        title = Label("| Select indicator:", parent=self)
        title.setStyleSheet(Css.TITLE)

        self.search_btn = ToolButton(Icon.SEARCH, parent=self)
        self.search_lineedit = QtWidgets.QLineEdit(parent=self)
        self.ok_btn = ToolButton(Icon.OK, "Ok", parent=self)
        self.cancel_btn = ToolButton(Icon.CANCEL, "Cancel", parent=self)

        self.addWidget(title)
        self.addWidget(Spacer(width=10))
        self.addWidget(self.search_btn)
        self.addWidget(self.search_lineedit)
        self.addWidget(Spacer())
        self.addWidget(self.ok_btn)
        self.addWidget(self.cancel_btn)

    # }}}


# }}}
class _Tree(QtWidgets.QTreeWidget):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0

    # }}}

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()

    # }}}
    def __iter__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__iter__()")

        all_items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            all_items.append(item)

        return iter(all_items)

    # }}}

    def addIndicator(self, indicator):  # {{{
        logger.debug(f"{self.__class__.__name__}.addIndicator()")

        item = indicator.item()
        self.addTopLevelItem(item)

    # }}}
    def getSelected(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.getSelected()")

        selected = list()
        for item in self:
            if item.checkState(self.Column.Name) == Qt.CheckState.Checked:
                selected.append(item.indicator)

        return selected

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config header
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(self.Column.Name, Qt.SortOrder.AscendingOrder)

        # config width
        self.setColumnWidth(self.Column.Name, 280)
        self.setMinimumWidth(300)

        # config style
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)


# }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = IndicatorSelectDialog()
    w.show()
    sys.exit(app.exec())
