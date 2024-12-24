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
    LineEdit,
    PushButton,
    Spacer,
    ToolButton,
)
from gui.filter.dialog_select import FilterSelectDialog
from gui.marker.dialog_shape_select import ShapeSelectDialog


class MarkerEditDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createForm()
        self.__createLayots()
        self.__connect()

        self.__currentName = None
        self.__currentFilter = None
        self.__currentGShape = None

    # }}}

    def newMarker(self) -> Marker | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__onFilterBtn()")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        if self.__currentName is None:
            return None
        if self.__currentFilter is None:
            return None
        if self.__currentGShape is None:
            return None

        m = Marker(
            self.__currentName,
            self.__currentFilter,
            self.__currentGShape,
        )
        return m

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
        self.__name_lineedit = LineEdit("Enter name...")
        self.__filter_btn = PushButton(text="Click for select...")
        self.__shape_btn = PushButton(text="Click for select...")

    # }}}
    def __createForm(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createForm()")

        form = QtWidgets.QFormLayout()
        form.addRow("Name", self.__name_lineedit)
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

        self.__name_lineedit.textChanged.connect(self.__onNameEdit)
        self.__filter_btn.clicked.connect(self.__onFilterBtn)
        self.__shape_btn.clicked.connect(self.__onShapeBtn)

    # }}}

    @QtCore.pyqtSlot()  # __onNameEdit  # {{{
    def __onNameEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onNameEdit()")

        name = self.__name_lineedit.text()
        if name:
            self.__currentName = name

    # }}}
    @QtCore.pyqtSlot()  # __onFilterBtn  # {{{
    def __onFilterBtn(self):
        logger.debug(f"{self.__class__.__name__}.__onFilterBtn()")

        dial = FilterSelectDialog()
        f = dial.selectFilter()
        if f is None:
            return
        else:
            self.__filter_btn.setText(f.name)
            self.__currentFilter = f

    # }}}
    @QtCore.pyqtSlot()  # __onShapeBtn  # {{{
    def __onShapeBtn(self):
        logger.debug(f"{self.__class__.__name__}.__onShapeBtn()")

        dial = ShapeSelectDialog()
        gshape = dial.selectGShape()
        if gshape is None:
            return
        else:
            icon = QtGui.QIcon(gshape.pixmap())
            self.__shape_btn.setText("")
            self.__shape_btn.setIcon(icon)
            self.__currentGShape = gshape

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

        title = Label("| Add marker:", parent=self)
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
