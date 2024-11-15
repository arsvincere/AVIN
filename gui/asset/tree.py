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
from gui.asset.editor import Editor
from gui.asset.item import AssetItem
from gui.asset.thread import Thread
from gui.custom import Css, Dialog, Menu


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
        self.__current_alist = alist
        for asset in alist:
            item = AssetItem(asset)
            self.addTopLevelItem(item)

    # }}}
    def currentAsset(self) -> Asset:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentAsset()")

        item = self.currentItem()
        return item.asset

    # }}}
    def currentAssetList(self) -> AssetList:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentAssetList()")

        return self.__current_alist

    # }}}
    def editCurrentAssetList(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.editCurrentAssetList()")

        editor = Editor()
        edited_list = editor.editAssetList(self.__current_alist)
        if edited_list:
            Thread.save(edited_list)
            self.setAssetList(edited_list)
            logger.info("Asset list edited")
        else:
            logger.info("Cancel edit asset list")

    # }}}
    def contextMenuEvent(self, e):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")

        item = self.itemAt(e.pos())
        self.__resetActions()
        self.__setVisibleActions(item)
        self.__menu.exec(QtGui.QCursor.pos())
        return e.ignore()

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
        if isinstance(item, AssetItem):
            self.__action_add.setEnabled(True)
            self.__action_remove.setEnabled(True)
            self.__action_info.setEnabled(True)

    # }}}
    @QtCore.pyqtSlot()  # __onAdd{{{
    def __onAdd(self):
        logger.debug(f"{self.__class__.__name__}.__onAdd()")

        self.editCurrentAssetList()

    # }}}
    @QtCore.pyqtSlot()  # __onRemove{{{
    def __onRemove(self):
        logger.debug(f"{self.__class__.__name__}.__onRemove()")

        # get current item
        item = self.currentItem()
        assert isinstance(item, AssetItem)

        # edit asset list
        self.__current_alist.remove(item.asset)
        Thread.save(self.__current_alist)

        # edit tree
        model_index = self.indexFromItem(item)
        index = model_index.row()
        self.takeTopLevelItem(index)

    # }}}
    @QtCore.pyqtSlot()  # __onInfo{{{
    def __onInfo(self):
        logger.debug(f"{self.__class__.__name__}.__onInfo()")

        # TODO: this
        # надо заебенить какой то общий виджет с информацией
        # об активе. Он будет использоваться не только этим
        # модулем, ну типо в любом место чтобы по активу
        # можно было кликнуть и посмотреть подробную инфу,
        # поэтому его в отдельный файл запихай.
        Dialog.info("This feature not avalible, its coming soon")

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = AssetListTree()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
