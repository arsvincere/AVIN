#!/usr/bin/env  python3
# ============================================================================
# FILE:         main.py
# CREATED:      2023.07.23 15:06
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

import PyQt6

from gui import MainWindow, Splash


def main():
    print("Welcome to AVIN Trade System!")

    # start app
    app = PyQt6.QtWidgets.QApplication(sys.argv)

    # show splash
    splash = Splash()
    splash.show()

    # show main window
    w = MainWindow()
    w.show()
    splash.finish(w)
    code = app.exec()

    # before quit actions
    print("Goodbuy!")
    sys.exit(code)


if __name__ == "__main__":
    main()
