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
from gui.asset.dialog_select import AssetSelectDialog
from gui.asset.item import AssetItem
from gui.asset.thread import Thread
from gui.custom import Css, Dialog, Icon, Menu, Spacer, ToolButton


class AssetListWidget(QtWidgets.QWidget):  # {{{
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

        self.__tool_bar = _AssetListToolBar(self)
        self.__tree = _AssetListTree(self)

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


# }}}
class _AssetListToolBar(QtWidgets.QToolBar):  # {{{
    listChanged = QtCore.pyqtSignal()
    __ICON_SIZE = QtCore.QSize(32, 32)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__createActions()
        self.__createListButton()
        self.__createAddButton()
        self.__createOtherButton()
        self.__config()
        self.__connect()

    # }}}

    def addAssetListName(self, alist_name: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")

        self.__list_menu.add(alist_name)

        # if this is the first, set the current
        if self.__current_list is None:
            self.setCurrentAssetListName(alist_name)

    # }}}
    def removeAssetListName(self, alist_name: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove()")

        self.__list_menu.remove(alist_name)

        # set first list as current if exist
        actions = self.__list_menu.actions()
        if len(actions) > 0:
            alist_name = actions[0].data()
            self.setCurrentAssetListName(alist_name)

    # }}}
    def currentAssetListName(self) -> str:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentListName()")

        return self.__current_list

    # }}}
    def setCurrentAssetListName(self, alist_name: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setCurrentAssetListName()")

        if alist_name not in self.__list_menu:
            logger.error(
                f"_AssetListToolBar.setCurrent: {alist_name} not found"
            )
            return

        self.__current_list_btn.setText(alist_name)
        self.__current_list = alist_name

    # }}}
    def isExist(self, alist_name) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.isExist()")

        existed = alist_name in self.__list_menu
        return existed

    # }}}

    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.action_add = QtGui.QAction(Icon.ADD, "Add", self)
        self.action_new = QtGui.QAction(Icon.NEW, "New", self)
        self.action_rename = QtGui.QAction(Icon.RENAME, "Rename", self)
        self.action_copy = QtGui.QAction(Icon.COPY, "Copy", self)
        self.action_clear = QtGui.QAction(Icon.CLEAR, "Clear", self)
        self.action_delete = QtGui.QAction(Icon.THRASH, "Delete", self)

    # }}}
    def __createListButton(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createListButton()")

        # create current list button
        self.__current_list_btn = ToolButton(width=128, parent=self)
        self.__current_list_btn.setText("List: None")
        self.__current_list = None
        self.addWidget(self.__current_list_btn)

        # add spacer
        self.addWidget(Spacer())

        # create menu for current list
        self.__list_menu = _AssetListMenu(self)
        self.__current_list_btn.setMenu(self.__list_menu)
        self.__current_list_btn.setPopupMode(
            QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
        )

    # }}}
    def __createAddButton(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createAddButton()")

        self.addAction(self.action_add)
        self.widgetForAction(self.action_add).setStyleSheet(Css.TOOL_BUTTON)

    # }}}
    def __createOtherButton(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createOtherButton()")

        # create other button
        self.__other_btn = ToolButton(Icon.OTHER, parent=self)
        self.addWidget(self.__other_btn)

        # menu for other_btn
        menu = Menu(parent=self)
        menu.addAction(self.action_new)
        menu.addAction(self.action_rename)
        menu.addAction(self.action_copy)
        menu.addAction(self.action_clear)
        menu.addAction(self.action_delete)
        self.__other_btn.setMenu(menu)
        self.__other_btn.setPopupMode(
            QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
        )

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.STYLE)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__list_menu.triggered.connect(self.__onListTriggered)

    # }}}

    @QtCore.pyqtSlot(QtGui.QAction)  # __onListTriggered{{{
    def __onListTriggered(self, action: QtGui.QAction):
        logger.debug(f"{self.__class__.__name__}.__onListTriggered()")

        list_name = action.data()
        if self.__current_list != list_name:
            self.__current_list = list_name
            self.__current_list_btn.setText(list_name)
            self.listChanged.emit()

    # }}}


# }}}
class _AssetListMenu(QtWidgets.QMenu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        QtWidgets.QMenu.__init__(self, parent)

        self.__config()

    # }}}
    def __contains__(self, alist_name: str) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.__contains__()")

        for i in self.actions():
            if i.data() == alist_name:
                return True

        return False

    # }}}
    def add(self, alist_name: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add({alist_name})")

        action = QtGui.QAction(alist_name, self)
        action.setData(alist_name)
        self.addAction(action)

    # }}}
    def remove(self, alist_name: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove({alist_name})")

        for i in self.actions():
            if i.data() == alist_name:
                self.removeAction(i)
                return

        logger.warning(f"_AssetListMenu.remove: '{alist_name}' not found!")

    # }}}
    def __config(self):  # {{{
        self.setStyleSheet(Css.MENU)


# }}}


# }}}
class _AssetListTree(QtWidgets.QTreeWidget):  # {{{
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

        dial = AssetSelectDialog()
        edited_list = dial.editAssetList(self.__current_alist)
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
    def __setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")

        # disable all actions
        for i in self.__menu.actions():
            i.setEnabled(False)

        # enable availible for this item
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


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = AssetListWidget()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
