#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt


class InstrumentItem(QtWidgets.QTreeWidgetItem):
    class Column(enum.IntEnum):  # {{{
        Ticker = 0
        Name = 1
        Figi = 2
        Exchange = 3
        AssetType = 4

    # }}}
    def __init__(self, instrument: Instrument, parent=None):  # {{{
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.instrument = instrument

        self.setFlags(
            Qt.ItemFlag.ItemIsAutoTristate
            | Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setCheckState(self.Column.Ticker, Qt.CheckState.Unchecked)
        self.setText(self.Column.Ticker, instrument.ticker)
        self.setText(self.Column.Name, instrument.name)
        self.setText(self.Column.Exchange, instrument.exchange.name)
        self.setText(self.Column.AssetType, instrument.type.name)
        self.setText(self.Column.Figi, instrument.figi)

    # }}}
    def __str__(self):  # {{{
        return str(self.instrument)

    # }}}


class DataInfoItem(QtWidgets.QTreeWidgetItem):
    class Column(enum.IntEnum):  # {{{
        DataType = 0
        Begin = 1
        End = 2
        Source = 3

    # }}}
    def __init__(self, info: DataInfo, parent=None):  # {{{
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.info = info

        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setCheckState(self.Column.DataType, Qt.CheckState.Unchecked)

        self.setText(self.Column.DataType, info.data_type.name)
        self.setText(
            self.Column.Begin,
            f"{info.first_dt.strftime("%Y-%m-%d")}",
        )
        self.setText(
            self.Column.End,
            f"{info.last_dt.strftime("%Y-%m-%d")}",
        )
        self.setText(self.Column.Source, f"source {info.source.name}")

    # }}}


if __name__ == "__main__":
    ...
