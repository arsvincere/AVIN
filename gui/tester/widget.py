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

from avin.tester import Test
from avin.utils import logger
from gui.custom import Css
from gui.tester.tree import TestTree


class TesterDockWidget(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QDockWidget.__init__(self, "Tester", parent)

        self.widget = TesterWidget(self)
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
class TesterWidget(QtWidgets.QWidget):  # {{{
    testChanged = QtCore.pyqtSignal(Test)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

    # }}}
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.STYLE)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.test_tree = TestTree(self)

        vertical = QtCore.Qt.Orientation.Vertical
        self.vsplit = QtWidgets.QSplitter(vertical, self)
        self.vsplit.addWidget(self.test_tree)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.vsplit)
        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.test_tree.clicked.connect(self.__onTestTreeClicked)

    # }}}

    @QtCore.pyqtSlot()  # __onTestTreeClicked# {{{
    def __onTestTreeClicked(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onTestTreeClicked()")

        item = self.test_tree.currentItem()
        class_name = item.__class__.__name__
        match class_name:
            case "TestItem":
                test = item.test
                self.testChanged.emit(test)
            case "TestListItem":
                pass

    # }}}


# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TestWidget()
    w.show()
    sys.exit(app.exec())
