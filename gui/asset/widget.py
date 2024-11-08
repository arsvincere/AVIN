#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.const import ASSET_DIR
from avin.core import Asset
from avin.gui.custom import Dialog, Icon, Palette, ToolButton
from avin.utils import Cmd


class AssetWidget(QtWidgets.QWidget):
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
