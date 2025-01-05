#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin.core import FilterList
from avin.utils import logger
from gui.custom import Css
from gui.filter.tree import FilterTree


class FilterDockWidget(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QDockWidget.__init__(self, "Filter", parent)

        self.widget = FilterWidget(self)
        self.setWidget(self.widget)
        self.setStyleSheet(Css.DOCK_WIDGET)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        feat = QtWidgets.QDockWidget.DockWidgetFeature
        self.setFeatures(
            feat.DockWidgetMovable
            | feat.DockWidgetClosable
            | feat.DockWidgetFloatable
        )

        # }}}


# }}}
class FilterWidget(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserFilters()

    # }}}
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.STYLE)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.filter_tree = FilterTree(self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.filter_tree)
        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

    # }}}
    def __loadUserFilters(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserMarker()")

        all_names = FilterList.requestAll()
        for name in all_names:
            filter_list = FilterList.load(name)
            self.filter_tree.addFilterList(filter_list)

    # }}}


# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = FilterWidget()
    w.show()
    sys.exit(app.exec())
