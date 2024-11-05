#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import enum
import logging
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from avin.const import STRATEGY_DIR, ASSET_DIR, EDITOR, TERMINAL, EXEC
from avin.core import Type, Share, AssetList
from avin.utils import Cmd
from avin.gui.custom import Icon, Font, Palette, ToolButton, Dialog
logger = logging.getLogger("LOGGER")

class IAssetCfg(Share, QtWidgets.QTreeWidgetItem):
    def __init__(self, asset, parent=None):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Share.__init__(self, ticker=asset.ticker)
        self.__config()
        self.__parent = parent
        self.asset = asset

    def __config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Name, self.ticker)


class IAssetListCfg(AssetList, QtWidgets.QTreeWidgetItem):
    def __init__(self, name, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        AssetList.__init__(self, name)
        self.__parent = parent
        self.setFlags(
            Qt.ItemFlag.ItemIsAutoTristate |
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.__updateText()

    def __updateText(self):
        logger.debug(f"{self.__class__.__name__}.__updateText()")
        self.setText(Tree.Column.Name, self.name)

    @staticmethod  #load
    def load(path=None, name=None, parent=None):
        logger.debug(f"{__class__.__name__}.load()")
        if path:
            assert name is None
            name = Cmd.name(path, extension=False)
        elif name:
            assert path is None
            path = Cmd.join(ASSET_DIR, f"{name}.al")
        ialist_cfg = IAssetListCfg("assets", parent=parent)
        obj = Cmd.loadJSON(path)
        for ID in obj:
            assert eval(ID["type"]) == Type.SHARE
            share = Share(ID["ticker"])
            cfg = IAssetCfg(share)
            ialist_cfg.add(cfg)
        return ialist_cfg

    def parent(self):
        logger.debug(f"{self.__class__.__name__}.parent()")
        return self.__parent

    def add(self, iasset: IAssetCfg):
        logger.debug(f"{self.__class__.__name__}.add()")
        AssetList.add(self, iasset)
        self.addChild(iasset)
        self.__updateText()

    def remove(self, iasset):
        logger.debug(f"{self.__class__.__name__}.remove()")
        AssetList.remove(self, iasset)
        self.removeChild(iasset)
        self.__updateText()

    def clear(self):
        logger.debug(f"{self.__class__.__name__}.clear()")
        AssetList.clear(self)
        while self.takeChild(0): pass
        self.__updateText()


class IStrategy(QtWidgets.QTreeWidgetItem):
    """ Const """
    ASSET = 0x0101  # user data role

    def __init__(self, dir_path, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.dir_path = dir_path
        self.name = Cmd.name(dir_path)
        self.__config()
        self.__loadLongList()
        self.__loadShortList()
        self.__createAssetListCfg()
        self.__loadConfig()
        self.__loadVersions()

    def __config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsAutoTristate |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Name, self.name)
        self.setCheckState(Tree.Column.Long, Qt.CheckState.Unchecked)
        self.setCheckState(Tree.Column.Short, Qt.CheckState.Unchecked)

    def __loadLongList(self):
        logger.debug(f"{self.__class__.__name__}.__loadLongList()")
        self.long_list_path = Cmd.join(self.dir_path, "long.al")
        try:
            self.long_list = AssetList.load(self.long_list_path)
        except FileNotFoundError:
            self.long_list = AssetList("long")
            AssetList.save(self.long_list, self.long_list_path)

    def __loadShortList(self):
        logger.debug(f"{self.__class__.__name__}.__loadShortList()")
        self.short_list_path = Cmd.join(self.dir_path, "short.al")
        try:
            self.short_list = AssetList.load(self.short_list_path)
        except FileNotFoundError:
            self.short_list = AssetList(f"short")
            AssetList.save(self.short_list, self.short_list_path)

    def __createAssetListCfg(self):
        logger.debug(f"{self.__class__.__name__}.__createChilds()")
        self.alist_cfg = IAssetListCfg.load(name="XX5", parent=self)
        self.alist_cfg.name = "assets"
        for asset in self.alist_cfg:
            self.__setCheckState(asset)

    def __setCheckState(self, item: IAssetCfg):
        if item in self.long_list:
            item.setCheckState(Tree.Column.Long, Qt.CheckState.Checked)
        else:
            item.setCheckState(Tree.Column.Long, Qt.CheckState.Unchecked)
        if item in self.short_list:
            item.setCheckState(Tree.Column.Short, Qt.CheckState.Checked)
        else:
            item.setCheckState(Tree.Column.Short, Qt.CheckState.Unchecked)

    def __loadConfig(self):
        logger.debug(f"{self.__class__.__name__}.__loadConfig()")
        file_path = Cmd.join(self.dir_path, "config.cfg")
        self.config_item = IConfig(path=file_path, parent=self)

    def __loadVersions(self):
        logger.debug(f"{self.__class__.__name__}.__loadVersions()")
        self.versions = QtWidgets.QTreeWidgetItem()
        self.versions.setText(Tree.Column.Name, "versions")
        files = Cmd.getFiles(self.dir_path, full_path=True)
        files = Cmd.select(files, extension=".py")
        for file_path in files:
            item = IVersion(path=file_path, parent=self.versions)
        self.addChild(self.versions)

    def saveAssetSettings(self):
        logger.debug(f"{self.__class__.__name__}.saveAssetSettings()")
        long_list = AssetList("long", parent=self)
        short_list = AssetList("short", parent=self)
        for i in range(self.alist_cfg.childCount()):
            item = self.alist_cfg.child(i)
            long_state = item.checkState(Tree.Column.Long)
            short_state = item.checkState(Tree.Column.Short)
            asset = item.asset
            if long_state == Qt.CheckState.Checked:
                long_list.add(asset)
            if short_state == Qt.CheckState.Checked:
                short_list.add(asset)
        AssetList.save(long_list, self.long_list_path)
        AssetList.save(short_list, self.short_list_path)

    @staticmethod  #rename
    def rename(istrategy, new_name):
        logger.debug(f"{__class__.__name__}.rename()")
        old_path = istrategy.dir_path
        new_path = Cmd.join(STRATEGY_DIR, new_name)
        Cmd.rename(old_path, new_path)
        istrategy.setText(Tree.Column.Name, new_name)
        istrategy.dir_path = new_path
        istrategy.config_item.path = Cmd.join(new_path, "config.cfg")
        for i in range(istrategy.versions.childCount()):
            item = istrategy.versions.child(i)
            item.path = Cmd.join(new_path, f"{item.version}.py")

    @staticmethod  #copy
    def copy(istrategy, new_name):
        logger.debug(f"{__class__.__name__}.copy()")
        old_path = istrategy.dir_path
        new_path = Cmd.join(STRATEGY_DIR, new_name)
        Cmd.copyDir(old_path, new_path)
        copy = IStrategy(new_path)
        return copy

    @staticmethod  #delete
    def delete(istrategy):
        logger.debug(f"{__class__.__name__}.delete()")
        Cmd.deleteDir(istrategy.dir_path)


class IConfig(QtWidgets.QTreeWidgetItem):
    def __init__(self, path, parent=None):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.path = path
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Name, "config")


class IVersion(QtWidgets. QTreeWidgetItem):
    def __init__(self, path, parent=None):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.path = path
        self.version = Cmd.name(path, extension=False)
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Name, self.version)

    @staticmethod  #rename
    def rename(iversion, new_name):
        old_path = iversion.path
        dir_path = Cmd.dirPath(iversion.path)
        new_path = Cmd.join(dir_path, f"{new_name}.py")
        Cmd.rename(old_path, new_path)
        iversion.setText(Tree.Column.Name, new_name)
        iversion.path = new_path

    @staticmethod  #copy
    def copy(iversion, new_name):
        old_path = iversion.path
        dir_path = Cmd.dirPath(iversion.path)
        new_path = Cmd.join(dir_path, f"{new_name}.py")
        Cmd.copyFile(old_path, new_path)
        copy = IVersion(new_path)
        return copy

    @staticmethod  #delete
    def delete(iversion):
        path = iversion.path
        Cmd.delete(path)


