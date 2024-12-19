#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum
import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.core import Filter
from avin.utils import logger
from gui.chart.gchart import GBar
from gui.custom import Color, Css, Icon, Label, Spacer, ToolButton
from gui.filter.item import FilterItem


class Shape(QtWidgets.QGraphicsPixmapItem):  # {{{
    class Type(enum.Enum):  # {{{
        CIRCLE = 1
        SQARE = 2
        TRIANGLE_UP = 3
        TRIANGLE_DOWN = 4

    # }}}
    class Size(enum.Enum):  # {{{
        VERY_SMALL = GBar.WIDTH * 0.5
        SMALL = GBar.WIDTH * 0.75
        NORMAL = GBar.WIDTH
        BIG = GBar.WIDTH * 1.5
        VERY_BIG = GBar.WIDTH * 2

    # }}}
    class Color(enum.Enum):  # {{{
        # dragonWhite = "#c5c9c5"{{{
        # dragonGray = "#a6a69c"
        # dragonGray2 = "#9e9b93"
        # dragonGray3 = "#7a8382"
        # lotusWhite0 = "#d5cea3"
        # lotusWhite1 = "#dcd5ac"
        # lotusWhite2 = "#e5ddb0"
        # lotusWhite3 = "#f2ecbc"
        # lotusWhite4 = "#e7dba0"
        # lotusWhite5 = "#e4d794"
        # lotusGray3 = "#8a8980"
        # nord11 = "#BF616A"
        # lotusRed = "#c84053"
        # lotusRed2 = "#d7474b"
        # lotusRed3 = "#e82424"
        # nord12 = "#D08770"
        # lotusOrange = "#cc6d00"
        # lotusOrange2 = "#e98a00"
        # nord13 = "#EBCB8B"
        # lotusYellow = "#77713f"
        # lotusYellow2 = "#836f4a"
        # lotusYellow3 = "#de9800"
        # lotusYellow4 = "#f9d791"
        # nord14 = "#A3BE8C"
        # lotusGreen = "#6f894e"
        # lotusGreen2 = "#6e915f"
        # nord7 = "#8FBCBB"
        # lotusAqua = "#597b75"
        # lotusAqua2 = "#5e857a"
        # lotusTeal1 = "#4e8ca2"
        # lotusTeal2 = "#6693bf"
        # lotusTeal3 = "#5a7785"
        # nord10 = "#5E81AC"
        # lotusBlue1 = "#c7d7e0"
        # lotusBlue2 = "#b5cbd2"
        # lotusBlue3 = "#9fb5c9"
        # lotusBlue4 = "#4d699b"
        # lotusBlue5 = "#5d57a3"
        # oniViolet = "#957FB8"
        # lotusViolet1 = "#a09cac"
        # lotusViolet2 = "#766b90"
        # lotusViolet3 = "#c9cbd1"
        # lotusViolet4 = "#624c83"
        # sakuraPink = "#D27E99"
        # lotusPink = "#b35b79"}}}
        WHITE = QtGui.QColor(Color.dragonWhite)  # #c5c9c5
        RED = QtGui.QColor(Color.nord11)  # #BF616A
        ORANGE = QtGui.QColor(Color.nord12)  # #D08770
        YELLOW = QtGui.QColor(Color.nord13)  # #EBCB8B
        GREEN = QtGui.QColor(Color.nord14)  # #A3BE8C
        CYAN = QtGui.QColor(Color.nord7)  # #8FBCBB
        BLUE = QtGui.QColor(Color.nord10)  # #5E81AC
        VIOLET = QtGui.QColor(Color.oniViolet)  # #957FB8
        PINK = QtGui.QColor(Color.sakuraPink)  # D27E99

    # }}}

    def __init__(  # {{{
        self, t: Shape.Type, s: Shape.Size, c: Shape.Color, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsPixmapItem.__init__(self, parent)

        self.type = t
        self.size = s
        self.color = c

        self.__drawShape()

    # }}}
    def __drawShape(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawShape()")

        match self.type:
            case Shape.Type.CIRCLE:
                self.__drawShapeCircle()
            case Shape.Type.SQARE:
                self.__drawShapeSqare()
            case Shape.Type.TRIANGLE_UP:
                self.__drawShapeTriangleUp()
            case Shape.Type.TRIANGLE_DOWN:
                self.__drawShapeTriangleDown()

    # }}}
    def __drawShapeCircle(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawShapeCircle()")

        x = 0
        y = 0
        width = int(self.size.value)
        height = int(self.size.value)

        pixmap = QtGui.QPixmap(width + 2, height + 2)  # +2 иначе подрезает...
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QtGui.QPainter()
        painter.begin(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(self.color.value)
        painter.setBrush(self.color.value)
        painter.drawEllipse(0, 0, width, height)
        painter.end()

        self.setPixmap(pixmap)

    # }}}
    def __drawShapeSqare(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawShapeSqare()")

        x = 0
        y = 0
        width = self.size.value
        height = self.size.value

        pixmap = QtGui.QPixmap(width + 2, height + 2)  # +2 иначе подрезает...
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QtGui.QPainter()
        painter.begin(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(self.color.value)
        painter.setBrush(self.color.value)
        painter.drawRect(QtCore.QRect(0, 0, width, height))
        painter.end()

        self.setPixmap(pixmap)

    # }}}
    def __drawShapeTriangleUp(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawShapeTriangleUp()")

        width = self.size.value
        height = self.size.value
        x0 = 0
        x1 = x0 + self.size.value
        x_center = (x0 + x1) / 2
        y0 = 0
        y1 = y0 + self.size.value

        p1 = QtCore.QPointF(x_center, y0)
        p2 = QtCore.QPointF(x0, y1)
        p3 = QtCore.QPointF(x1, y1)

        pixmap = QtGui.QPixmap(width + 2, height + 2)  # +2 иначе подрезает...
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QtGui.QPainter()
        painter.begin(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(self.color.value)
        painter.setBrush(self.color.value)
        painter.drawPolygon(p1, p2, p3)
        painter.end()

        self.setPixmap(pixmap)

    # }}}
    def __drawShapeTriangleDown(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawShapeTriangleDown()")

        width = self.size.value
        height = self.size.value
        x0 = 0
        x1 = x0 + self.size.value
        x_center = (x0 + x1) / 2
        y0 = 0
        y1 = y0 + self.size.value

        p1 = QtCore.QPointF(x_center, y1)
        p2 = QtCore.QPointF(x0, y0)
        p3 = QtCore.QPointF(x1, y0)

        pixmap = QtGui.QPixmap(width + 2, height + 2)  # +2 иначе подрезает...
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QtGui.QPainter()
        painter.begin(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(self.color.value)
        painter.setBrush(self.color.value)
        painter.drawPolygon(p1, p2, p3)
        painter.end()

        self.setPixmap(pixmap)

    # }}}


# }}}
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
    def selectShape(self) -> Shape | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectFilters()")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return None

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

        for i in Shape.Type:
            self.__type_combobox.addItem(i.name, userData=i)

        for i in Shape.Size:
            self.__size_combobox.addItem(i.name, userData=i)
        self.__size_combobox.setCurrentIndex(2)  # Shape.Size.NORMAL

        for i in Shape.Color:
            self.__color_combobox.addItem(i.name, userData=i)

        size = QtCore.QSize(
            Shape.Size.VERY_BIG.value, Shape.Size.VERY_BIG.value
        )
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
    def __updatePreview(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__updatePreview()")

        typ = self.__type_combobox.currentData()
        size = self.__size_combobox.currentData()
        color = self.__color_combobox.currentData()

        shape = Shape(typ, size, color)
        pixmap = shape.pixmap()
        self.__priview_label.setPixmap(pixmap)

    # }}}


# }}}
class _Tree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()

    # }}}
    def __iter__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__iter__()")

        all_items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            all_items.append(item)

        return iter(all_items)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config header
        labels = list()
        for l in FilterItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(FilterItem.Column.Name, Qt.SortOrder.AscendingOrder)

        # config width
        self.setColumnWidth(FilterItem.Column.Name, 150)

        # config style
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)

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


class Marker:  # {{{
    def __init__(  # {{{
        self, name: str, filter: Filter, shape: Shape, parent=None
    ):
        self.name = name
        self.filter = filter
        self.shape = shape

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ShapeSelectDialog()
    w.show()
    sys.exit(app.exec())
