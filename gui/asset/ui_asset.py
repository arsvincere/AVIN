#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


import enum
import logging
import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.company import Tinkoff
from avin.const import ASSET_DIR, RES_DIR
from avin.core import Asset, AssetList, Exchange, Share, Type
from avin.gui.custom import Dialog, Font, Icon, Palette, ToolButton
from avin.utils import Cmd

sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
logger = logging.getLogger("LOGGER")


class IShare(Share, QtWidgets.QTreeWidgetItem):
    def __init__(self, ticker, exchange=Exchange.MOEX, parent=None):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Share.__init__(self, ticker, exchange, parent)
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(Tree.Column.Ticker, self.ticker)
        self.setText(Tree.Column.Name, self.name)
        self.setText(Tree.Column.Type, self.type.name)
        self.setText(Tree.Column.Exchange, self.exchange.name)

    @property
    def last_price(self):
        price = Tinkoff.getLastPrice(self)
        return price


class IAssetList(AssetList, QtWidgets.QTreeWidgetItem):
    def __init__(self, name="unnamed", parent=None):
        logger.debug("IAssetList.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        AssetList.__init__(self, name, parent)
        self.__parent = parent
        self.setFlags(
            Qt.ItemFlag.ItemIsAutoTristate
            | Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.__updateText()

    def __updateText(self):
        logger.debug(f"{self.__class__.__name__}.__updateText()")
        self.setText(Tree.Column.ListName, self.name)
        self.setText(Tree.Column.ListCount, str(self.count))

    @staticmethod  # load
    def load(path=None, name=None, parent=None):
        logger.debug("IAssetList.load()")
        if path:
            assert name is None
            name = Cmd.name(path, extension=False)
        elif name:
            assert path is None
            path = Cmd.join(ASSET_DIR, f"{name}.al")
        ialist = IAssetList(name, parent=parent)
        obj = Cmd.loadJSON(path)
        for ID in obj:
            assert eval(ID["type"]) == Type.SHARE
            ishare = IShare(ID["ticker"])
            ialist.add(ishare)
        return ialist

    def parent(self):
        logger.debug("IAssetList.parent()")
        return self.__parent

    def add(self, iasset: IShare):
        logger.debug("IAssetList.add()")
        assert isinstance(iasset, IShare)
        AssetList.add(self, iasset)
        self.__updateText()

    def remove(self, iasset):
        logger.debug("IAssetList.remove()")
        AssetList.remove(self, iasset)
        self.removeChild(iasset)
        self.__updateText()

    def clear(self):
        logger.debug(f"{self.__class__.__name__}.clear()")
        AssetList.clear(self)
        while self.takeChild(0):
            pass
        self.__updateText()


class Tree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Ticker = 0
        Name = 1
        Type = 2
        Exchange = 3
        ListName = 0
        ListCount = 1

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createMenu()
        self.__connect()

    def __iter__(self):
        items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            items.append(item)
        return iter(items)

    def __config(self):
        self.setHeaderLabels(["Ticker"])
        self.setSortingEnabled(True)
        self.sortByColumn(Tree.Column.Ticker, Qt.SortOrder.AscendingOrder)
        self.setFont(Font.MONO)

    def __createMenu(self):
        logger.debug(f"{self.__class__.__name__}.__createContextMenu()")
        self.action_add = QtGui.QAction("Add", self)
        self.action_remove = QtGui.QAction("Remove", self)
        self.action_info = QtGui.QAction("Info", self)
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_add)
        self.menu.addAction(self.action_remove)
        self.menu.addAction(self.action_info)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.menu.actions():
            i.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.action_add.setEnabled(True)
            self.action_remove.setEnabled(True)
        if isinstance(item, Asset):
            self.action_add.setEnabled(True)
            self.action_remove.setEnabled(True)
            self.action_info.setEnabled(True)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.action_add.triggered.connect(self.__onAdd)
        self.action_remove.triggered.connect(self.__onRemove)
        self.action_info.triggered.connect(self.__onInfo)

    @QtCore.pyqtSlot()  # __onAdd
    def __onAdd(self):
        logger.debug(f"{self.__class__.__name__}.__onAdd()")
        ialist = self.parent().currentList()
        editor = Editor()
        edited_list = editor.editAssetList(ialist)
        if edited_list:
            IAssetList.save(edited_list)
            self.parent().updateWidget()
            logger.info("Asset list saved")

    @QtCore.pyqtSlot()  # __onRemove
    def __onRemove(self):
        logger.debug(f"{self.__class__.__name__}.__onRemove()")
        item = self.currentItem()
        assert isinstance(item, IShare)
        ialist = item.parent()
        ialist.remove(item)
        IAssetList.save(ialist)

    @QtCore.pyqtSlot()  # __onInfo
    def __onInfo(self):
        logger.debug(f"{self.__class__.__name__}.__onInfo()")
        ...

    def contextMenuEvent(self, e):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.itemAt(e.pos())
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    def setAssetList(self, ialist: IAssetList):
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


class Editor(QtWidgets.QDialog):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__configTree()
        self.__connect()
        self.__initUI()
        self.__loadAssets()

    def __config(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tree = Tree(self)
        self.search_line = QtWidgets.QLineEdit(self)
        self.btn_search = ToolButton(Icon.SEARCH)
        self.btn_apply = ToolButton(Icon.APPLY)
        self.btn_cancel = ToolButton(Icon.CANCEL)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.btn_search)
        hbox.addWidget(self.search_line)
        hbox.addStretch()
        hbox.addWidget(self.btn_apply)
        hbox.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.tree)
        self.setLayout(vbox)

    def __configTree(self):
        logger.debug(f"{self.__class__.__name__}.__configTree()")
        labels = list()
        for i in Tree.Column:
            labels.append(i.name)
        self.tree.setHeaderLabels(labels)
        self.tree.setColumnWidth(Tree.Column.Ticker, 100)
        self.tree.setColumnWidth(Tree.Column.Name, 300)
        self.tree.setColumnWidth(Tree.Column.Type, 70)
        self.tree.setColumnWidth(Tree.Column.Exchange, 70)
        self.tree.setFixedWidth(600)
        self.tree.setMinimumHeight(400)

    def __connect(self):
        self.btn_apply.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def __initUI(self):
        logger.debug(f"{self.__class__.__name__}.__initUI()")
        self.search_line.setText("Enter ticker...")

    def __loadAssets(self):
        logger.debug(f"{self.__class__.__name__}.__loadAssets()")
        path = Cmd.join(RES_DIR, "share", "MOEX_ALL_ASSET_LIST")
        # path = Cmd.join(RES_DIR, "share", "MOEX_TINKOFF_XX5")
        self.full_alist = IAssetList.load(path)
        self.tree.setAssetList(self.full_alist)

    def __clearMark(self):
        logger.debug(f"{self.__class__.__name__}.__clearMark()")
        for i in self.tree:
            i.setCheckState(Tree.Column.Ticker, Qt.CheckState.Unchecked)

    def __markExisting(self, editable):
        logger.debug(f"{self.__class__.__name__}.__markExisting()")
        for asset in self.full_alist:
            if asset in editable:
                asset.setCheckState(Tree.Column.Ticker, Qt.CheckState.Checked)

    def editAssetList(self, editable: IAssetList) -> bool:
        logger.debug(f"{self.__class__.__name__}.editAssetList()")

        self.__clearMark()
        self.__markExisting(editable)
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            editable.clear()
            for i in self.tree:
                state = i.checkState(Tree.Column.Ticker)
                if state == Qt.CheckState.Checked:
                    index = self.tree.indexOfTopLevelItem(i)
                    item = self.tree.takeTopLevelItem(index)
                    editable.add(item)
            return editable

        logger.info("Cancel edit asset list")
        return False


