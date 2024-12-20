#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtGui, QtWidgets

from avin.config import Usr
from avin.const import WeekDays
from avin.utils import logger
from gui.custom import Css, Font, Theme


class BarInfo(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsWidget.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__configPalette()

    # }}}

    def set(self, gbar):  # {{{
        logger.debug(f"{self.__class__.__name__}.set(bar)")

        b = gbar.bar
        local_time = Usr.localTime(b.dt)
        day = WeekDays(b.dt.weekday()).name
        percent = b.body.percent()

        self.label_barinfo.setText(
            f"{local_time} {day} - "
            f"Open: {b.open:<6} "
            f"High: {b.high:<6} "
            f"Low: {b.low:<6} "
            f"Close: {b.close:<6} "
            f"(Body: {percent:.2f}%)"
        )

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.label_barinfo = QtWidgets.QLabel()
        self.label_barinfo.setText(
            "[date-time] [day] - "
            "Open: ____ "
            "High: ____ "
            "Low: ____ "
            "Close: ____ "
            "(Body: __%)"
        )

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


# }}}
class VolumeInfo(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsWidget.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__configPalette()

    # }}}

    def set(self, gbar):  # {{{
        logger.debug(f"{self.__class__.__name__}.set(bar)")

        self.label_volinfo.setText(f"Volume: {gbar.bar.vol}")

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.label_volinfo = QtWidgets.QLabel("Volume: ")
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


# }}}


class ChartLabels(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsProxyWidget.__init__(self, parent)

        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)
        self.setStyleSheet(Css.CHART_LABEL)

    # }}}

    def add(self, widget: QtWidgets.QWidget) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")

        self.vbox.addWidget(widget)

    # }}}
    def remove(self, widget: QtWidgets.QWidget) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove()")

        self.vbox.removeWidget(widget)

    # }}}


# }}}


if __name__ == "__main__":
    ...