class Tree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Name =      0
        Long =      1
        Short =     2

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createEditor()
        self.__createActions()
        self.__createMenu()
        self.__connect()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(
            Tree.Column.Name,
            Qt.SortOrder.AscendingOrder
            )
        self.setColumnWidth(Tree.Column.Name, 150)
        self.setColumnWidth(Tree.Column.Long, 50)
        self.setColumnWidth(Tree.Column.Short, 50)
        self.setFont(Font.MONO)

    def __createEditor(self):
        self.editor = Editor()

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.__new =     QtGui.QAction("New", self)
        self.__copy =    QtGui.QAction("Copy", self)
        self.__edit =    QtGui.QAction("Edit", self)
        self.__rename =    QtGui.QAction("Rename", self)
        self.__delete =  QtGui.QAction("Delete", self)

    def __createMenu(self):
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.__new)
        self.menu.addAction(self.__copy)
        self.menu.addAction(self.__edit)
        self.menu.addAction(self.__rename)
        self.menu.addAction(self.__delete)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.__new.triggered.connect(self.__onNew)
        self.__copy.triggered.connect(self.__onCopy)
        self.__edit.triggered.connect(self.__onEdit)
        self.__rename.triggered.connect(self.__onRename)
        self.__delete.triggered.connect(self.__onDelete)
        self.itemChanged.connect(self.__onItemChanged)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.menu.actions():
            i.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.__new.setEnabled(True)
        elif isinstance(item, IStrategy):
            self.__new.setEnabled(True)
            self.__copy.setEnabled(True)
            self.__edit.setEnabled(False)
            self.__rename.setEnabled(True)
            self.__delete.setEnabled(True)
        elif isinstance(item, IConfig):
            self.__edit.setEnabled(True)
        elif isinstance(item, IVersion):
            self.__copy.setEnabled(True)
            self.__edit.setEnabled(True)
            self.__rename.setEnabled(True)
            self.__delete.setEnabled(True)

    @QtCore.pyqtSlot()  #__onNew
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")
        istrategy = self.editor.newStrategy()
        if istrategy:
            self.addTopLevelItem(istrategy)

    @QtCore.pyqtSlot()  #__onCopy
    def __onCopy(self):
        logger.debug(f"{self.__class__.__name__}.__onCopy()")
        item = self.currentItem()
        new_name = Dialog.name("New name...")
        if new_name:
            if isinstance(item, IStrategy):
                copy = IStrategy.copy(item, new_name)
                self.addTopLevelItem(copy)
            elif isinstance(item, IVersion):
                versions = item.parent()
                copy = IVersion.copy(item, new_name)
                versions.addChild(copy)

    @QtCore.pyqtSlot()  #__onEdit
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onEdit()")
        item = self.currentItem()
        path = item.path
        command = (TERMINAL, EXEC, EDITOR, path)
        Cmd.subprocess(command)

    @QtCore.pyqtSlot()  #__onRename
    def __onRename(self):
        logger.debug(f"{self.__class__.__name__}.__onRename()")
        item = self.currentItem()
        new_name = Dialog.name("New name...")
        if new_name:
            if isinstance(item, IStrategy):
                IStrategy.rename(item, new_name)
            elif isinstance(item, IVersion):
                IVersion.rename(item, new_name)

    @QtCore.pyqtSlot()  #__onDelete
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.__onDelete()")
        dial = Dialog.confirm()
        if dial.confirm():
            item = self.currentItem()
            if isinstance(item, IStrategy):
                index = self.indexFromItem(item).row()
                self.takeTopLevelItem(index)
                IStrategy.delete(item)
            elif isinstance(item, IVersion):
                istrategy = item.parent()
                index = istrategy.indexOfChild(item)
                istrategy.takeChild(index)
                IVersion.delete(item)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)  #__onItemChanged
    def __onItemChanged(self, item: QtWidgets.QTreeWidgetItem, column: int):
        logger.debug(f"{self.__class__.__name__}.__onItemChanged()")
        if not isinstance(item, IAssetCfg):
            return
        # else: item - IAssetCfg с измененным чек-стейт
        istrategy = item.parent().parent()
        istrategy.saveAssetSettings()

    def contextMenuEvent(self, e):
        logger.debug("Tree.contextMenuEvent(e)")
        item = self.itemAt(e.pos())
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()


