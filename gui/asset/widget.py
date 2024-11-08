#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


import asyncio
import sys
import time as timer

from PyQt6 import QtCore, QtWidgets

from avin.core import Asset, AssetList
from avin.utils import logger
from gui.asset.toolbar import AssetListToolBar
from gui.asset.tree import AssetListTree
from gui.custom import Css, Dialog


class _TRequestAll(QtCore.QThread):  # {{{
    def __init__(  # {{{
        self, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.all_list = list()

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__arequest())

    # }}}
    async def __arequest(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arequest()")

        self.all_list = await AssetList.requestAll()

    # }}}


# }}}
class _TLoad(QtCore.QThread):  # {{{
    def __init__(  # {{{
        self, name, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__name = name
        self.alist = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__aload())

    # }}}
    async def __aload(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__aload()")

        self.alist = await AssetList.load(self.__name)

    # }}}


# }}}


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
    def currentAssetList(self) -> AssetList:  # {{{
        return self.__current_alist

    # }}}
    def currentAsset(self) -> Asset:  # {{{
        return self.tree.currentAsset()

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

        if self.__isBusy():
            return

        self.__thread = _TRequestAll(self)
        self.__thread.finished.connect(self.__onRequestAllFinished)
        self.__thread.start()

    # }}}
    def __isBusy(self) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.__isBusy()")

        if self.__thread is not None:
            Dialog.info("Data manager is busy now, wait for complete task")
            return True

        return False

    # }}}
    @QtCore.pyqtSlot()  # __updateWidget  # {{{
    def __updateWidget(self):
        logger.debug(f"{self.__class__.__name__}.__updateWidget()")

        while self.__isBusy():
            timer.sleep(0.1)

        list_name = self.__tool_bar.currentAssetListName()
        self.__thread = _TLoad(list_name, self)
        self.__thread.finished.connect(self.__onLoadFinished)
        self.__thread.start()

    # }}}
    @QtCore.pyqtSlot()  # __onRequestAllFinished  # {{{
    def __onRequestAllFinished(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onRequestAllFinished()")

        all_list = self.__thread.all_list
        for list_name in all_list:
            self.__tool_bar.addAssetListName(list_name)

        del self.__thread
        self.__thread = None
        self.__updateWidget()

    # }}}
    @QtCore.pyqtSlot()  # __onLoadFinished  # {{{
    def __onLoadFinished(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onLoadFinished()")

        self.__current_alist = self.__thread.alist
        self.__tree.setAssetList(self.__current_alist)

        del self.__thread
        self.__thread = None

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
        alist = self.currentList()
        editor = Editor()
        edited_list = editor.editAssetList(alist)
        if edited_list:
            AssetList.save(edited_list)
            self.__updateWidget()

    # }}}
    @QtCore.pyqtSlot()  # __onNew{{{
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")

        name = Dialog.name("New list name")
        new_list = AssetList(name)
        AssetList.save(new_list)
        self.__tool_bar.addAssetListName(name)
        self.__tool_bar.setCurrentAssetList(name)
        self.updateWidget()

    # }}}
    @QtCore.pyqtSlot()  # __onCopy{{{
    def __onCopy(self):
        logger.debug(f"{self.__class__.__name__}.__onCopy()")
        copy_name = Dialog.name("Copy list name")
        IAssetList.copy(self.__current_list, copy_name)
        self.combobox_listname.addItem(copy_name)
        self.combobox_listname.setCurrentText(copy_name)
        self.updateWidget()

    # }}}
    @QtCore.pyqtSlot()  # __onRename{{{
    def __onRename(self):
        logger.debug(f"{self.__class__.__name__}.__onRename()")
        new_name = Dialog.name("New name")
        IAssetList.rename(self.__current_list, new_name)
        index = self.combobox_listname.currentIndex()
        self.combobox_listname.removeItem(index)
        self.combobox_listname.addItem(new_name)
        self.combobox_listname.setCurrentText(new_name)
        self.updateWidget()

    # }}}
    @QtCore.pyqtSlot()  # __onClear{{{
    def __onClear(self):
        logger.debug(f"{self.__class__.__name__}.__onClear()")
        if Dialog.confirm:
            IAssetList.delete(self.__current_list)
            self.__current_list.clear()
            IAssetList.save(self.__current_list)
            self.updateWidget()

    # }}}
    @QtCore.pyqtSlot()  # __onDelete{{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.__onDelete()")
        if Dialog.confirm():
            IAssetList.delete(self.__current_list)
            index = self.combobox_listname.currentIndex()
            self.combobox_listname.removeItem(index)
            self.updateWidget()

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = AssetWidget()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
