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
from gui.custom.font import Font
from gui.custom.icon import Icon
from gui.custom.tool_button import ToolButton


class InfoDialog(QtWidgets.QDialog):
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
        self.__message_label = QtWidgets.QLabel(self)
        self.__btn_ok = ToolButton(Icon.OK, self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.__btn_ok)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__message_label)
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

    # }}}
    def info(self, message: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.info()")

        self.__message_label.setText(message)
        self.exec()


# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = InfoDialog()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.info("Info message!")
    app.exit(0)
