#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore, QtWidgets

from gui.chart.gtrade import GTrade


class ChartView(QtWidgets.QGraphicsView):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QGraphicsView.__init__(self, parent)
        # включает режим перетаскивания сцены внутри QGraphicsView
        # мышкой с зажатой левой кнопкой
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.current_gtrade = None

    # }}}
    def wheelEvent(self, e):  # {{{
        ctrl = QtCore.Qt.KeyboardModifier.ControlModifier
        no = QtCore.Qt.KeyboardModifier.NoModifier
        if e.modifiers() == no:
            if e.angleDelta().y() < 0:
                self.scale(0.9, 1)
            else:
                self.scale(1.1, 1)
        if e.modifiers() == ctrl:
            if e.angleDelta().y() < 0:
                self.scale(1, 0.9)
            else:
                self.scale(1, 1.1)
        self.__resetTranformation()

    # }}}
    def __resetTranformation(self):  # {{{
        tr = self.transform()
        tr = tr.inverted()[0]
        pos = self.mapToScene(0, 0)
        info = self.scene().labels
        info.setTransform(tr)
        info.setPos(pos)
        if self.current_gtrade:
            self.current_gtrade.annotation.setTransform(tr)

    # }}}
    # def mouseMoveEvent(self, e: QtGui.QMouseEvent):{{{
    #     ...
    #     super().mouseMoveEvent(e)
    #     return e.ignore()
    # }}}
    # def mousePressEvent(self, e: QtGui.QMouseEvent):{{{
    #     ...
    #     super().mousePressEvent(e)
    #     return e.ignore()
    # }}}
    def centerOnFirst(self):  # {{{
        logger.debug("ChartView.centerOnFirst()")
        scene = self.scene()
        first_bar_item = scene.gchart.childItems()[0]
        pos = first_bar_item.close_pos
        self.centerOn(pos)

    # }}}
    def centerOnLast(self):  # {{{
        scene = self.scene()
        last_bar_item = scene.gchart.childItems()[-1]
        pos = last_bar_item.close_pos
        self.centerOn(pos)

    # }}}
    def centerOnTrade(self, gtrade: GTrade):  # {{{
        logger.debug(
            f"ChartView.centerOnTrade(trade)" f"trade.dt = {gtrade.dt}"
        )
        if self.current_gtrade is not None:
            self.current_gtrade.hideAnnotation()
        self.current_gtrade = gtrade
        gtrade.showAnnotation()
        pos = gtrade.trade_pos
        self.centerOn(pos)


# }}}


# }}}


if __name__ == "__main__":
    ...
