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

from avin.utils import configureLogger, logger
from gui import MainWindow, Splash

configureLogger(debug=True, info=True)


def main():
    try:
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
        sys.exit(code)
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
