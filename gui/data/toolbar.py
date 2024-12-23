#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin import DataType, Date, logger
from gui.custom import (
    Css,
    Icon,
    Label,
    Menu,
    MonthWidget,
    Spacer,
    ToolButton,
    YearWidget,
)


class DataToolBar(QtWidgets.QToolBar):  # {{{
    __ICON_SIZE = QtCore.QSize(32, 32)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__createActions()
        self.__createButtons()
        self.__config()

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.download = QtGui.QAction(Icon.DOWNLOAD, "Download", self)
        self.convert = QtGui.QAction(Icon.CONVERT, "Convert", self)
        self.delete = QtGui.QAction(Icon.DELETE, "Delete", self)
        self.update = QtGui.QAction(Icon.UPDATE, "Update", self)

        self.addAction(self.download)
        self.addAction(self.convert)
        self.addAction(self.delete)
        self.addAction(self.update)

        actions = self.actions()
        for i in actions:
            btn = self.widgetForAction(i)
            btn.setStyleSheet(Css.TOOL_BUTTON)

    # }}}
    def __createButtons(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.viewer_btn = ToolButton(text="Viewer", width=80)
        self.close_btn = ToolButton(Icon.CLOSE, "Close", parent=self)

        self.addWidget(self.viewer_btn)
        self.addWidget(Spacer())
        self.addWidget(self.close_btn)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setIconSize(self.__ICON_SIZE)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.STYLE)

    # }}}


# }}}
class BarViewToolBar(QtWidgets.QWidget):  # {{{
    # NOTE:
    # этот тулбар сделан на основе виджета, иначе добавляемые
    # на него действия не ведут себя как полноценные виджеты
    # не работает self.month.hide()  self.month.show() например

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__createWidgets()
        self.__createLayouts()
        self.__config()
        self.__connect()

    # }}}

    def currentYear(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.currentYear()")

        return self.year.value()

    # }}}
    def currentMonth(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.currentMonth()")

        return self.month.value()

    # }}}

    def showMonthSelector(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.currentMonth()")

        self.month.show()

    # }}}
    def hideMonthSelector(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.currentMonth()")

        self.month.hide()

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.title = Label("| Bars Data:", parent=self)
        self.title.setStyleSheet(Css.TITLE)

        self.year = YearWidget("Year", Date.today().year, parent=self)
        self.month = MonthWidget("Month", 1, parent=self)
        self.month.hide()

        self.refresh_btn = ToolButton(Icon.REFRESH, parent=self)
        self.close_btn = ToolButton(Icon.CLOSE, "Close", parent=self)

    # }}}
    def __createLayouts(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.title)
        self.hbox.addWidget(Spacer(width=25))
        self.hbox.addWidget(self.year)
        self.hbox.addWidget(Spacer(width=25))
        self.hbox.addWidget(self.month)
        self.hbox.addStretch()
        self.hbox.addWidget(self.refresh_btn)
        self.hbox.addWidget(self.close_btn)
        self.setLayout(self.hbox)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.STYLE)
        self.setFixedHeight(45)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

    # }}}


# }}}
class _DataTypeMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        Menu.__init__(self, parent=parent)

        self.__config()
        self.__createActions()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setFixedWidth(64)

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.t_1M = QtGui.QAction("1M", self)
        self.t_5M = QtGui.QAction("5M", self)
        self.t_10M = QtGui.QAction("10M", self)
        self.t_1H = QtGui.QAction("1H", self)
        self.t_D = QtGui.QAction("D", self)
        self.t_W = QtGui.QAction("W", self)
        self.t_M = QtGui.QAction("M", self)

        self.t_1M.setData(DataType.BAR_1M)
        self.t_5M.setData(DataType.BAR_5M)
        self.t_10M.setData(DataType.BAR_10M)
        self.t_1H.setData(DataType.BAR_1H)
        self.t_D.setData(DataType.BAR_D)
        self.t_W.setData(DataType.BAR_W)
        self.t_M.setData(DataType.BAR_M)

        self.addAction(self.t_1M)
        self.addAction(self.t_5M)
        self.addAction(self.t_10M)
        self.addAction(self.t_1H)
        self.addAction(self.t_D)
        self.addAction(self.t_W)
        self.addAction(self.t_M)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = BarViewToolBar()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
