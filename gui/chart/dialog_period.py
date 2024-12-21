#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin import UTC, Date, DateTime, Time, logger
from gui.custom import Css, Icon, Label, LineEdit, Spacer, ToolButton


class ChartPeriodDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

    # }}}
    def selectPeriod(self) -> tuple:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectFilter()")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None, None

        begin = DateTime.combine(
            date=self.__begin_dateedit.date().toPyDate(),
            time=Time(0, 0),
            tzinfo=UTC,
        )
        end = DateTime.combine(
            date=self.__end_dateedit.date().toPyDate(),
            time=Time(0, 0),
            tzinfo=UTC,
        )
        return begin, end

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__toolbar = _ToolBar(self)
        self.__begin_dateedit = QtWidgets.QDateEdit(parent=self)
        self.__end_dateedit = QtWidgets.QDateEdit(parent=self)
        self.__center_dateedit = QtWidgets.QDateEdit(parent=self)
        self.__bar_count_widget = _BarCountWidget(
            "bars count", count=100, width=50
        )

        self.__begin_dateedit.setDisplayFormat("yyyy-MM-dd")
        self.__begin_dateedit.setDate(Date(2018, 1, 1))

        self.__end_dateedit.setDisplayFormat("yyyy-MM-dd")
        self.__end_dateedit.setDate(Date(2023, 1, 1))

        # TODO: а оно вообще надо?
        self.__center_dateedit.setDisplayFormat("yyyy-MM-dd")
        self.__center_dateedit.setDate(Date(2020, 1, 1))
        self.__center_dateedit.hide()
        self.__bar_count_widget.hide()

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.__begin_dateedit)
        hbox1.addWidget(self.__end_dateedit)

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.__center_dateedit)
        hbox2.addWidget(self.__bar_count_widget)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__toolbar)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__toolbar.btn_ok.clicked.connect(self.accept)
        self.__toolbar.btn_cancel.clicked.connect(self.reject)

    # }}}


# }}}
class _ToolBar(QtWidgets.QToolBar):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__createWidgets()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        title = Label("| Chart period:", parent=self)
        title.setStyleSheet(Css.TITLE)
        self.addWidget(title)
        self.addWidget(Spacer())

        self.btn_ok = ToolButton(Icon.OK, "Ok", parent=self)
        self.btn_cancel = ToolButton(Icon.CANCEL, "Cancel", parent=self)
        self.addWidget(self.btn_ok)
        self.addWidget(self.btn_cancel)

    # }}}


# }}}
class _BarCountWidget(QtWidgets.QWidget):  # {{{
    def __init__(self, name="", count=2000, width=50, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__name = name
        self.__count = count
        self.__width = width

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}
    def setYear(self, count: int):  # {{{
        logger.debug(f"{self.__class__.__name__}.setYear()")

        self.year_line_edit.setText(str(count))
        self.__count = count

    # }}}
    def value(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.value()")

        return self.__count

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.name_label = Label(self.__name, parent=self)
        self.year_line_edit = LineEdit(str(self.__count))

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
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.year_line_edit.setFixedWidth(self.__width)
        self.year_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.year_line_edit.setStyleSheet(Css.LINE_EDIT)

        re = QtCore.QRegularExpression("[0-9][0-9][0-9][0-9]")
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

        self.__count += 100
        self.year_line_edit.setText(str(self.__count))

    # }}}
    @QtCore.pyqtSlot()  # __onMinus  # {{{
    def __onMinus(self):
        logger.debug(f"{self.__class__.__name__}.__onMinus()")

        self.__count -= 100
        self.year_line_edit.setText(str(self.__count))

    # }}}
    @QtCore.pyqtSlot()  # __onChanged  # {{{
    def __onChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onChanged()")

        text = self.year_line_edit.text()
        if text:
            self.__count = int(text)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ChartPeriodDialog()
    w.show()
    sys.exit(app.exec())
