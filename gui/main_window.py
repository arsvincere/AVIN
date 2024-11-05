#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""Doc"""

import sys

from PyQt6 import QtCore, QtWidgets


class DataWidget(QtWidgets.QLabel):  # {{{
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        self.setText("I'm data widget!")


# }}}
class AssetWidget(QtWidgets.QLabel):  # {{{
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        self.setText("asset!")


# }}}
class StrategyWidget(QtWidgets.QLabel):  # {{{
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        self.setText("strategy!")


# }}}
class TestWidget(QtWidgets.QLabel):  # {{{
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        self.setText("test!")


# }}}


class DataDockWideg(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):
        QtWidgets.QDockWidget.__init__(self, parent)
        data_widget = DataWidget(self)
        self.setWidget(data_widget)

        f = QtWidgets.QDockWidget.DockWidgetFeature
        self.setFeatures(
            f.DockWidgetMovable | f.DockWidgetClosable | f.DockWidgetFloatable
        )

        self.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
            | QtCore.Qt.DockWidgetArea.TopDockWidgetArea
            | QtCore.Qt.DockWidgetArea.BottomDockWidgetArea
        )


# }}}
class AssetDockWideg(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):
        QtWidgets.QDockWidget.__init__(self, parent)
        asset_widget = AssetWidget(self)
        self.setWidget(asset_widget)

        f = QtWidgets.QDockWidget.DockWidgetFeature
        self.setFeatures(
            f.DockWidgetMovable | f.DockWidgetClosable | f.DockWidgetFloatable
        )

        self.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
            | QtCore.Qt.DockWidgetArea.TopDockWidgetArea
            | QtCore.Qt.DockWidgetArea.BottomDockWidgetArea
        )


# }}}
class StrategyDockWideg(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):
        QtWidgets.QDockWidget.__init__(self, parent)
        strategy_widget = StrategyWidget(self)
        self.setWidget(strategy_widget)

        f = QtWidgets.QDockWidget.DockWidgetFeature
        self.setFeatures(
            f.DockWidgetMovable | f.DockWidgetClosable | f.DockWidgetFloatable
        )

        self.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
            | QtCore.Qt.DockWidgetArea.TopDockWidgetArea
            | QtCore.Qt.DockWidgetArea.BottomDockWidgetArea
        )


# }}}
class TestDockWideg(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):
        QtWidgets.QDockWidget.__init__(self, parent)
        widget = TestWidget(self)
        self.setWidget(widget)

        f = QtWidgets.QDockWidget.DockWidgetFeature
        self.setFeatures(
            f.DockWidgetMovable | f.DockWidgetClosable | f.DockWidgetFloatable
        )

        self.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
            | QtCore.Qt.DockWidgetArea.TopDockWidgetArea
            | QtCore.Qt.DockWidgetArea.BottomDockWidgetArea
        )


# }}}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.data_widget = DataDockWideg()
        self.asset_widget = AssetDockWideg()
        self.strategy_widget = StrategyDockWideg()
        self.test_widget = TestDockWideg()

        left = QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
        right = QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        top = QtCore.Qt.DockWidgetArea.TopDockWidgetArea
        bottom = QtCore.Qt.DockWidgetArea.BottomDockWidgetArea

        self.setCentralWidget(self.data_widget)

        self.addDockWidget(left, self.asset_widget)
        self.addDockWidget(right, self.strategy_widget)
        self.addDockWidget(right, self.test_widget)

        hor = QtCore.Qt.Orientation.Horizontal
        ver = QtCore.Qt.Orientation.Vertical
        # self.splitDockWidget(self.data_widget, self.asset_widget, hor)
        # self.splitDockWidget(self.data_widget, self.strategy_widget, hor)
        # self.splitDockWidget(self.data_widget, self.test_widget, ver)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())
