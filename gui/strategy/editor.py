#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets

from avin.const import STRATEGY_DIR
from avin.gui.custom import Icon, ToolButton
from avin.utils import Cmd


class Editor(QtWidgets.QDialog):
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
            logger.info("Cancel new strategy")
            return False


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = StrategyWidget()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
