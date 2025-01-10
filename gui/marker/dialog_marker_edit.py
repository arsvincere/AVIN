#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.utils import logger
from gui.custom import (
    Css,
    Icon,
    Label,
    PushButton,
    Spacer,
    ToolButton,
)
from gui.filter.dialog_select import FilterSelectDialog
from gui.marker.dialog_shape_select import ShapeSelectDialog
from gui.marker.mark import Mark


class MarkerEditDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createForm()
        self.__createLayots()
        self.__connect()

        self.__current_filter = None
        self.__current_gshape = None

        self.__filter_select_dialog = None

    # }}}

    def newMark(self) -> Mark | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.newMark()")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        if self.__current_filter is None:
            return None
        if self.__current_gshape is None:
            return None

        m = Mark(
            self.__current_filter,
            self.__current_gshape,
        )
        return m

    # }}}
    def editMark(self, mark: Mark) -> Mark | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.editMark()")

        # read mark in UI
        self.__current_filter = mark.filter
        self.__filter_btn.setText(mark.filter.name)

        self.__current_gshape = mark.shape
        icon = QtGui.QIcon(mark.shape.pixmap())
        self.__shape_btn.setText("")
        self.__shape_btn.setIcon(icon)

        # exec dialog
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        if self.__current_filter is None:
            return None
        if self.__current_gshape is None:
            return None

        # create and return mark
        mark = Mark(
            self.__current_filter,
            self.__current_gshape,
        )
        return mark

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__toolbar = _MarkerToolBar(self)
        self.__filter_btn = PushButton(text="Click to select")
        self.__shape_btn = PushButton(text="Click to select")

    # }}}
    def __createForm(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createForm()")

        form = QtWidgets.QFormLayout()
        form.addRow("Filter", self.__filter_btn)
        form.addRow("Shape", self.__shape_btn)
        self.__form = form

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__toolbar)
        vbox.addLayout(self.__form)

        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__toolbar.btn_ok.clicked.connect(self.accept)
        self.__toolbar.btn_cancel.clicked.connect(self.reject)

        self.__filter_btn.clicked.connect(self.__onFilterBtn)
        self.__shape_btn.clicked.connect(self.__onShapeBtn)

    # }}}

    @QtCore.pyqtSlot()  # __onFilterBtn  # {{{
    def __onFilterBtn(self):
        logger.debug(f"{self.__class__.__name__}.__onFilterBtn()")

        if self.__filter_select_dialog is None:
            self.__filter_select_dialog = FilterSelectDialog()

        f = self.__filter_select_dialog.selectFilter()
        if f is None:
            self.__filter_btn.setText("Click to select")
            return
        else:
            self.__filter_btn.setText(f.name)
            self.__current_filter = f

    # }}}
    @QtCore.pyqtSlot()  # __onShapeBtn  # {{{
    def __onShapeBtn(self):
        logger.debug(f"{self.__class__.__name__}.__onShapeBtn()")

        dial = ShapeSelectDialog()
        gshape = dial.selectGShape()
        if gshape is None:
            self.__shape_btn.setText("Click to select")
            return
        else:
            icon = QtGui.QIcon(gshape.pixmap())
            self.__shape_btn.setText("")
            self.__shape_btn.setIcon(icon)
            self.__current_gshape = gshape

    # }}}


# }}}
class _MarkerToolBar(QtWidgets.QToolBar):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__createWidgets()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        title = Label("| Add mark:", parent=self)
        title.setStyleSheet(Css.TITLE)
        self.addWidget(title)
        self.addWidget(Spacer())

        self.btn_ok = ToolButton(Icon.OK, "Ok", parent=self)
        self.btn_cancel = ToolButton(Icon.CANCEL, "Cancel", parent=self)
        self.addWidget(self.btn_ok)
        self.addWidget(self.btn_cancel)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MarkerEditDialog()
    w.show()
    sys.exit(app.exec())
