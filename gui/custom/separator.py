#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtWidgets


class Spacer(QtWidgets.QLabel):  # {{{
    def __init__(self, width=0, height=0, parent=None):  # {{{
        QtWidgets.QLabel.__init__(self, parent)

        if width:
            self.setFixedWidth(width)

        if height:
            self.setFixedHeight(height)

        if not width and not height:
            self.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding,
            )

    # }}}


# }}}
class HLine(QtWidgets.QFrame):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

    # }}}


# }}}
class VLine(QtWidgets.QFrame):  # {{{
    def __init__(self, width=0, parent=None):  # {{{
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        if width:
            self.setFixedWidth(width)

    # }}}


# }}}


if __name__ == "__main__":
    ...
