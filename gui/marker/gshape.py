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
from PyQt6.QtCore import Qt

from avin.config import Cfg
from avin.utils import logger
from gui.custom import (
    Color,
)


class GShape(QtWidgets.QGraphicsPixmapItem):  # {{{
    class Type(enum.Enum):  # {{{
        CIRCLE = 1
        SQARE = 2
        TRIANGLE_UP = 3
        TRIANGLE_DOWN = 4

        @classmethod  # fromStr  #{{{
        def fromStr(cls, string_type: str):
            types = {
                "CIRCLE": GShape.Type.CIRCLE,
                "SQARE": GShape.Type.SQARE,
                "TRIANGLE_UP": GShape.Type.TRIANGLE_UP,
                "TRIANGLE_DOWN": GShape.Type.TRIANGLE_DOWN,
            }
            return types[string_type]

        # }}}

    # }}}
    class Size(enum.Enum):  # {{{
        VERY_SMALL = Cfg.ShapeSize.VERY_SMALL
        SMALL = Cfg.ShapeSize.SMALL
        NORMAL = Cfg.ShapeSize.NORMAL
        BIG = Cfg.ShapeSize.BIG
        VERY_BIG = Cfg.ShapeSize.VERY_BIG

        @classmethod  # fromStr  #{{{
        def fromStr(cls, string_type: str):
            types = {
                "VERY_SMALL": GShape.Size.VERY_SMALL,
                "SMALL": GShape.Size.SMALL,
                "NORMAL": GShape.Size.NORMAL,
                "BIG": GShape.Size.BIG,
                "VERY_BIG": GShape.Size.VERY_BIG,
            }
            return types[string_type]

        # }}}

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

        @classmethod  # fromStr  #{{{
        def fromStr(cls, string_type: str):
            types = {
                "WHITE": GShape.Color.WHITE,
                "RED": GShape.Color.RED,
                "ORANGE": GShape.Color.ORANGE,
                "YELLOW": GShape.Color.YELLOW,
                "GREEN": GShape.Color.GREEN,
                "CYAN": GShape.Color.CYAN,
                "BLUE": GShape.Color.BLUE,
                "VIOLET": GShape.Color.VIOLET,
                "PINK": GShape.Color.PINK,
            }
            return types[string_type]

        # }}}

    # }}}

    def __init__(  # {{{
        self, t: GShape.Type, s: GShape.Size, c: GShape.Color, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsPixmapItem.__init__(self, parent)

        self.type = t
        self.size = s
        self.color = c

        self.__drawGShape()

    # }}}
    def __drawGShape(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawGShape()")

        match self.type:
            case GShape.Type.CIRCLE:
                self.__drawGShapeCircle()
            case GShape.Type.SQARE:
                self.__drawGShapeSqare()
            case GShape.Type.TRIANGLE_UP:
                self.__drawGShapeTriangleUp()
            case GShape.Type.TRIANGLE_DOWN:
                self.__drawGShapeTriangleDown()

    # }}}
    def __drawGShapeCircle(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawGShapeCircle()")

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
        painter.drawEllipse(x, y, width, height)
        painter.end()

        self.setPixmap(pixmap)

    # }}}
    def __drawGShapeSqare(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawGShapeSqare()")

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
        painter.drawRect(QtCore.QRect(x, y, width, height))
        painter.end()

        self.setPixmap(pixmap)

    # }}}
    def __drawGShapeTriangleUp(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawGShapeTriangleUp()")

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
    def __drawGShapeTriangleDown(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawGShapeTriangleDown()")

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


if __name__ == "__main__":
    ...
