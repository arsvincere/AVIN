#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


import enum
import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.core import Asset
from gui.custom import Font


class Tree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):  # {{{
        Ticker = 0
        Name = 1
        Type = 2
        Exchange = 3
        ListName = 0
        ListCount = 1

    # }}}
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createMenu()
        self.__connect()

    # }}}
    def __iter__(self):  # {{{
        items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            items.append(item)
        return iter(items)

    # }}}
    def __config(self):  # {{{
        self.setHeaderLabels(["Ticker"])
        self.setSortingEnabled(True)
        self.sortByColumn(Tree.Column.Ticker, Qt.SortOrder.AscendingOrder)
        self.setFont(Font.MONO)

    # }}}
    def __createMenu(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createContextMenu()")
        self.action_add = QtGui.QAction("Add", self)
        self.action_remove = QtGui.QAction("Remove", self)
        self.action_info = QtGui.QAction("Info", self)
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_add)
        self.menu.addAction(self.action_remove)
        self.menu.addAction(self.action_info)

    # }}}
    def __resetActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.menu.actions():
            i.setEnabled(False)

    # }}}
    def __setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.action_add.setEnabled(True)
            self.action_remove.setEnabled(True)
        if isinstance(item, Asset):
            self.action_add.setEnabled(True)
            self.action_remove.setEnabled(True)
            self.action_info.setEnabled(True)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.action_add.triggered.connect(self.__onAdd)
        self.action_remove.triggered.connect(self.__onRemove)
        self.action_info.triggered.connect(self.__onInfo)

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
    def contextMenuEvent(self, e):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.itemAt(e.pos())
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    # }}}
    def setAssetList(self, ialist: IAssetList):  # {{{
        logger.debug("Tree.setAssetList()")
        """ Если воспользовться функцией
        self.clear()
        то заодно будет вызван деструктор QTreeWidgetItem и в следующий
        раз когда снова выберу тот же самый лист в комбобоксе
        получится:
        RuntimeError: wrapped C/C++ object of type IShare has been deleted
        Aborted (core dumped)
        --
        Поэтому очищаю список через takeTopLevelItem
        """
        while self.takeTopLevelItem(0):
            pass
        for iasset in ialist:
            self.addTopLevelItem(iasset)


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Tree()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
