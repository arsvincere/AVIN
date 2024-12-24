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

from avin import Asset, AssetList, logger
from gui.asset.item import AssetItem
from gui.asset.thread import Thread
from gui.custom import Css, Icon, LineEdit, ToolButton


class AssetSelectDialog(QtWidgets.QDialog):  # {{{
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

    def selectAsset(self) -> Asset | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.editAssetList()")

        # self.__enableSingleMode()

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        item = self.__tree.currentItem()
        if item is None:
            return None

        return item.asset

    # }}}
    def selectAssets(self) -> AssetList | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.editAssetList()")

        self.__enableMultipleMode()

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        selected = AssetList("selected")
        for i in self.__tree:
            if i.isChecked():
                selected.add(i.asset)

        return selected

    # }}}
    def editAssetList(self, editable: AssetList) -> AssetList | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.editAssetList()")

        self.__enableMultipleMode()
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
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__btn_ok.clicked.connect(self.accept)
        self.__btn_cancel.clicked.connect(self.reject)

    # }}}
    def __loadUserAssets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserAssets()")

        assets = Thread.requestAllAsset()
        self.__all_assets = AssetList(name="", assets=assets)
        self.__tree.setAssetList(self.__all_assets)

    # }}}
    def __enableMultipleMode(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__enableMultipleMode()")

        for item in self.__tree:
            item.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEnabled
            )

    # }}}
    def __enableSingleMode(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__enableSingleMode()")

        for item in self.__tree:
            item.setFlags(
                Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
            )

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

    def setAssetList(self, alist: AssetList):  # {{{
        logger.debug(f"{self.__class__.__name__}.setAssetList()")

        self.clear()
        self.__current_alist = alist
        for asset in alist:
            item = AssetItem(asset)
            self.addTopLevelItem(item)

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


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = AssetSelectDialog()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
