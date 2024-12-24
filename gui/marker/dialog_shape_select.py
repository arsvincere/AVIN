#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import sys

from PyQt6 import QtCore, QtWidgets

from avin.utils import logger
from gui.custom import (
    Css,
    Icon,
    Label,
    Spacer,
    ToolButton,
)
from gui.marker.gshape import GShape


class ShapeSelectDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createForm()
        self.__createLayots()
        self.__initUI()
        self.__connect()  # важноk после initUI делать конект!
        self.__updatePreview()

    # }}}

    def selectGShape(self) -> GShape | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectFilters()")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

        shape = self.__currentGShape()
        return shape

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__toolbar = _ShapeToolBar(self)
        self.__type_combobox = QtWidgets.QComboBox(self)
        self.__size_combobox = QtWidgets.QComboBox(self)
        self.__color_combobox = QtWidgets.QComboBox(self)
        self.__priview_label = QtWidgets.QLabel(self)

    # }}}
    def __createForm(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createForm()")

        form = QtWidgets.QFormLayout()
        form.addRow("Form", self.__type_combobox)
        form.addRow("Size", self.__size_combobox)
        form.addRow("Color", self.__color_combobox)
        form.addRow("Preview", self.__priview_label)
        self.__form = form

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__toolbar)
        vbox.addLayout(self.__form)

        self.setLayout(vbox)

    # }}}
    def __initUI(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        for i in GShape.Type:
            self.__type_combobox.addItem(i.name, userData=i)

        for i in GShape.Size:
            self.__size_combobox.addItem(i.name, userData=i)
        self.__size_combobox.setCurrentIndex(2)  # GShape.Size.NORMAL

        for i in GShape.Color:
            self.__color_combobox.addItem(i.name, userData=i)

        self.__priview_label.setFixedSize(32, 32)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__toolbar.btn_ok.clicked.connect(self.accept)
        self.__toolbar.btn_cancel.clicked.connect(self.reject)

        self.__type_combobox.currentTextChanged.connect(self.__updatePreview)
        self.__size_combobox.currentTextChanged.connect(self.__updatePreview)
        self.__color_combobox.currentTextChanged.connect(self.__updatePreview)

    # }}}
    def __currentGShape(self) -> GShape:  # {{{
        logger.debug(f"{self.__class__.__name__}.__currentGShape()")

        typ = self.__type_combobox.currentData()
        size = self.__size_combobox.currentData()
        color = self.__color_combobox.currentData()

        shape = GShape(typ, size, color)
        return shape

    # }}}
    def __updatePreview(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__updatePreview()")

        shape = self.__currentGShape()
        pixmap = shape.pixmap()
        self.__priview_label.setPixmap(pixmap)

    # }}}


# }}}
class _ShapeToolBar(QtWidgets.QToolBar):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__createWidgets()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        title = Label("| Select shape:", parent=self)
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
    w = ShapeSelectDialog()
    w.show()
    sys.exit(app.exec())
