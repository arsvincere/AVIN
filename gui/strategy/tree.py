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

from avin.config import Usr
from avin.core import Strategy, StrategyList, StrategySet
from avin.utils import Cmd, logger
from gui.custom import Css, Dialog, Menu
from gui.strategy.dialog import StrategyAddDialog
from gui.strategy.item import (
    ConfigItem,
    StrategyItem,
    StrategySetNodeGroup,
    StrategySetNodeItem,
    VersionItem,
)


class StrategyTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__createActions()
        self.__createMenu()
        self.__config()
        self.__connect()

    # }}}

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.itemAt(e.pos())
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    # }}}
    def setStrategyList(self, slist: StrategyList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setStrategyList()")

        self.clear()
        for strategy in slist:
            item = StrategyItem(strategy, self)
            self.addTopLevelItem(item)

        self.__current_slist = slist

    # }}}
    def currentStrategyList(self) -> StrategyList:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentStrategyList()")

        return self.__current_alist

    # }}}

    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.__new = QtGui.QAction("New", self)
        self.__copy = QtGui.QAction("Copy", self)
        self.__edit = QtGui.QAction("Edit", self)
        self.__rename = QtGui.QAction("Rename", self)
        self.__delete = QtGui.QAction("Delete", self)

    # }}}
    def __createMenu(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenu()")

        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.__new)
        self.menu.addAction(self.__copy)
        self.menu.addAction(self.__edit)
        self.menu.addAction(self.__rename)
        self.menu.addAction(self.__delete)
        self.menu.setStyleSheet(Css.MENU)

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
        self.setColumnWidth(StrategyItem.Column.Name, 150)

        # config style
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__new.triggered.connect(self.__onNew)
        self.__copy.triggered.connect(self.__onCopy)
        self.__edit.triggered.connect(self.__onEdit)
        self.__rename.triggered.connect(self.__onRename)
        self.__delete.triggered.connect(self.__onDelete)

    # }}}
    def __setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")

        # disable all actions
        for i in self.menu.actions():
            i.setEnabled(False)

        # enable availible for this item
        if item is None:
            self.__new.setEnabled(True)
        elif isinstance(item, StrategyItem):
            self.__new.setEnabled(True)
            self.__rename.setEnabled(True)
            self.__delete.setEnabled(True)
        elif isinstance(item, ConfigItem):
            self.__edit.setEnabled(True)
        elif isinstance(item, VersionItem):
            self.__copy.setEnabled(True)
            self.__edit.setEnabled(True)
            self.__rename.setEnabled(True)
            self.__delete.setEnabled(True)

    # }}}

    @QtCore.pyqtSlot()  # __onNew{{{
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")

        name = Dialog.name("Enter strategy name")
        if not name:
            return

        new_strategy_item = StrategyItem.new(name)
        if new_strategy_item:
            self.addTopLevelItem(new_strategy_item)
        else:
            Dialog.error("Name alreade exist, creation canceled.")

    # }}}
    @QtCore.pyqtSlot()  # __onCopy{{{
    def __onCopy(self):
        logger.debug(f"{self.__class__.__name__}.__onCopy()")

        new_name = Dialog.name("New name...")
        if not new_name:
            return

        item = self.currentItem()
        new_version_item = VersionItem.copy(item, new_name)
        if new_version_item:
            strategy_item = item.parent()
            strategy_item.addChild(new_version_item)
        else:
            Dialog.error("Name alreade exist, coping canceled.")

    # }}}
    @QtCore.pyqtSlot()  # __onRename{{{
    def __onRename(self):
        logger.debug(f"{self.__class__.__name__}.__onRename()")

        new_name = Dialog.name("New name...")
        if not new_name:
            return

        item = self.currentItem()
        match item.__class__.__name__:
            case "StrategyItem":
                StrategyItem.rename(item, new_name)
            case "VersionItem":
                VersionItem.rename(item, new_name)

    # }}}
    @QtCore.pyqtSlot()  # __onEdit{{{
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onEdit()")

        item = self.currentItem()
        assert isinstance(item, (VersionItem, ConfigItem))

        command = (
            Usr.TERMINAL,
            *Usr.OPT,
            Usr.EXEC,
            Usr.EDITOR,
            item.path,
        )
        Cmd.subprocess(command)

    # }}}
    @QtCore.pyqtSlot()  # __onDelete{{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.__onDelete()")
        if not Dialog.confirm():
            return

        item = self.currentItem()
        match item.__class__.__name__:
            case "StrategyItem":
                index = self.indexFromItem(item).row()
                self.takeTopLevelItem(index)
                StrategyItem.delete(item)
            case "VersionItem":
                strategy_item = item.parent()
                index = strategy_item.indexOfChild(item)
                strategy_item.takeChild(index)
                VersionItem.delete(item)

    # }}}


# }}}
class StrategySetTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__createActions()
        self.__createMenu()
        self.__config()
        self.__connect()

    # }}}
    def __iter__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__iter__()")

        all_items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            all_items.append(item)

        return iter(all_items)

    # }}}
    def __contains__(self, strategy: Strategy):  # {{{
        logger.debug(f"{self.__class__.__name__}.__contains__()")

        for group in self:
            eq_name = group.strategy == strategy.name
            eq_ver = group.version == strategy.version
            if eq_name and eq_ver:
                return True

        return False

    # }}}
    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.itemAt(e.pos())
        self.__setVisibleActions(item)
        self.__menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    # }}}
    def setStrategySet(self, strategy_set: StrategySet) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setStrategySet()")

        # create strategy list
        slist = strategy_set.createStrategyList()

        # create asset list
        alist = strategy_set.createAssetList()

        # create items
        for strategy in slist:
            group_item = StrategySetNodeGroup(strategy)
            self.addTopLevelItem(strategy_item)
            for node in slist[strategy]:
                asset = alist.find(figi=node.figi)
                node_item = StrategySetNodeItem(node)
                node_item.setAsset(asset)
                group_item.addChild(node_item)

    # }}}

    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.__strategy_add = QtGui.QAction("Add", self)
        self.__strategy_remove = QtGui.QAction("Remove", self)

        self.__asset_add = QtGui.QAction("Add", self)
        self.__asset_remove = QtGui.QAction("Remove", self)
        self.__asset_clear = QtGui.QAction("Clear", self)
        self.__asset_info = QtGui.QAction("Info", self)

    # }}}
    def __createMenu(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenu()")

        self.__menu = Menu(parent=self)

        self.__menu.addTextSeparator("Strategy")
        self.__menu.addAction(self.__strategy_add)
        self.__menu.addAction(self.__strategy_remove)

        self.__menu.addTextSeparator("Asset")
        self.__menu.addAction(self.__asset_add)
        self.__menu.addAction(self.__asset_remove)
        self.__menu.addAction(self.__asset_clear)
        self.__menu.addAction(self.__asset_info)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config style
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)

        # config header
        labels = list()
        for l in StrategySetNodeItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(
            StrategySetNodeItem.Column.Name, Qt.SortOrder.AscendingOrder
        )

        # config width
        self.setColumnWidth(StrategySetNodeItem.Column.Name, 150)
        self.setColumnWidth(StrategySetNodeItem.Column.Figi, 150)
        self.setColumnWidth(StrategySetNodeItem.Column.Long, 50)
        self.setColumnWidth(StrategySetNodeItem.Column.Short, 50)
        self.setMinimumWidth(420)
        self.setMinimumHeight(200)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__strategy_add.triggered.connect(self.__onStrategyAdd)
        self.__strategy_remove.triggered.connect(self.__onStrategyRemove)

        self.__asset_add.triggered.connect(self.__onAssetAdd)
        self.__asset_remove.triggered.connect(self.__onAssetRemove)
        self.__asset_clear.triggered.connect(self.__onAssetClear)
        self.__asset_info.triggered.connect(self.__onAssetInfo)

    # }}}
    def __setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")

        # disable all actions
        for i in self.__menu.actions():
            i.setEnabled(False)

        # # enable availible for this item
        if item is None:
            self.__strategy_add.setEnabled(True)
        elif isinstance(item, StrategySetNodeGroup):
            self.__strategy_add.setEnabled(True)
            self.__strategy_remove.setEnabled(True)
            self.__asset_add.setEnabled(True)
            self.__asset_clear.setEnabled(True)
        elif isinstance(item, StrategySetNodeItem):
            self.__asset_add.setEnabled(True)
            self.__asset_remove.setEnabled(True)
            self.__asset_clear.setEnabled(True)
            self.__asset_info.setEnabled(True)

    # }}}

    @QtCore.pyqtSlot()  # __onStrategyAdd  # {{{
    def __onStrategyAdd(self):
        logger.debug(f"{self.__class__.__name__}.__onStrategyAdd()")

        dial = StrategyAddDialog()
        selected = dial.selectStrategys()
        for strategy in selected:
            if strategy not in self:
                group_item = StrategySetNodeGroup(strategy)
                self.addTopLevelItem(group_item)

    # }}}
    @QtCore.pyqtSlot()  # __onStrategyRemove  # {{{
    def __onStrategyRemove(self):
        logger.debug(f"{self.__class__.__name__}.__onStrategyRemove()")

        item = self.currentItem()
        index = self.indexFromItem(item).row()
        self.takeTopLevelItem(index)

    # }}}
    @QtCore.pyqtSlot()  # __onAssetAdd  # {{{
    def __onAssetAdd(self):
        logger.debug(f"{self.__class__.__name__}.__onAssetAdd()")

    # }}}
    @QtCore.pyqtSlot()  # __onAssetRemove  # {{{
    def __onAssetRemove(self):
        logger.debug(f"{self.__class__.__name__}.__onAssetRemove()")

    # }}}
    @QtCore.pyqtSlot()  # __onAssetClear  # {{{
    def __onAssetClear(self):
        logger.debug(f"{self.__class__.__name__}.__onAssetClear()")

    # }}}
    @QtCore.pyqtSlot()  # __onAssetInfo  # {{{
    def __onAssetInfo(self):
        logger.debug(f"{self.__class__.__name__}.__onAssetInfo()")

    # }}}


# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = StrategySetTree()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
