#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin.const import RES_DIR
from avin.gui.custom import Icon, ToolButton
from avin.utils import Cmd


class Editor(QtWidgets.QDialog):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__configTree()
        self.__connect()
        self.__initUI()
        self.__loadAssets()

    # }}}
    def __config(self):  # {{{
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tree = Tree(self)
        self.search_line = QtWidgets.QLineEdit(self)
        self.btn_search = ToolButton(Icon.SEARCH)
        self.btn_apply = ToolButton(Icon.APPLY)
        self.btn_cancel = ToolButton(Icon.CANCEL)

    # }}}
    def __createLayots(self):  # {{{
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

    # }}}
    def __configTree(self):  # {{{
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

    # }}}
    def __connect(self):  # {{{
        self.btn_apply.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")
        self.search_line.setText("Enter ticker...")

    # }}}
    def __loadAssets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadAssets()")
        path = Cmd.join(RES_DIR, "share", "MOEX_ALL_ASSET_LIST")
        # path = Cmd.join(RES_DIR, "share", "MOEX_TINKOFF_XX5")
        self.full_alist = IAssetList.load(path)
        self.tree.setAssetList(self.full_alist)

    # }}}
    def __clearMark(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__clearMark()")
        for i in self.tree:
            i.setCheckState(Tree.Column.Ticker, Qt.CheckState.Unchecked)

    # }}}
    def __markExisting(self, editable):  # {{{
        logger.debug(f"{self.__class__.__name__}.__markExisting()")
        for asset in self.full_alist:
            if asset in editable:
                asset.setCheckState(Tree.Column.Ticker, Qt.CheckState.Checked)

    # }}}
    def editAssetList(self, editable: IAssetList) -> bool:  # {{{
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


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Editor()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
