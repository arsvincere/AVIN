#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtWidgets

from avin.utils import logger
from gui.custom.css import Css


class Menu(QtWidgets.QMenu):
    def __init__(self, title=None, parent=None):  # {{{
        QtWidgets.QMenu.__init__(self, parent)

        if title:
            self.setTitle(title)

        self.setStyleSheet(Css.MENU)

    # }}}
    def addTextSeparator(self, text: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.addTextSeparator()")

        text_label = QtWidgets.QLabel(text)
        # text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet(Css.MENU_SECTION)
        sep = QtWidgets.QWidgetAction(self)
        sep.setDefaultWidget(text_label)
        self.addAction(sep)

        # // possible alignment

    # }}}


if __name__ == "__main__":
    ...
