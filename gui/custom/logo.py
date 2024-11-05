#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from PyQt6 import QtGui, QtWidgets


class Logo(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        logo = QtGui.QPixmap()
        logo.load("/home/alex/yandex/src/moex.data/res/logo.png")
        logo = logo.scaledToWidth(32)
        self.setPixmap(logo)


if __name__ == "__main__":
    ...
