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

from avin.core import Strategy
from avin.utils import logger
from gui.custom import Css, Icon, Label, Spacer, ToolButton
from gui.strategy.item import StrategyItem, VersionItem


class StrategySelectDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()
        self.__loadUserStrategy()

    # }}}

    def selectStrategy(self) -> Strategy | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectStrategy()")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        item = self.__tree.currentItem()
        if isinstance(item, StrategyItem):
            return None

        if isinstance(item, VersionItem):
            return item.strategy

    # }}}
    def selectStrategys(self) -> list[Strategy]:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectStrategys()")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return list()

        selected = list()
        for strategy_item in self.__tree:
            for version_item in strategy_item:
                if version_item.isChecked():
                    selected.append(version_item.strategy)

        return selected

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
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__toolbar.btn_ok.clicked.connect(self.accept)
        self.__toolbar.btn_cancel.clicked.connect(self.reject)

    # }}}
    def __loadUserStrategy(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserStrategy()")

        strategy_names = Strategy.requestAll()
        for name in strategy_names:
            item = StrategyItem(name)
            item.loadVersions(checkable=True)
            # item.setCheckState(
            #     StrategyItem.Column.Name, Qt.CheckState.Unchecked
            # )
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
        self.setColumnWidth(StrategyItem.Column.Name, 300)
        self.setMinimumWidth(320)

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

        title = Label("| Select strategys:", parent=self)
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
    w = StrategySelectDialog()
    w.show()
    sys.exit(app.exec())
