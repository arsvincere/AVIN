#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum

from PyQt6 import QtWidgets


class Shape(QtWidgets.QGraphicsItemGroup):  # {{{
    class Type(enum.Enum):  # {{{
        DEFAULT = 0
        VERY_SMALL = 1
        SMALL = 2
        NORMAL = 3
        BIG = 4
        VERY_BIG = 5

    # }}}
    class Size(enum.Enum):  # {{{
        DEFAULT = 0
        VERY_SMALL = 1
        SMALL = 2
        NORMAL = 3
        BIG = 4
        VERY_BIG = 5

    # }}}
    def __init__(self, TYPE, size, color, parent=None):  # {{{
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        # TODO нужна глобальная палитра
        # из нее уже черпать цвета в другие классы
        self.type = TYPE
        self.size = size
        self.color = color


# }}}


# }}}
class Mark:  # {{{
    def __init__(self, name, condition, shape, parent=None):  # {{{
        self.name = name
        self.condition = condition
        self.shape = shape


# }}}
# }}}


if __name__ == "__main__":
    ...
