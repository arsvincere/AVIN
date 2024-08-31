#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import logging
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from avin.core import Report
from avin.gui.custom import Palette, Font
logger = logging.getLogger("LOGGER")


class ReportWidget(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        QtWidgets.QTableWidget.__init__(self, parent)
        self.setFont(Font.MONO)
        self.rows = 1
        self.setRowCount(1)
        self.current_row = 0
        self.__createHeader()
        self.__setColumnWidth()

    def __setColumnWidth(self):
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

    def __addNewRow(self):
        self.rows += 1
        self.current_row += 1
        self.setRowCount(self.rows)

    def __createHeader(self) -> None:
        header = Report.getHeader()
        self.setColumnCount(len(header))
        self.setHorizontalHeaderLabels(header)

    def __clear(self):
        self.rows = 1
        self.setRowCount(1)
        self.current_row = 0

    def showSummary(self, itlist):
        self.__clear()
        df = Report.calculate(itlist)
        for i in df.index:
            for n, val in enumerate(df.loc[i], 0):
                item = QtWidgets.QTableWidgetItem()
                if n != 0:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight |
                        Qt.AlignmentFlag.AlignVCenter
                        )
                item.setText(str(val))
                self.setItem(self.current_row, n, item)
            self.__addNewRow()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = ReportWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())

