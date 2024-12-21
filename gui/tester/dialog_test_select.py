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

from avin.utils import logger
from gui.custom import Css, Icon, Label, Spacer, ToolButton
from gui.filter.item import FilterItem
from gui.tester.thread import Thread


class TestSelectDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserTests()

    # }}}
    def selectTestName(self) -> str | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectFilter()")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        item = self.__tree.currentItem()
        if item is None:
            return None

        name = item.test_name
        return name

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__toolbar = _ToolBar(self)
        self.__tree = _Tree(self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__toolbar)
        vbox.addWidget(self.__tree)

        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__toolbar.btn_ok.clicked.connect(self.accept)
        self.__toolbar.btn_cancel.clicked.connect(self.reject)

    # }}}
    def __loadUserTests(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserTests()")

        all_names = Thread.requestAllTest()
        for name in all_names:
            item = _TestItem(name)
            self.__tree.addTopLevelItem(item)

    # }}}


# }}}


class _TestItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0

    # }}}

    def __init__(self, name: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.test_name = name
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(self.Column.Name, name)

    # }}}


# }}}
class _Tree(QtWidgets.QTreeWidget):  # {{{
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
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config header
        labels = list()
        for l in _TestItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(FilterItem.Column.Name, Qt.SortOrder.AscendingOrder)

        # config width
        self.setColumnWidth(FilterItem.Column.Name, 150)

        # config style
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)

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

        title = Label("| Select test:", parent=self)
        title.setStyleSheet(Css.TITLE)
        self.addWidget(title)
        self.addWidget(Spacer())

        self.btn_ok = ToolButton(Icon.OK, "Ok", parent=self)
        self.btn_cancel = ToolButton(Icon.CANCEL, "Cancel", parent=self)
        self.addWidget(self.btn_ok)
        self.addWidget(self.btn_cancel)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TestSelectDialog()
    w.show()
    sys.exit(app.exec())
