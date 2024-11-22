#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from gui.custom.css import Css


class DockWidget(QtWidgets.QDockWidget):
    def __init__(  # {{{
        self,
        title: str,
        widget: QtWidgets.QWidget,
        parent=None,
    ):
        QtWidgets.QDockWidget.__init__(self, title, parent)

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


if __name__ == "__main__":
    ...
