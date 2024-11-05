#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# FILE:         main.py
# CREATED:      2023.07.23 15:06
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

import PyQt6

from avin import *
from gui.data.widget import DataWidget


def main():
    print("Welcome to AVIN Trade System!")

    # show splash
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    # pic = PyQt6.QtGui.QPixmap(SPLASH_PIC)
    # splash = PyQt6.QtWidgets.QSplashScreen(pic)
    # splash.show()

    w = DataWidget()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(PyQt6.QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    code = app.exec()

    # show main window
    # w = MainWindow()
    # w.show()
    # splash.finish(w)
    # code = app.exec()

    # before quit actions
    ...
    sys.exit(code)


if __name__ == "__main__":
    main()
