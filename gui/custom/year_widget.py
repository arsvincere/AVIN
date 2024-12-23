#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.utils import logger
from gui.custom.css import Css
from gui.custom.icon import Icon
from gui.custom.label import Label
from gui.custom.line_edit import LineEdit
from gui.custom.tool_button import ToolButton


class YearWidget(QtWidgets.QWidget):  # {{{
    def __init__(self, name="", year=2000, width=50, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__name = name
        self.__year = year
        self.__width = width

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}

    def setYear(self, year: int):  # {{{
        logger.debug(f"{self.__class__.__name__}.setYear()")

        self.year_line_edit.setText(str(year))
        self.__year = year

    # }}}
    def value(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.value()")

        return self.__year

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.name_label = Label(self.__name, parent=self)
        self.year_line_edit = LineEdit(str(self.__year))

        self.plus_btn = ToolButton(Icon.ADD, width=16, height=16, parent=self)
        self.minus_btn = ToolButton(
            Icon.REMOVE, width=16, height=16, parent=self
        )

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.name_label)
        hbox.addWidget(self.minus_btn)
        hbox.addWidget(self.year_line_edit)
        hbox.addWidget(self.plus_btn)
        hbox.addStretch()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.year_line_edit.setFixedWidth(self.__width)
        self.year_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.year_line_edit.setStyleSheet(Css.LINE_EDIT)

        re = QtCore.QRegularExpression("[1-2][0-9][0-9][0-9]")
        validator = QtGui.QRegularExpressionValidator(re)
        self.year_line_edit.setValidator(validator)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.plus_btn.clicked.connect(self.__onPlus)
        self.minus_btn.clicked.connect(self.__onMinus)
        self.year_line_edit.textChanged.connect(self.__onChanged)

    # }}}

    @QtCore.pyqtSlot()  # __onPlus  # {{{
    def __onPlus(self):
        logger.debug(f"{self.__class__.__name__}.__onPlus()")

        self.__year += 1
        self.year_line_edit.setText(str(self.__year))

    # }}}
    @QtCore.pyqtSlot()  # __onMinus  # {{{
    def __onMinus(self):
        logger.debug(f"{self.__class__.__name__}.__onMinus()")

        self.__year -= 1
        self.year_line_edit.setText(str(self.__year))

    # }}}
    @QtCore.pyqtSlot()  # __onChanged  # {{{
    def __onChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onChanged()")

        text = self.year_line_edit.text()
        if text:
            self.__year = int(text)

    # }}}


# }}}
class MonthWidget(QtWidgets.QWidget):  # {{{
    def __init__(self, name="", month=1, width=50, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__name = name
        self.__month = month
        self.__width = width

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}

    def setMonth(self, month: int):  # {{{
        logger.debug(f"{self.__class__.__name__}.setYear()")

        self.month_line_edit.setText(str(month))
        self.__month = month

    # }}}
    def value(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.value()")

        return self.__month

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.name_label = Label(self.__name, parent=self)
        self.month_line_edit = LineEdit(str(self.__month))

        self.plus_btn = ToolButton(Icon.ADD, width=16, height=16, parent=self)
        self.minus_btn = ToolButton(
            Icon.REMOVE, width=16, height=16, parent=self
        )

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.name_label)
        hbox.addWidget(self.minus_btn)
        hbox.addWidget(self.month_line_edit)
        hbox.addWidget(self.plus_btn)
        hbox.addStretch()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.month_line_edit.setFixedWidth(self.__width)
        self.month_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_line_edit.setStyleSheet(Css.LINE_EDIT)

        re = QtCore.QRegularExpression("[0-9][0-9]")
        validator = QtGui.QRegularExpressionValidator(re)
        self.month_line_edit.setValidator(validator)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.plus_btn.clicked.connect(self.__onPlus)
        self.minus_btn.clicked.connect(self.__onMinus)
        self.month_line_edit.textChanged.connect(self.__onChanged)

    # }}}

    @QtCore.pyqtSlot()  # __onPlus  # {{{
    def __onPlus(self):
        logger.debug(f"{self.__class__.__name__}.__onPlus()")

        self.__month += 1
        self.month_line_edit.setText(str(self.__month))

    # }}}
    @QtCore.pyqtSlot()  # __onMinus  # {{{
    def __onMinus(self):
        logger.debug(f"{self.__class__.__name__}.__onMinus()")

        self.__month -= 1
        self.month_line_edit.setText(str(self.__month))

    # }}}
    @QtCore.pyqtSlot()  # __onChanged  # {{{
    def __onChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onChanged()")

        text = self.month_line_edit.text()
        if not text:
            val = 1
        else:
            val = int(text)

        if val > 12:
            val = 12
        if val < 1:
            val = 1

        self.__month = val
        self.month_line_edit.setText(str(self.__month))

    # }}}


# }}}


if __name__ == "__main__":
    ...
