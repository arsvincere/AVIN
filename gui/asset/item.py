#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


import enum

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from avin.core import Asset, AssetList
from avin.utils import logger


class AssetItem(QtWidgets.QTreeWidgetItem):
    class Column(enum.IntEnum):  # {{{
        Ticker = 0
        Name = 1
        Exchange = 3
        Type = 2
        Figi = 4

    # }}}

    def __init__(self, asset: Asset, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.asset = asset

        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )

        self.setText(self.Column.Ticker, asset.ticker)
        self.setText(self.Column.Name, asset.name)
        self.setText(self.Column.Type, asset.type.name)
        self.setText(self.Column.Exchange, asset.exchange.name)

    # }}}

    def isChecked(self) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.isChecked()")

        check_state = self.checkState(self.Column.Ticker)

        return check_state == Qt.CheckState.Checked

    # }}}


class AssetListItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, alist: AssetList, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.alist = alist
        self.setFlags(
            Qt.ItemFlag.ItemIsAutoTristate
            | Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )

    # }}}


if __name__ == "__main__":
    ...
