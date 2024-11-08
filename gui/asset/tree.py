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

from avin.core import Asset, AssetList
from avin.utils import logger
from gui.asset.item import AssetItem
from gui.custom import Css, Menu


class AssetListTree(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__createMenu()
        self.__config()
        self.__connect()

    # }}}
    def __iter__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__iter__()")

        items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            items.append(item)
        return iter(items)

    # }}}
    def setAssetList(self, alist: AssetList):  # {{{
        logger.debug(f"{self.__class__.__name__}.setAssetList()")

        self.clear()
        for asset in alist:
            item = AssetItem(asset)
            self.addTopLevelItem(item)

    # }}}
    def currentAsset(self) -> Asset:  # {{{
        item = self.currentItem()
        return item.asset

    # }}}
    def contextMenuEvent(self, e):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")

        item = self.itemAt(e.pos())
        self.__resetActions()
        self.__setVisibleActions(item)
        self.__menu.exec(QtGui.QCursor.pos())
        # return e.ignore()

    # }}}
    def __createMenu(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createContextMenu()")
        self.__action_add = QtGui.QAction("Add", self)
        self.__action_remove = QtGui.QAction("Remove", self)
        self.__action_info = QtGui.QAction("Info", self)
        self.__menu = Menu(parent=self)
        self.__menu.addAction(self.__action_add)
        self.__menu.addAction(self.__action_remove)
        self.__menu.addAction(self.__action_info)

        self.addAction(self.__action_add)
        self.addAction(self.__action_remove)
        self.addAction(self.__action_info)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)

    # }}}
    def __config(self):  # {{{
        self.setHeaderLabels(["Ticker", "Name"])
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setStyleSheet(Css.TREE)
        self.header().setStyleSheet(Css.TREE_HEADER)
        self.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.__action_add.triggered.connect(self.__onAdd)
        self.__action_remove.triggered.connect(self.__onRemove)
        self.__action_info.triggered.connect(self.__onInfo)

    # }}}
    def __resetActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.__menu.actions():
            i.setEnabled(False)

    # }}}
    def __setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.__action_add.setEnabled(True)
        if isinstance(item, Asset):
            self.__action_add.setEnabled(True)
            self.__action_remove.setEnabled(True)
            self.__action_info.setEnabled(True)

    # }}}
    @QtCore.pyqtSlot()  # __onAdd{{{
    def __onAdd(self):
        logger.debug(f"{self.__class__.__name__}.__onAdd()")
        ialist = self.parent().currentList()
        editor = Editor()
        edited_list = editor.editAssetList(ialist)
        if edited_list:
            IAssetList.save(edited_list)
            self.parent().updateWidget()
            logger.info("Asset list saved")

    # }}}
    @QtCore.pyqtSlot()  # __onRemove{{{
    def __onRemove(self):
        logger.debug(f"{self.__class__.__name__}.__onRemove()")
        item = self.currentItem()
        assert isinstance(item, IShare)
        ialist = item.parent()
        ialist.remove(item)
        IAssetList.save(ialist)

    # }}}
    @QtCore.pyqtSlot()  # __onInfo{{{
    def __onInfo(self):
        logger.debug(f"{self.__class__.__name__}.__onInfo()")
        ...

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Tree()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
