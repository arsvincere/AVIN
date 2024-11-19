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

from avin.core import AssetList
from avin.utils import logger
from gui.asset.item import AssetItem
from gui.asset.thread import Thread
from gui.custom import Css, Icon, LineEdit, ToolButton

# TODO:
# а что если:
# Editor -> AssetWidget
# AssetWidget -> AssetListWidget
# и у AssetWidget добавить метод
# чтобы он мог возвращать один ассет - getAsset()
# и так же сохранить функционал что он может возвращать список - editAssetList
# тогда этот виджет будет более универсальным, его и график сможет дергать
# и StrategySet...


class Editor(QtWidgets.QDialog):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__all_assets = None

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()
        self.__loadUserAssets()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__tree = _Tree(self)
        self.__search_line = LineEdit("Enter ticker...", self)
        self.__btn_search = ToolButton(Icon.SEARCH)
        self.__btn_ok = ToolButton(Icon.OK)
        self.__btn_cancel = ToolButton(Icon.CANCEL)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.__btn_search)
        hbox.addWidget(self.__search_line)
        hbox.addStretch()
        hbox.addWidget(self.__btn_ok)
        hbox.addWidget(self.__btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.__tree)
        self.setLayout(vbox)

    # }}}
    def __config(self):  # {{{
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN  -  Widget")

    # }}}
    def __connect(self):  # {{{
        self.__btn_ok.clicked.connect(self.accept)
        self.__btn_cancel.clicked.connect(self.reject)

    # }}}
    def __loadUserAssets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserAssets()")

        assets = Thread.requestAllAsset()
        self.__all_assets = AssetList(name="", assets=assets)
        self.__tree.setAssetList(self.__all_assets)

    # }}}
    def __clearMark(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__clearMark()")
        for i in self.__tree:
            i.setCheckState(Tree.Column.Ticker, Qt.CheckState.Unchecked)

    # }}}
    def __markExisting(self, alist):  # {{{
        logger.debug(f"{self.__class__.__name__}.__markExisting()")
        for item in self.__tree:
            if item.asset in alist:
                item.setCheckState(
                    AssetItem.Column.Ticker, Qt.CheckState.Checked
                )
            else:
                item.setCheckState(
                    AssetItem.Column.Ticker, Qt.CheckState.Unchecked
                )

    # }}}
    def editAssetList(self, editable: AssetList) -> AssetList | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.editAssetList()")

        self.__markExisting(editable)

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        editable.clear()
        for i in self.__tree:
            state = i.checkState(AssetItem.Column.Ticker)
            if state == Qt.CheckState.Checked:
                index = self.__tree.indexOfTopLevelItem(i)
                item = self.__tree.takeTopLevelItem(index)
                editable.add(item.asset)
        return editable


# }}}


class _Tree(QtWidgets.QTreeWidget):
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
    def setAssetList(self, alist: AssetList):  # {{{
        logger.debug(f"{self.__class__.__name__}.setAssetList()")

        self.clear()
        self.__current_alist = alist
        for asset in alist:
            item = AssetItem(asset)
            self.addTopLevelItem(item)

    # }}}
    def currentAssetList(self) -> AssetList:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentAssetList()")

        return self.__current_alist

    # }}}
    def editCurrentAssetList(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.editCurrentAssetList()")

        editor = Editor()
        edited_list = editor.editAssetList(ialist)
        if edited_list:
            self.setAssetList(edited_list)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        labels = list()
        for i in AssetItem.Column:
            labels.append(i.name)
        self.setHeaderLabels(labels)

        self.setColumnWidth(AssetItem.Column.Ticker, 100)
        self.setColumnWidth(AssetItem.Column.Name, 200)
        self.setColumnWidth(AssetItem.Column.Type, 75)
        self.setColumnWidth(AssetItem.Column.Exchange, 75)
        self.setColumnWidth(AssetItem.Column.Figi, 150)
        self.setFixedWidth(620)
        self.setMinimumHeight(400)

        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setStyleSheet(Css.TREE)
        self.header().setStyleSheet(Css.TREE_HEADER)
        self.setContentsMargins(0, 0, 0, 0)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Editor()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
