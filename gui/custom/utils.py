#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore

from avin.utils import logger


def awaitQThread(thread: QtCore.QThread):  # {{{
    logger.debug("gui.utils.awaitQThread()")

    while not thread.isFinished():
        QtCore.QThread.msleep(50)


# }}}


if __name__ == "__main__":
    ...
