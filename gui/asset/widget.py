#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


import sys

from PyQt6 import QtCore, QtWidgets

from avin.core import Asset, AssetList
from avin.utils import logger
from gui.asset.thread import Thread
from gui.asset.toolbar import AssetListToolBar
from gui.asset.tree import AssetListTree
from gui.custom import Css, Dialog


class AssetWidget(QtWidgets.QWidget):
    assetChanged = QtCore.pyqtSignal(Asset)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__thread = None

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()
        self.__loadUserAssetLists()

    # }}}
    def currentAsset(self) -> Asset:  # {{{
        return self.tree.currentAsset()

    # }}}
    def currentAssetList(self) -> AssetList:  # {{{
        return self.tree.currentAssetList()

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__tool_bar = AssetListToolBar(self)
        self.__tree = AssetListTree(self)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__tool_bar)
        vbox.addWidget(self.__tree)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    # }}}
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setStyleSheet(Css.STYLE)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__tree.itemClicked.connect(self.__onItemClicked)
        self.__tool_bar.listChanged.connect(self.__updateWidget)
        self.__tool_bar.action_add.triggered.connect(self.__onAdd)
        self.__tool_bar.action_new.triggered.connect(self.__onNew)
        self.__tool_bar.action_rename.triggered.connect(self.__onRename)
        self.__tool_bar.action_copy.triggered.connect(self.__onCopy)
        self.__tool_bar.action_clear.triggered.connect(self.__onClear)
        self.__tool_bar.action_delete.triggered.connect(self.__onDelete)

    # }}}
    def __loadUserAssetLists(self):  # {{{
        logger.debug("self.__class__.__name__.__loadUserAssetLists()")

        all_names = Thread.requestAllAssetList()
        for list_name in sorted(all_names):
            self.__tool_bar.addAssetListName(list_name)

        self.__updateWidget()

    # }}}

    @QtCore.pyqtSlot()  # __updateWidget  # {{{
    def __updateWidget(self):
        logger.debug(f"{self.__class__.__name__}.__updateWidget()")

        list_name = self.__tool_bar.currentAssetListName()
        alist = Thread.load(list_name)
        self.__tree.setAssetList(alist)

    # }}}
    @QtCore.pyqtSlot()  # __onItemClicked{{{
    def __onItemClicked(self):
        logger.debug(f"{self.__class__.__name__}.__onItemClicked()")
        asset = self.__tree.currentAsset()
        self.assetChanged.emit(asset)

    # }}}
    @QtCore.pyqtSlot()  # __onAdd{{{
    def __onAdd(self):
        logger.debug(f"{self.__class__.__name__}.__onAdd()")

        self.__tree.editCurrentAssetList()

    # }}}
    @QtCore.pyqtSlot()  # __onNew{{{
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")

        name = Dialog.name("New list name")
        if self.__tool_bar.isExist(name):
            Dialog.error("Name already exist.\nAssetList not created.")
            return

        new_list = AssetList(name)
        Thread.save(new_list)
        self.__tool_bar.addAssetListName(name)
        self.__tool_bar.setCurrentAssetListName(name)
        self.__updateWidget()

    # }}}
    @QtCore.pyqtSlot()  # __onRename{{{
    def __onRename(self):
        logger.debug(f"{self.__class__.__name__}.__onRename()")

        # get current alist and save old name
        alist = self.__tree.currentAssetList()
        old_name = alist.name

        # get and check new name
        new_name = Dialog.name(old_name)
        if self.__tool_bar.isExist(new_name):
            Dialog.error("Name already exist.\nAssetList not renamed.")
            return

        # rename alist in database
        Thread.rename(alist, new_name)

        # remove old name from tool bar
        # add new name to tool bar, then update widget
        self.__tool_bar.removeAssetListName(old_name)
        self.__tool_bar.addAssetListName(new_name)
        self.__tool_bar.setCurrentAssetListName(new_name)
        self.__updateWidget()

    # }}}
    @QtCore.pyqtSlot()  # __onCopy{{{
    def __onCopy(self):
        logger.debug(f"{self.__class__.__name__}.__onCopy()")

        copy_name = Dialog.name("Copy list name")
        if self.__tool_bar.isExist(copy_name):
            Dialog.error("Name already exist.\nAssetList not copied.")
            return

        alist = self.__tree.currentAssetList()
        Thread.copy(alist, copy_name)
        self.__tool_bar.addAssetListName(copy_name)
        self.__tool_bar.setCurrentAssetListName(copy_name)
        self.__updateWidget()

    # }}}
    @QtCore.pyqtSlot()  # __onClear{{{
    def __onClear(self):
        logger.debug(f"{self.__class__.__name__}.__onClear()")

        if not Dialog.confirm():
            return

        alist = self.__tree.currentAssetList()
        alist.clear()
        Thread.save(alist)
        self.__updateWidget()

    # }}}
    @QtCore.pyqtSlot()  # __onDelete{{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.__onDelete()")

        if not Dialog.confirm():
            return

        alist = self.__tree.currentAssetList()
        self.__tool_bar.removeAssetListName(alist.name)
        Thread.delete(alist)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = AssetWidget()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