class AssetWidget(QtWidgets.QWidget):
    """Signal"""

    assetChanged = QtCore.pyqtSignal(IShare)

    def __init__(self, parent=None):
        logger.debug("self.__class__.__name__.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__createSettingsMenu()
        self.__connect()
        self.__loadUserAssetLists()
        self.__initUI()

    def __createWidgets(self):
        logger.debug("self.__class__.__name__.__createWidgets()")
        self.combobox_listname = QtWidgets.QComboBox(self)
        self.btn_add = ToolButton(Icon.ADD)
        self.btn_settings = ToolButton(Icon.SETTINGS)
        self.tree = Tree(self)

    def __createLayots(self):
        logger.debug("self.__class__.__name__.__createLayots()")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.combobox_listname)
        hbox.addWidget(self.btn_add)
        hbox.addWidget(self.btn_settings)
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(hbox)
        vbox.addWidget(self.tree)
        self.setLayout(vbox)

    def __createSettingsMenu(self):
        logger.debug(f"{self.__class__.__name__}.__createToolMenu()")
        self.tool_new = QtGui.QAction(Icon.NEW, "New", self)
        self.tool_copy = QtGui.QAction(Icon.COPY, "Copy", self)
        self.tool_rename = QtGui.QAction(Icon.RENAME, "Rename", self)
        self.tool_clear = QtGui.QAction(Icon.CLEAR, "Clear", self)
        self.tool_delete = QtGui.QAction(Icon.THRASH, "Delete", self)
        self.tool_section = QtGui.QAction(Icon.SECTION, "Add section", self)
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.tool_new)
        self.menu.addAction(self.tool_copy)
        self.menu.addAction(self.tool_rename)
        self.menu.addAction(self.tool_clear)
        self.menu.addAction(self.tool_delete)
        self.menu.addAction(self.tool_section)
        self.btn_settings.setMenu(self.menu)
        self.btn_settings.setPopupMode(
            QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
        )

    def __connect(self):
        logger.debug("self.__class__.__name__.__connect()")
        self.combobox_listname.currentTextChanged.connect(self.updateWidget)
        self.tree.itemClicked.connect(self.__onItemClicked)
        self.btn_add.clicked.connect(self.__onButtonAdd)
        self.tool_new.triggered.connect(self.__onToolNew)
        self.tool_copy.triggered.connect(self.__onToolCopy)
        self.tool_rename.triggered.connect(self.__onToolRename)
        self.tool_clear.triggered.connect(self.__onToolClear)
        self.tool_delete.triggered.connect(self.__onToolDelete)
        self.tool_section.triggered.connect(self.__onToolSection)

    def __loadUserAssetLists(self):
        logger.debug("self.__class__.__name__.__loadUserAssetLists()")
        files = sorted(Cmd.getFiles(ASSET_DIR))
        for file_name in files:
            name = file_name.replace(".al", "")
            self.combobox_listname.addItem(name)

    def __initUI(self):
        logger.debug("self.__class__.__name__.__initUI()")
        self.combobox_listname.setCurrentText("XX5")
        iasset = self.tree.topLevelItem(0)
        self.tree.setCurrentItem(iasset)

    @QtCore.pyqtSlot()  # __onItemClicked
    def __onItemClicked(self):
        logger.debug(f"{self.__class__.__name__}.__onItemClicked()")
        item = self.tree.currentItem()
        if isinstance(item, Asset):
            self.assetChanged.emit(item)

    @QtCore.pyqtSlot()  # __onButtonAdd
    def __onButtonAdd(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonAdd()")
        ialist = self.currentList()
        editor = Editor()
        edited_list = editor.editAssetList(ialist)
        if edited_list:
            IAssetList.save(edited_list)
            self.updateWidget()

    @QtCore.pyqtSlot()  # __onToolNew
    def __onToolNew(self):
        logger.debug(f"{self.__class__.__name__}.__onToolNew()")
        name = Dialog.name("New list name")
        new_list = IAssetList(name)
        IAssetList.save(new_list)
        self.combobox_listname.addItem(name)
        self.combobox_listname.setCurrentText(name)
        self.updateWidget()

    @QtCore.pyqtSlot()  # __onToolCopy
    def __onToolCopy(self):
        logger.debug(f"{self.__class__.__name__}.__onToolCopy()")
        copy_name = Dialog.name("Copy list name")
        IAssetList.copy(self.__current_list, copy_name)
        self.combobox_listname.addItem(copy_name)
        self.combobox_listname.setCurrentText(copy_name)
        self.updateWidget()

    @QtCore.pyqtSlot()  # __onToolRename
    def __onToolRename(self):
        logger.debug(f"{self.__class__.__name__}.__onToolRename()")
        new_name = Dialog.name("New name")
        IAssetList.rename(self.__current_list, new_name)
        index = self.combobox_listname.currentIndex()
        self.combobox_listname.removeItem(index)
        self.combobox_listname.addItem(new_name)
        self.combobox_listname.setCurrentText(new_name)
        self.updateWidget()

    @QtCore.pyqtSlot()  # __onToolClear
    def __onToolClear(self):
        logger.debug(f"{self.__class__.__name__}.__onToolClear()")
        if Dialog.confirm:
            IAssetList.delete(self.__current_list)
            self.__current_list.clear()
            IAssetList.save(self.__current_list)
            self.updateWidget()

    @QtCore.pyqtSlot()  # __onToolDelete
    def __onToolDelete(self):
        logger.debug(f"{self.__class__.__name__}.__onToolDelete()")
        if Dialog.confirm():
            IAssetList.delete(self.__current_list)
            index = self.combobox_listname.currentIndex()
            self.combobox_listname.removeItem(index)
            self.updateWidget()

    @QtCore.pyqtSlot()  # __onToolSection
    def __onToolSection(self):
        logger.debug(f"{self.__class__.__name__}.__onToolSection()")
        logger.warning("This feature is unavailible, it will be added later")

    def updateWidget(self):
        logger.debug("self.__class__.__name__.updateWidget()")
        name = self.combobox_listname.currentText()
        self.__current_list = IAssetList.load(name=name)
        self.tree.setAssetList(self.__current_list)

    def currentList(self):
        return self.__current_list

    def currentAsset(self):
        return self.tree.currentItem()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = AssetWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())
