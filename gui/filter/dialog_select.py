#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin.core import Filter, FilterList
from avin.utils import logger
from gui.custom import Css, Icon, Label, Spacer, ToolButton
from gui.filter.item import FilterItem, FilterListItem


class FilterSelectDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserFilters()

    # }}}
    def selectFilter(self) -> FilterList | Filter | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectFilter()")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        item = self.__tree.currentItem()
        if item is None:
            return None

        if isinstance(item, FilterItem):
            f = item.filter
            return f
        elif isinstance(item, FilterListItem):
            f = item.filter_list
            return f
        else:
            assert False, "жизнь меня к этому не готовила..."

    # }}}
    def selectFilters(self) -> list[Filter]:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectFilters()")

        for item in self.__tree:
            item.setCheckState(
                FilterItem.Column.Name, Qt.CheckState.Unchecked
            )

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return list()

        selected = list()
        for item in self.__tree:
            if item.isChecked():
                selected.append(item.filter)

        return selected

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

        self.setMinimumWidth(500)
        self.setMinimumHeight(800)

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

        vbox.setContentsMargins(8, 4, 8, 8)
        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__toolbar.btn_ok.clicked.connect(self.accept)
        self.__toolbar.btn_cancel.clicked.connect(self.reject)

    # }}}
    def __loadUserFilters(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserTests()")

        all_names = FilterList.requestAll()
        for name in all_names:
            filter_list = FilterList.load(name)
            item = FilterListItem(filter_list)
            self.__tree.addTopLevelItem(item)

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
        for l in FilterItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(FilterItem.Column.Name, Qt.SortOrder.AscendingOrder)

        # config width
        self.setColumnWidth(FilterItem.Column.Name, 250)
        self.setMinimumWidth(300)

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

        title = Label("| Select filters:", parent=self)
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
    w = FilterSelectDialog()
    w.show()
    sys.exit(app.exec())
