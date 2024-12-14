#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin.core import Summary
from avin.utils import logger
from gui.custom import Css


class SummaryDockWidget(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDockWidget.__init__(self, "Summary", parent)

        self.widget = SummaryWidget(self)
        self.setWidget(self.widget)
        self.setStyleSheet(Css.DOCK_WIDGET)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
        )

        feat = QtWidgets.QDockWidget.DockWidgetFeature
        self.setFeatures(
            feat.DockWidgetMovable
            | feat.DockWidgetClosable
            | feat.DockWidgetFloatable
        )

        # }}}


# }}}
class SummaryWidget(QtWidgets.QTableWidget):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTableWidget.__init__(self, parent)

        self.rows = 1
        self.setRowCount(1)
        self.current_row = 0

        self.__config()
        self.__createHeader()
        self.__setColumnWidth()

    # }}}

    def showSummary(self, tlist):  # {{{
        logger.debug(f"{self.__class__.__name__}.showSummary()")

        self.__clear()
        df = Summary.calculate(tlist)
        for i in df.index:
            for n, val in enumerate(df.loc[i], 0):
                item = QtWidgets.QTableWidgetItem()
                if n != 0:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight
                        | Qt.AlignmentFlag.AlignVCenter
                    )
                item.setText(str(val))
                self.setItem(self.current_row, n, item)
            self.__addNewRow()

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.STYLE)
        self.setWindowTitle("AVIN")

    # }}}
    def __createHeader(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createHeader()")

        header = Summary.getHeader()
        self.setColumnCount(len(header))
        self.setHorizontalHeaderLabels(header)

    # }}}
    def __setColumnWidth(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setColumnWidth()")

        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 50)
        self.setColumnWidth(3, 50)
        self.setColumnWidth(4, 50)
        self.setColumnWidth(5, 50)
        self.setColumnWidth(6, 50)
        self.setColumnWidth(7, 50)
        self.setColumnWidth(8, 70)
        self.setColumnWidth(9, 70)
        self.setColumnWidth(10, 70)
        self.setColumnWidth(11, 70)
        self.setColumnWidth(12, 70)
        self.setColumnWidth(13, 100)
        self.setColumnWidth(14, 100)
        self.setColumnWidth(15, 50)

    # }}}
    def __addNewRow(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__addNewRow()")

        self.rows += 1
        self.current_row += 1
        self.setRowCount(self.rows)

    # }}}
    def __clear(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__clear()")

        self.rows = 1
        self.setRowCount(1)
        self.current_row = 0

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = SummaryWidget()
    w.show()
    sys.exit(app.exec())
