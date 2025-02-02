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

from avin import (
    Trade,
    Usr,
    logger,
)


class TradeItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Date = 0
        Type = 1
        Ticker = 2
        Status = 3
        Result = 4
        PPD = 5

    # }}}
    def __init__(self, trade: Trade, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.trade = trade

        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )

        dt = trade.dt + Usr.TIME_DIF
        dt = dt.strftime("%Y-%m-%d  %H:%M")
        self.setText(self.Column.Date, dt)
        self.setText(self.Column.Type, trade.type.name)
        self.setText(self.Column.Ticker, trade.instrument.ticker)
        self.setText(self.Column.Status, trade.status.name)

        if trade.status == Trade.Status.CLOSED:
            self.setText(self.Column.Result, str(trade.result()))
            self.setText(self.Column.PPD, str(trade.percentPerDay()))

    # }}}


# }}}


if __name__ == "__main__":
    ...
