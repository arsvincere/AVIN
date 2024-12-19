#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.utils import logger
from gui.chart.gchart import GBar
from gui.custom import Color


class Shape(QtWidgets.QGraphicsItemGroup):  # {{{
    class Type(enum.Enum):  # {{{
        DEFAULT = 0
        CIRCLE = 1
        SQARE = 2
        TRIANGLE_UP = 3
        TRIANGLE_DOWN = 4

    # }}}
    class Size(enum.Enum):  # {{{
        DEFAULT = GBar.WIDTH
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
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

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
        width = self.size.value
        height = self.size.value

        circle = QtWidgets.QGraphicsEllipseItem(x, y, width, height)
        circle.setPen(self.color.value)
        circle.setBrush(self.color.value)

        self.addToGroup(circle)

    # }}}
    def __drawShapeSqare(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawShapeSqare()")

        x = 0
        y = 0
        width = self.size.value
        height = self.size.value

        sqare = QtWidgets.QGraphicsRectItem(x, y, width, height)
        sqare.setPen(self.color.value)
        sqare.setBrush(self.color.value)

        self.addToGroup(sqare)

    # }}}
    def __drawShapeTriangleUp(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawShapeTriangleUp()")

        x0 = 0
        x1 = x0 + self.size.value
        x_center = (x0 + x1) / 2
        y0 = 0
        y1 = y0 + self.size.value

        p1 = QtCore.QPointF(x_center, y0)
        p2 = QtCore.QPointF(x0, y1)
        p3 = QtCore.QPointF(x1, y1)
        triangle = QtGui.QPolygonF([p1, p2, p3])

        graphic_triangle = QtWidgets.QGraphicsPolygonItem(triangle)
        graphic_triangle.setPen(self.color.value)
        graphic_triangle.setBrush(self.color.value)

        self.addToGroup(graphic_triangle)

    # }}}
    def __drawShapeTriangleDown(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawShapeTriangleDown()")

        x0 = 0
        x1 = x0 + self.size.value
        x_center = (x0 + x1) / 2
        y0 = 0
        y1 = y0 + self.size.value

        p1 = QtCore.QPointF(x_center, y1)
        p2 = QtCore.QPointF(x0, y0)
        p3 = QtCore.QPointF(x1, y0)
        triangle = QtGui.QPolygonF([p1, p2, p3])

        graphic_triangle = QtWidgets.QGraphicsPolygonItem(triangle)
        graphic_triangle.setPen(self.color.value)
        graphic_triangle.setBrush(self.color.value)

        self.addToGroup(graphic_triangle)

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
    ...
