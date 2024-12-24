#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin import logger


class MarkItem(QtWidgets.QTreeWidgetItem):
    class Column(enum.IntEnum):  # {{{
        Filter = 0
        Shape = 1

    # }}}

    def __init__(self, mark: Mark, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.mark = mark

        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setCheckState(self.Column.Filter, Qt.CheckState.Unchecked)

        self.setText(self.Column.Filter, mark.filter.name)
        icon = QtGui.QIcon(mark.shape.pixmap())
        self.setIcon(self.Column.Shape, icon)

    # }}}

    def isChecked(self) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.isChecked()")

        check_state = self.checkState(self.Column.Filter)

        return check_state == Qt.CheckState.Checked

    # }}}


if __name__ == "__main__":
    ...
