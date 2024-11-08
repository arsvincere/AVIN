#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.utils import logger
from gui.custom import Css, Icon, Menu, Spacer, ToolButton


class AssetListToolBar(QtWidgets.QToolBar):  # {{{
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

        # if this is the first, install the current
        if self.__current_list is None:
            self.setCurrentAssetListName(alist_name)

    # }}}
    def removeAssetListName(self, alist_name: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove()")

        self.__list_menu.remove(alist_name)

    # }}}
    def currentAssetListName(self) -> str:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentListName()")

        return self.__current_list

    # }}}
    def setCurrentAssetListName(self, alist_name: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setCurrentAssetListName()")

        if alist_name not in self.__list_menu:
            logger.error(
                f"AssetListToolBar.setCurrent: {alist_name} not found"
            )
            return

        self.__current_list_btn.setText(alist_name)
        self.__current_list = alist_name

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
        self.__list_menu = _AssetListNameMenu(self)
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
        menu = Menu(self)
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


class _AssetListNameMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        Menu.__init__(self, parent)

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

        logger.warning(
            f"_AssetListNameMenu.remove: '{alist_name}' not found!"
        )

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = AssetListToolBar()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
