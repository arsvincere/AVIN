#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets

from avin.utils import logger
from gui.custom.css import Css
from gui.custom.font import Font
from gui.custom.icon import Icon
from gui.custom.line_edit import LineEdit
from gui.custom.tool_button import ToolButton


class NameDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__lineedit = LineEdit("Enter name", self)
        self.__btn_ok = ToolButton(Icon.OK, self)
        self.__btn_cancel = ToolButton(Icon.CANCEL, self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.__btn_ok)
        btn_box.addWidget(self.__btn_cancel)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__lineedit)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    # }}}
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setFont(Font.MONO)

        sp = QtWidgets.QSizePolicy.Policy.Minimum
        self.setSizePolicy(sp, sp)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__btn_ok.clicked.connect(self.accept)
        self.__btn_cancel.clicked.connect(self.reject)

    # }}}
    def enterName(self, message: str) -> str | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.enterName()")

        self.__lineedit.setText(message)
        result = self.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            name = self.__lineedit.text()
            return name
        else:
            return None


# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = NameDialog()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.enterName("Enter name")
    app.exit(0)
