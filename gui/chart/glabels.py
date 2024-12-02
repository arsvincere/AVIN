#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.config import Usr
from avin.const import WeekDays
from avin.utils import logger
from gui.custom import Font, Theme


class BarInfo(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configPalette()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.label_barinfo = QtWidgets.QLabel("BAR INFO")
        self.label_barinfo.setFont(Font.MONO)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.label_barinfo)

    # }}}
    def __configPalette(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__configPalette()")
        p = self.palette()
        p.setColor(QtGui.QPalette.ColorRole.Window, Theme.Chart.RED)
        self.setPalette(p)

    # }}}
    def set(self, bar):  # {{{
        logger.debug(f"{self.__class__.__name__}.set(bar)")
        msk_time = (bar.dt + Usr.TIME_DIF).strftime("%Y-%m-%d %H:%M")
        day = WeekDays[bar.dt.weekday()]
        body = bar.body.percent()
        self.label_barinfo.setText(
            f"{msk_time} {day} - Open: {bar.open:<6} High: {bar.high:<6} "
            f"Low: {bar.low:<6} Close: {bar.close:<6} (Body: {body:.2f}%)"
        )


# }}}


# }}}
class VolumeInfo(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configPalette()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.label_volinfo = QtWidgets.QLabel("VOL INFO")
        self.label_volinfo.setFont(Font.MONO)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.label_volinfo)
        vbox.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __configPalette(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__configPalette()")
        p = self.palette()
        p.setColor(QtGui.QPalette.ColorRole.Window, Theme.Chart.RED)
        self.setPalette(p)

    # }}}
    def set(self, bar):  # {{{
        logger.debug(f"{self.__class__.__name__}.set(bar)")
        self.label_volinfo.setText(f"Vol: {bar.vol}")


# }}}


# }}}
class ChartLabels(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.__configPalette()

    # }}}
    def __configPalette(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__configPalette()")
        # p = self.palette()
        # p.setColor(QtGui.QPalette.ColorRole.Window, Color.NONE)
        # self.setPalette(p)

    # }}}
    def add(self, widget):  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")
        self.vbox.addWidget(widget)

    # }}}
    def remove(self, widget):  # {{{
        logger.debug(f"{self.__class__.__name__}.remove()")
        self.vbox.removeWidget(widget)


# }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ChartWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
