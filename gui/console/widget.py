#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import logging
import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin.utils import logger
from gui.custom import Css


class ConsoleDockWidget(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QDockWidget.__init__(self, "Console", parent)

        widget = ConsoleWidget(self)
        self.setWidget(widget)
        self.setStyleSheet(Css.DOCK_WIDGET)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
        )

        feat = QtWidgets.QDockWidget.DockWidgetFeature
        self.setFeatures(
            feat.DockWidgetMovable
            | feat.DockWidgetClosable
            | feat.DockWidgetFloatable
        )

        # }}}


# }}}
class ConsoleWidget(QtWidgets.QPlainTextEdit):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QTabWidget.__init__(self, parent)
        self.__config()
        self.__createHandler()
        self.__connect()
        logger.info("Welcome to AVIN Trade System v0.1!")

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setStyleSheet(Css.STYLE)
        self.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __createHandler(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createTester()")
        self.handler = Handler(self)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
        )
        self.handler.setFormatter(formatter)
        self.handler.setLevel(logging.INFO)
        logger.addHandler(self.handler)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.handler.message.connect(self.__updateText)

    # }}}
    def __scrollDown(self):  # {{{
        scroll_bar = self.verticalScrollBar()
        end_text = scroll_bar.maximum()
        scroll_bar.setValue(end_text)

    # }}}
    def __updateText(self, msg):  # {{{
        self.appendPlainText(msg)
        self.__scrollDown()

    # }}}


# }}}
class Handler(logging.StreamHandler, QtCore.QObject):  # {{{
    message = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):  # {{{
        logging.StreamHandler.__init__(self)
        QtCore.QObject.__init__(self, parent)

    # }}}
    def emit(self, record):  # {{{
        log_msg = self.format(record)
        self.message.emit(log_msg)
        self.flush()

        # log_message = self.format(record)
        # if "DEBUG" in log_message:
        #     text = f"""<span style='color:#ff00ff;'>{log_message}</span>"""
        # elif "INFO" in log_message:
        #     text = f"""<span style='color:#00ffff;'>{log_message}</span>"""
        # elif "WARNING" in log_message:
        #     text = f"""<span style='color:#ffff00;'>{log_message}</span>"""
        # elif "ERROR" in log_message or "CRITICAL" in log_message:
        #     text = f"""<span style='color:#ff0000;'>{log_message}</span>"""
        # self.widget.append(text)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ConsoleWidget()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
