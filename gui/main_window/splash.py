#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# FILE:         main.py
# CREATED:      2023.07.23 15:06
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from PyQt6 import QtGui, QtWidgets

from avin.const import Res


class Splash(QtWidgets.QSplashScreen):
    def __init__(self, parent=None):
        pic = QtGui.QPixmap(Res.SPLASH_PIC)
        QtWidgets.QSplashScreen.__init__(self, pic)
        self.setWindowTitle("AVIN")
