#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets

from avin.core import Asset
from avin.utils import logger
from gui.custom import Css, Icon, Label, TitleLabel, ToolButton


class AssetInfoDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}
    def showInfo(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.showInfo()")

        text = asset.pretty()
        self.__info_label.setText(text)
        self.exec()

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__title_label = TitleLabel("Asset info:", parent=self)
        self.__close_btn = ToolButton(Icon.CANCEL, parent=self)

        self.__info_label = Label("", parent=self)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.__title_label)
        hbox.addStretch()
        hbox.addWidget(self.__close_btn)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.__info_label)
        self.setLayout(vbox)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__close_btn.clicked.connect(self.reject)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = AssetInfoDialog()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
