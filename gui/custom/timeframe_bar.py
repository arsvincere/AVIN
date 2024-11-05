#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.core import TimeFrame, TimeFrameList
from avin.utils import logger
from gui.custom.css import Css


class TimeFrameBar(QtWidgets.QToolBar):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__size = QtCore.QSize(32, 32)

        self.__config()
        self.__connect()

    # }}}
    def add(self, timeframe: TimeFrame) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")

        action = QtGui.QAction(text=str(timeframe), parent=self)
        action.setData(timeframe)
        action.setProperty("selected", False)
        self.addAction(action)

        btn = self.widgetForAction(action)
        btn.setStyleSheet(Css.TOOL_BUTTON)
        btn.setCheckable(True)
        btn.setFixedSize(self.__size)
        btn.setIconSize(self.__size)

    # }}}
    def selected(self) -> TimeFrameList:  # {{{
        logger.debug(f"{self.__class__.__name__}.timeframes()")

        selected = TimeFrameList()
        for i in self.actions():
            if i.property("selected"):
                timeframe = i.data()
                selected.add(timeframe)

        return selected

    # }}}
    def setSelected(self, timeframe: TimeFrame) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")

        for i in self.actions():
            if i.data() == timeframe:
                i.setProperty("selected", True)
                btn = self.widgetForAction(i)
                btn.setChecked(True)
                return

        assert False, "TimeFrame not in bar"

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.STYLE)
        # sp = QtWidgets.QSizePolicy.Policy.Expanding
        # self.setSizePolicy(sp, sp)
        # self.setFixedSize(200, 40)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.actionTriggered.connect(self.__onTriggered)

    # }}}
    @QtCore.pyqtSlot(QtGui.QAction)  # __onTriggered  # {{{
    def __onTriggered(self, action: QtGui.QAction):
        logger.debug(f"{self.__class__.__name__}.__onTriggered()")

        btn = self.widgetForAction(action)
        state = btn.isChecked()
        btn.setChecked(not state)
        action.setProperty("selected", not state)

        # }}}


if __name__ == "__main__":
    ...