class Editor(QtWidgets.QDialog):
    """ Const """
    __TEMPLATE = Cmd.join(STRATEGY_DIR, ".template")

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.lineedit_name = QtWidgets.QLineEdit("Enter strategy name", self)
        self.btn_ok = ToolButton(Icon.OK)
        self.btn_cancel = ToolButton(Icon.CANCEL)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.btn_ok)
        btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.lineedit_name)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    def __config(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def newStrategy(self):
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            name = self.lineedit_name.text()
            new_strategy_path = Cmd.join(STRATEGY_DIR, name)
            Cmd.copyDir(self.__TEMPLATE, new_strategy_path)
            istrategy = IStrategy(new_strategy_path)
            logger.info(f"Create new strategy '{istrategy.name}'")
            return istrategy
        else:
            logger.info(f"Cancel new strategy")
            return False


class StrategyWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logger.debug("UStrategyWidget.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserStrategy()

    def __createWidgets(self):
        logger.debug("UStrategyWidget.__createWidgets()")
        self.tree = Tree(self)

    def __createLayots(self):
        logger.debug("UStrategyWidget.__createLayots()")
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.tree)
        self.setLayout(vbox)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")

    def __loadUserStrategy(self):
        logger.debug(f"{self.__class__.__name__}.__loadUserStrategy()")
        dirs = Cmd.getDirs(STRATEGY_DIR, full_path=True)
        for path in dirs:
            name = Cmd.name(path)
            s = IStrategy(path)
            self.tree.addTopLevelItem(s)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = StrategyWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())

