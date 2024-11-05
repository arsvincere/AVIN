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
from gui.custom.label import Label
from gui.custom.tool_button import ToolButton


class ConfirmDialog(QtWidgets.QDialog):
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

        self.__message_label = Label(parent=self)
        self.__btn_ok = ToolButton(Icon.OK, parent=self)
        self.__btn_cancel = ToolButton(Icon.CANCEL, parent=self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.__btn_ok)
        btn_box.addWidget(self.__btn_cancel)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__message_label)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    # }}}
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setFont(Font.MONO)
        self.setStyleSheet(Css.DIALOG)

        sp = QtWidgets.QSizePolicy.Policy.Minimum
        self.setSizePolicy(sp, sp)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__btn_ok.clicked.connect(self.accept)
        self.__btn_cancel.clicked.connect(self.reject)

    # }}}
    def confirm(self, message: str) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.confirm()")
        self.__message_label.setText(message)
        result = self.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            return True
        else:
            return False

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ConfirmDialog()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.confirm("Are you serious?")
    app.exit(0)
