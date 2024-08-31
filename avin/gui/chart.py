#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import enum
import logging
from datetime import datetime, date, time
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from avin.const import UTC, MSK_TIME_DIF, ONE_DAY, DAYS_NAME
from avin.core import (
    Asset, TimeFrame, Bar, Chart, Trade, TradeList, ExtremumList
    )

from avin.utils import now, findLeft
from avin.gui.custom import (
    Color, Font, Icon, Palette, ToolButton, SmallButton, Dialog
    )

logger = logging.getLogger("LOGGER")

# Upd 2024.01.01 Begin -------------------------------------------------------

class Shape(QtWidgets.QGraphicsItemGroup):
    class Type(enum.Enum):
        DEFAULT =       0
        VERY_SMALL =    1
        SMALL =         2
        NORMAL =        3
        BIG =           4
        VERY_BIG =      5

    class Size(enum.Enum):
        DEFAULT =       0
        VERY_SMALL =    1
        SMALL =         2
        NORMAL =        3
        BIG =           4
        VERY_BIG =      5

    def __init__(self, TYPE, size, color, parent=None):
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        # TODO нужна глобальная палитра
        # из нее уже черпать цвета в другие классы
        self.type = TYPE
        self.size = size
        self.color = color

class Mark():
    def __init__(self, name, condition, shape, parent=None):
        self.name = name
        self.condition = condition
        self.shape = shape

# Upd 2024.01.01 End ---------------------------------------------------------

class Tree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Name =       0

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(Tree.Column.Name, Qt.SortOrder.AscendingOrder)
        self.setColumnWidth(Tree.Column.Name, 250)
        self.setFont(Font.MONO)


class IndicatorDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserIndicators()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tree = Tree(self)
        self.search_line = QtWidgets.QLineEdit(self)
        self.btn_search = ToolButton(Icon.SEARCH, self)
        self.btn_apply = ToolButton(Icon.APPLY, self)
        self.btn_cancel = ToolButton(Icon.CANCEL, self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.btn_search)
        hbox.addWidget(self.search_line)
        hbox.addStretch()
        hbox.addWidget(self.btn_apply)
        hbox.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.tree)
        self.setLayout(vbox)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_apply.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def __loadUserIndicators(self):
        logger.debug(f"{self.__class__.__name__}.__loadUserIndicators()")
        i = ExtremumHandler()
        self.__add(i)

    def __getSelected(self):
        logger.debug(f"{self.__class__.__name__}.__getSelected()")
        selected = list()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(Tree.Column.Name) == Qt.CheckState.Checked:
                selected.append(item.handler)
        return selected

    def __add(self, indicator):
        logger.debug(f"{self.__class__.__name__}.__add()")
        item = indicator.item
        self.tree.addTopLevelItem(item)

    def chooseIndicator(self):
        logger.debug(f"{self.__class__.__name__}.__loadUserIndicators()")
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            selected = self.__getSelected()
            return selected
        else:
            return False



class GBar(Bar, QtWidgets.QGraphicsItemGroup):
    """ Const """
    # DRAW_BODY =         False
    DRAW_BODY =         True
    WIDTH =             16
    # INDENT =            1
    INDENT =            4
    SHADOW_WIDTH =      1

    def __init__(self, dt, o, h, l, c, v, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        Bar.__init__(self, dt, o, h, l, c, v, parent)
        self.n = None

    def __calcCoordinates(self):
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")
        gchart = self.parent()
        self.x = gchart.xFromNumber(self.n)
        self.x0 = self.x + self.INDENT
        self.x1 = self.x + self.WIDTH - self.INDENT
        self.x_center = int((self.x0 + self.x1) / 2)
        self.y_opn = gchart.yFromPrice(self.open)
        self.y_cls = gchart.yFromPrice(self.close)
        self.y_hgh = gchart.yFromPrice(self.high)
        self.y_low = gchart.yFromPrice(self.low)
        self.open_pos = QtCore.QPointF(self.x_center, self.y_opn)
        self.close_pos = QtCore.QPointF(self.x_center, self.y_cls)
        self.high_pos = QtCore.QPointF(self.x_center, self.y_hgh)
        self.low_pos = QtCore.QPointF(self.x_center, self.y_low)

    def __setColor(self):
        logger.debug(f"{self.__class__.__name__}.__setColor()")
        if self.isBull():
            self.color = Color.BULL
        elif self.isBear():
            self.color = Color.BEAR
        else:
            self.color = Color.UNDEFINE

    def __createOpenLine(self):
        logger.debug(f"{self.__class__.__name__}.__createOpenLine()")
        opn = QtWidgets.QGraphicsLineItem(
            self.x0,        self.y_opn,
            self.x_center,  self.y_opn
            )
        pen = QtGui.QPen()
        pen.setColor(self.color)
        pen.setWidth(GBar.SHADOW_WIDTH)
        opn.setPen(pen)
        self.addToGroup(opn)

    def __createCloseLine(self):
        logger.debug(f"{self.__class__.__name__}.__createCloseLine()")
        cls = QtWidgets.QGraphicsLineItem(
            self.x_center,  self.y_cls,
            self.x1,        self.y_cls
            )
        pen = QtGui.QPen()
        pen.setColor(self.color)
        pen.setWidth(GBar.SHADOW_WIDTH)
        cls.setPen(pen)
        self.addToGroup(cls)

    def __createShadowLine(self):
        logger.debug(f"{self.__class__.__name__}.__createShadowLine()")
        shadow = QtWidgets.QGraphicsLineItem(
            self.x_center,
            self.y_low,
            self.x_center,
            self.y_hgh
            )
        pen = QtGui.QPen()
        pen.setColor(self.color)
        pen.setWidth(GBar.SHADOW_WIDTH)
        shadow.setPen(pen)
        self.addToGroup(shadow)

    def __createBody(self):
        logger.debug(f"{self.__class__.__name__}.__createBody()")
        width = self.x1 - self.x0
        height = abs(self.y_opn - self.y_cls)
        y0 = self.y_cls if self.isBull() else self.y_opn
        x0 = self.x_center - width / 2
        body = QtWidgets.QGraphicsRectItem(x0, y0, width, height)
        body.setPen(self.color)
        body.setBrush(self.color)
        self.addToGroup(body)

    @staticmethod  #fromCSV
    def fromCSV(bar_str, parent):
        code = f"GBar({bar_str}, parent)"
        bar = eval(code)
        return bar

    def createGraphicsItem(self):
        logger.debug(f"{self.__class__.__name__}.createGraphicsItem()")
        self.__calcCoordinates()
        self.__setColor()
        self.__createShadowLine()
        if self.DRAW_BODY:
            self.__createBody()
        else:
            self.__createOpenLine()
            self.__createCloseLine()


class GChart(Chart, QtWidgets.QGraphicsItemGroup):
    def __init__(
            self,
            asset: Asset,
            timeframe: TimeFrame,
            begin: datetime,
            end: datetime,
            constructor=GBar.fromCSV,
            ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self)
        Chart.__init__(self, asset, timeframe, begin, end, constructor)
        # self.__createIndicatorGroup()
        self.__numerateBars()
        self.__createSceneRect()
        self.__createGBars()

    def __numerateBars(self):
        logger.debug(f"{self.__class__.__name__}.__numerateBars()")
        for n, bar in enumerate(self._bars, 0):
            bar.n = n

    def __createSceneRect(self):
        logger.debug(f"{self.__class__.__name__}.__createSceneRect()")
        self.SCALE_Y = 10
        self.step = self.asset.min_price_step
        x0 = 0
        y0 = 0
        x1 = len(self._bars) * GBar.WIDTH
        y1 = int(self.highestHigh() / self.step / self.SCALE_Y)
        self.x_indent = (x1 - x0) * 0.05
        self.y_indent = (y1 - y0) * 0.05
        height = y1 - y0 + self.y_indent
        width =  x1 - x0 + self.x_indent
        self.rect = QtCore.QRectF(0, 0, width, height)

    def __createGBars(self):
        logger.debug(f"{self.__class__.__name__}.__createGBars()")
        for bar in self._bars:
            # TODO чарт имеет список self._gbars
            # GBar содержит ссылку на бар и номер
            # GBar это график итем гроуп
            # созданные итемы помещаются в self._gbars
            # self.getGrapthics - возвращает группу всей графики
            # тогда даже наследовать график итем гроуп не надо.
            bar.createGraphicsItem()

    def barFromDatetime(self, dt):
        index = findLeft(self._bars, dt, key=lambda x: x.dt)
        assert index is not None
        gbar = self._bars[index]
        return gbar

    def xFromNumber(self, n):
        return int(n * GBar.WIDTH)

    def xFromDatetime(self, dt):
        gbar = self.barFromDatetime(dt)
        return gbar.x

    def yFromPrice(self, price):
        y = int(self.rect.height() - price / self.step / self.SCALE_Y + self.y_indent)
        return y

    def nFromX(self, x):
        n = int(x / GBar.WIDTH)
        return n

    def barAt(self, x):
        if x < 0:
            return None
        n = self.nFromX(x)
        if n < len(self._bars):
            return self._bars[n]
        else:
            return None


class GTrade(Trade, QtWidgets.QGraphicsItemGroup):
    """ Const """
    OPEN_WIDTH =    1
    STOP_WIDTH =    1
    TAKE_WIDTH =    1
    __open_pen = QtGui.QPen()
    __open_pen.setWidth(OPEN_WIDTH)
    __open_pen.setColor(Color.OPEN)
    __stop_pen = QtGui.QPen()
    __stop_pen.setWidth(STOP_WIDTH)
    __stop_pen.setColor(Color.STOP)
    __take_pen = QtGui.QPen()
    __take_pen.setWidth(TAKE_WIDTH)
    __take_pen.setColor(Color.TAKE)

    def __init__(self, itrade, parent):
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        Trade.__init__(self, itrade._info, parent)
        itrade.gtrade = self  # link to GTrade in ITrade item
        self.itrade = itrade  #  link to ITrade in GTrade item
        self.__parent = parent
        self.__gchart = parent.gchart
        self.__calcCoordinates()
        self.__crateTradeShape()
        self.__createOpenItem()
        self.__createStopLossItem()
        self.__createTakeProfitItem()

    def __calcCoordinates(self):
        gchart = self.__gchart
        self.x_opn = (gchart.xFromDatetime(self.open_dt))
        self.x_cls = (gchart.xFromDatetime(self.close_dt))
        gbar = gchart.barFromDatetime(self.open_dt)
        y_hgh = gbar.high_pos.y()
        self.y0 = y_hgh - 50
        self.trade_pos = QtCore.QPointF(self.x_opn, self.y0)

    def __crateTradeShape(self):
        x0 = self.x_opn
        x1 = x0 + GBar.WIDTH
        x_center = (x0 + x1) / 2
        y0 = self.y0
        y1 = y0 - GBar.WIDTH
        if self.isLong():
            p1 = QtCore.QPointF(x0, y0)
            p2 = QtCore.QPointF(x1, y0)
            p3 = QtCore.QPointF(x_center, y1)
            triangle = QtGui.QPolygonF([p1, p2, p3])
        else:
            p1 = QtCore.QPointF(x0, y1)
            p2 = QtCore.QPointF(x1, y1)
            p3 = QtCore.QPointF(x_center, y0)
            triangle = QtGui.QPolygonF([p1, p2, p3])
        triangle = QtWidgets.QGraphicsPolygonItem(triangle)
        if self.isWin():
            triangle.setPen(Color.TRADE_WIN)
            triangle.setBrush(Color.TRADE_WIN)
        else:
            triangle.setPen(Color.TRADE_LOSS)
            triangle.setBrush(Color.TRADE_LOSS)
        self.addToGroup(triangle)

    def __createOpenItem(self):
        open_price = self.strategy["open_price"]
        self.y_opn = self.__gchart.yFromPrice(open_price)
        open_item = QtWidgets.QGraphicsLineItem(
            self.x_opn,                 self.y_opn,
            self.x_cls + GBar.WIDTH,    self.y_opn
            )
        open_item.setPen(self.__open_pen)
        self.addToGroup(open_item)

    def __createStopLossItem(self):
        stop_loss_price = self.strategy["stop_price"]
        self.y_stop = self.__gchart.yFromPrice(stop_loss_price)
        stop_loss = QtWidgets.QGraphicsLineItem(
            self.x_opn,                 self.y_stop,
            self.x_cls + GBar.WIDTH,    self.y_stop,
            )
        stop_loss.setPen(self.__stop_pen)
        self.addToGroup(stop_loss)

    def __createTakeProfitItem(self):
        take_profit_price = self.strategy["take_price"]
        self.y_take = self.__gchart.yFromPrice(take_profit_price)
        take_profit = QtWidgets.QGraphicsLineItem(
            self.x_opn,                 self.y_take,
            self.x_cls + GBar.WIDTH,    self.y_take,
            )
        take_profit.setPen(self.__take_pen)
        self.addToGroup(take_profit)

    def __createAnnotation(self):
        msk_dt = self.dt + MSK_TIME_DIF
        str_dt = msk_dt.strftime("%Y-%m-%d  %H:%M")
        text = (
            "<div style='background-color:#333333;'>"
            f"{str_dt}<br>"
            f"Result: {self.result}<br>"
            f"Days: {self.holding}<br>"
            f"Profitability: {self.percent_per_day}% "
            "</div>"
            )
        self.annotation = QtWidgets.QGraphicsTextItem()
        self.annotation.setHtml(text)
        self.annotation.setPos(self.x_opn, self.y0 - 200)
        self.annotation.hide()
        self.addToGroup(self.annotation)

    def parent(self):
        return self.__parent

    def showAnnotation(self):
        self.__createAnnotation()
        self.annotation.show()

    def hideAnnotation(self):
        self.annotation.hide()


class GTradeList(TradeList, QtWidgets.QGraphicsItemGroup):
    def __init__(self, itlist, parent=None):
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        TradeList.__init__(self, itlist.name, parent=itlist)
        self.__createGChart()
        self.__createGTrades()

    def __createGChart(self):
        if self.asset is None:
            self.gchart = None
            return
        self.gchart = GChart(
            self.asset,
            TimeFrame("D"),
            self.begin,
            self.end,
            )

    def __createGTrades(self):
        if self.gchart is None:
            return
        for t in self.parent():
            gtrade = GTrade(t, parent=self)
            self.add(gtrade)         # Trade.add
            self.addToGroup(gtrade)  # QGraphicsItemGroup.addToGroup

    @property  #begin
    def begin(self):
        return self.test.begin

    @property  #end
    def end(self):
        return self.test.end


class GMark(QtWidgets.QGraphicsItemGroup):
    ...


class BarInfo(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configPalette()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.label_barinfo = QtWidgets.QLabel("BAR INFO")
        self.label_barinfo.setFont(Font.MONO)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.label_barinfo)

    def __configPalette(self):
        logger.debug(f"{self.__class__.__name__}.__configPalette()")
        p = self.palette()
        p.setColor(QtGui.QPalette.ColorRole.Window, Color.RED)
        self.setPalette(p)

    def set(self, bar):
        logger.debug(f"{self.__class__.__name__}.set(bar)")
        msk_time = (bar.dt + MSK_TIME_DIF).strftime("%Y-%m-%d %H:%M")
        day = DAYS_NAME[bar.dt.weekday()]
        body = bar.body.percent()
        self.label_barinfo.setText(
            f"{msk_time} {day} - Open: {bar.open:<6} High: {bar.high:<6} "
            f"Low: {bar.low:<6} Close: {bar.close:<6} (Body: {body:.2f}%)"
            )


class VolumeInfo(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configPalette()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.label_volinfo = QtWidgets.QLabel("VOL INFO")
        self.label_volinfo.setFont(Font.MONO)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.label_volinfo)
        vbox.setContentsMargins(0, 0, 0, 0)

    def __configPalette(self):
        logger.debug(f"{self.__class__.__name__}.__configPalette()")
        p = self.palette()
        p.setColor(QtGui.QPalette.ColorRole.Window, Color.RED)
        self.setPalette(p)

    def set(self, bar):
        logger.debug(f"{self.__class__.__name__}.set(bar)")
        self.label_volinfo.setText(f"Vol: {bar.vol}")



class ExtremumHandler():
    def __init__(self):
        self.item = ExtremumItem(self)
        self.label = ExtremumLabel(self)
        self.settings = ExtremumSettings(self)
        self.indicator = ExtremumList
        self.graphics = ExtremumGraphics

    def createGItem(self, gchart):
        logger.debug(f"{self.__class__.__name__}.createGItem()")
        graphics_item_group = self.graphics(gchart)
        return graphics_item_group

    def showSettings(self):
        self.settings.exec()

    def getLabel(self):
        return self.label


class ExtremumItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, handler, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__handler = handler
        self.__config()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setCheckState(Tree.Column.Name, Qt.CheckState.Unchecked)
        self.setText(Tree.Column.Name, "Extremum")

    @property  #handler
    def handler(self):
        return self.__handler


class ExtremumGraphics(QtWidgets.QGraphicsItemGroup):
    """ Const """
    LONGTERM_LINE_WIDTH =  4
    MIDTERM_LINE_WIDTH =   2
    SHORTTERM_LINE_WIDTH = 1
    __LPEN = QtGui.QPen()
    __LPEN.setWidth(LONGTERM_LINE_WIDTH)
    __LPEN.setColor(Color.LONGTERM)
    __MPEN = QtGui.QPen()
    __MPEN.setWidth(MIDTERM_LINE_WIDTH)
    __MPEN.setColor(Color.MIDTERM)
    __SPEN = QtGui.QPen()
    __SPEN.setWidth(SHORTTERM_LINE_WIDTH)
    __SPEN.setColor(Color.SHORTTERM)

    """ Data index """
    EXTR_POS = 0
    SHAPE_POS = 1

    def __init__(self, gchart: GChart, parent=None):
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        self.gchart = gchart
        self.elist = ExtremumList(self.gchart)
        self.s_points = self.__createPoints(self.elist.sterm)
        self.m_points = self.__createPoints(self.elist.mterm)
        self.l_points = self.__createPoints(self.elist.lterm)
        self.s_lines = self.__createLines(self.s_points, self.__SPEN)
        self.m_lines = self.__createLines(self.m_points, self.__MPEN)
        self.l_lines = self.__createLines(self.l_points, self.__LPEN)
        self.addToGroup(self.s_points)
        self.addToGroup(self.m_points)
        self.addToGroup(self.l_points)
        self.addToGroup(self.s_lines)
        self.addToGroup(self.m_lines)
        self.addToGroup(self.l_lines)

    def __createPoints(self, extr_list):
        points = QtWidgets.QGraphicsItemGroup()
        for e in extr_list:
            shape = self.__createPointShape(e)
            points.addToGroup(shape)
        return points

    def __createPointShape(self, extr):
        """
        (x, y)   - epos - точка экстремума на графике
        (x0, y0) - spos - точка начала QGraphicsEllipseItem, графической
                   метки экстремума
        """
        shape = QtWidgets.QGraphicsItemGroup()
        x0 = self.gchart.xFromDatetime(extr.dt)
        y = self.gchart.yFromPrice(extr.price)
        x = x0 + GBar.WIDTH / 2
        y0 = y * 0.98 if extr.isMax() else y * 1.02
        epos = QtCore.QPointF(x, y)
        spos = QtCore.QPointF(x0, y0)
        width = height = GBar.WIDTH
        shape.setData(ExtremumGraphics.EXTR_POS, epos)
        shape.setData(ExtremumGraphics.SHAPE_POS, spos)
        if extr.isLongterm():
            circle = QtWidgets.QGraphicsEllipseItem(x0, y0, width, height)
            circle.setPen(Color.LONGTERM)
            circle.setBrush(Color.LONGTERM)
            shape.addToGroup(circle)
        elif extr.isMidterm():
            circle = QtWidgets.QGraphicsEllipseItem(x0, y0, width, height)
            circle.setPen(Color.MIDTERM)
            circle.setBrush(Color.MIDTERM)
            shape.addToGroup(circle)
        else:
            # для short-term-extremum метку не рисуем
            pass
        return shape

    def __createLines(self, points_group: QtWidgets.QGraphicsItemGroup, pen):
        lines = QtWidgets.QGraphicsItemGroup()
        points = points_group.childItems()
        if len(points) < 2:
            return
        i = 0
        while i < len(points) - 1:
            e1 = points[i].data(ExtremumGraphics.EXTR_POS)
            e2 = points[i + 1].data(ExtremumGraphics.EXTR_POS)
            l = QtWidgets.QGraphicsLineItem(e1.x(), e1.y(), e2.x(), e2.y())
            l.setPen(pen)
            lines.addToGroup(l)
            i += 1
        return lines


class ExtremumLabel(QtWidgets.QWidget):
    def __init__(self, handler, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__handler = handler
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.label_name = QtWidgets.QLabel("Extremum")
        self.btn_hide = SmallButton(Icon.HIDE)
        self.btn_settings = SmallButton(Icon.CONFIG)
        self.btn_delete = SmallButton(Icon.DELETE)
        self.btn_other = SmallButton(Icon.OTHER)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.label_name)
        hbox.addWidget(self.btn_hide)
        hbox.addWidget(self.btn_settings)
        hbox.addWidget(self.btn_delete)
        hbox.addWidget(self.btn_other)
        hbox.addStretch()
        hbox.setContentsMargins(0, 0, 0, 0)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_settings.clicked.connect(self.__onSettings)

    @QtCore.pyqtSlot()  #__onSettings
    def __onSettings(self):
        logger.debug(f"{self.__class__.__name__}.__onSettings()")
        self.handler.showSettings()

    def mousePressEventtt(self):
        logger.debug(f"{self.__class__.__name__}.mousePressEvent()")
        self.__onSettings()  # TODO: сделать нормальную кликабельную кнопку
        # даже если надо будет не виджеты делать а график итем груп
        # для каждого индикатора

    @property  #handler
    def handler(self):
        return self.__handler



class ExtremumSettings(QtWidgets.QDialog):
    def __init__(self, handler, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__handler = handler
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.__message_label = QtWidgets.QLabel()
        self.checkbox_inside = QtWidgets.QCheckBox("Inside days")
        self.checkbox_outside = QtWidgets.QCheckBox("Outside days")
        self.checkbox_sterm = QtWidgets.QCheckBox("Short-term extremum")
        self.checkbox_mterm = QtWidgets.QCheckBox("Mid-term extremum")
        self.checkbox_lterm = QtWidgets.QCheckBox("Long-term extremum")
        self.btn_apply = ToolButton(Icon.APPLY)
        self.btn_cancel = ToolButton(Icon.CANCEL)

    def __createLayots(self):
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.btn_apply)
        btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(btn_box)
        vbox.addWidget(self.checkbox_inside)
        vbox.addWidget(self.checkbox_outside)
        vbox.addWidget(self.checkbox_sterm)
        vbox.addWidget(self.checkbox_mterm)
        vbox.addWidget(self.checkbox_lterm)

    def __config(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_apply.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    # def confirm(self, message):
    #     self.__message_label.setText(message)
    #     result = self.exec()
    #     if result == QtWidgets.QDialog.DialogCode.Accepted:
    #         return True
    #     else:
    #         return False

    @property  #handler
    def handler(self):
        return self.__handler




class ChartLabels(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.__configPalette()

    def __configPalette(self):
        logger.debug(f"{self.__class__.__name__}.__configPalette()")
        p = self.palette()
        p.setColor(QtGui.QPalette.ColorRole.Window, Color.NONE)
        self.setPalette(p)

    def add(self, widget):
        logger.debug(f"{self.__class__.__name__}.add()")
        self.vbox.addWidget(widget)

    def remove(self, widget):
        logger.debug(f"{self.__class__.__name__}.remove()")
        self.vbox.removeWidget(widget)


class ChartScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsScene.__init__(self, parent)
        self.__config()
        self.__createWidgets()
        self.__createChartGroup()
        self.__createTListGroup()
        self.__createIndicatorGroup()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setBackgroundBrush(Color.BG)

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.labels = self.addWidget(ChartLabels())
        self.bar_info = BarInfo()
        self.vol_info = VolumeInfo()
        eh = ExtremumHandler()
        self.extr_label = eh.getLabel()
        self.labels.widget().add(self.bar_info)
        self.labels.widget().add(self.vol_info)
        self.labels.widget().add(self.extr_label)

    def __createChartGroup(self):
        logger.debug(f"{self.__class__.__name__}.__createChartGroup()")
        self.__has_chart = False
        self.gchart = None

    def __createTListGroup(self):
        logger.debug(f"{self.__class__.__name__}.__createTListGroup()")
        self.__has_gtlist = False
        self.gtlist = None

    def __createIndicatorGroup(self):
        logger.debug(f"{self.__class__.__name__}.__createIndicatorGroup()")
        self.indicators = QtWidgets.QGraphicsItemGroup()
        self.addItem(self.indicators)

    def mouseMoveEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):
        # print(e.pos())
        # print(e.scenePos())
        # print(e.screenPos())
        # print("l", e.lastPos())
        # print("l", e.lastScenePos())
        # print("l", e.lastScreenPos())
        # print("p", e.buttonDownPos(QtCore.Qt.MouseButton.LeftButton))
        # print("p", e.buttonDownScenePos(QtCore.Qt.MouseButton.LeftButton))
        # print("p", e.buttonDownScreenPos(QtCore.Qt.MouseButton.LeftButton))
        if not self.__has_chart:
            return e.ignore()
        bar = self.gchart.barAt(e.scenePos().x())
        if not bar:
            return e.ignore()
        self.bar_info.set(bar)
        self.vol_info.set(bar)
        return e.ignore()

    def mousePressEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):
        pos = e.scenePos()
        items = self.items(pos)
        for i in items:
            if isinstance(i, QtWidgets.QGraphicsProxyWidget):
                self.extr_label.mousePressEventtt()
        # return e.ignore()

    def mouseReleaseEvent(self, e):
        view = self.views()[0]
        p = view.mapToScene(0, 0)
        self.labels.setPos(p)
        return e.ignore()

    def mouseDoubleClickEvent(self, e):
        """
        загрузить новый график, именно за этот период (бар)
        стереть станый график.
        нарисовать главный график до выделенного бара
        нарисовать раскрытый бар
        продолжить рисовать главный график.
        """
        # if self.chart is None:
        #     return e.ignore()
        # n = self._nFromPos(e.scenePos())
        # bar_items = self.gchart.childItems()
        # zoom_bar = bar_items[n].bar
        # ID = self.chart.ID
        # begin = zoom_bar.dt
        # end = zoom_bar.dt + self.chart.timeframe
        # self.zoom_chart = Chart(ID, TimeFrame("5M"), begin, end)
        # ###
        # self.removeChart()
        # ###
        # scene_x0 = 0
        # n1 = self.chart.getBarsCount() - 1
        # n2 = self.zoom_chart.getBarsCount()
        # scene_x1 = (n1 + n2) * self.SCALE_X
        # scene_y0 = 0
        # scene_y1 = self.chart.highestHigh() * self.SCALE_Y
        # height = scene_y1 - scene_y0 #+ 2 * self.SCENE_INDENT
        # width = scene_x1 - scene_x0 #+ 2 * self.SCENE_INDENT
        # self.setSceneRect(0, 0, width, height)
        # ###
        # i = 0
        # for big_bar in self.chart:
        #     if big_bar.dt != zoom_bar.dt:
        #         bar_item = GraphicsBarItem(big_bar, i, self)
        #         self.gchart.addToGroup(bar_item)
        #         i += 1
        #     else:
        #         bar_item = GraphicsBarItem(big_bar, i, self)
        #         self.gchart.addToGroup(bar_item)
        #         i += 1
        #         for small_bar in self.zoom_chart:
        #             bar_item = GraphicsZoomBarItem(small_bar, i, self)
        #             self.gchart.addToGroup(bar_item)
        #             i += 1

    def setGChart(self, gchart: GChart):
        logger.debug(f"{self.__class__.__name__}.setGChart()")
        self.removeGChart()
        self.setSceneRect(gchart.rect)
        self.addItem(gchart)
        self.gchart = gchart
        self.__has_chart = True
        return True

    def setGTradeList(self, gtlist: GTradeList):
        logger.debug(f"{self.__class__.__name__}.setGTradeList()")
        self.removeGTradeList()
        self.gchart = gtlist.gchart
        self.gtlist = gtlist
        self.__has_chart = True
        self.__has_gtlist = True
        self.setSceneRect(self.gchart.rect)
        self.addItem(self.gchart)
        self.addItem(self.gtlist)

    def addIndicator(self, gi):
        logger.debug(f"{self.__class__.__name__}.addIndicator()")
        self.indicators.addToGroup(gi)

    def removeGChart(self):
        logger.debug(f"{self.__class__.__name__}.removeGChart()")
        if self.__has_chart:
            self.removeItem(self.gchart)
            self.__has_chart = False

    def removeGTradeList(self):
        logger.debug(f"{self.__class__.__name__}.removeGTradeList()")
        if self.__has_chart:
            self.removeItem(self.gchart)
            self.__has_chart = False
        if self.__has_gtlist:
            self.removeItem(self.gtlist)
            self.__has_gtlist = False

    def currentChart(self):
        logger.debug(f"{self.__class__.__name__}.currentChart()")
        return self.gchart


class ChartView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        QtWidgets.QGraphicsView.__init__(self, parent)
        # включает режим перетаскивания сцены внутри QGraphicsView
        # мышкой с зажатой левой кнопкой
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.current_gtrade = None

    def wheelEvent(self, e):
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

    def __resetTranformation(self):
        tr = self.transform()
        tr = tr.inverted()[0]
        pos = self.mapToScene(0, 0)
        info = self.scene().labels
        info.setTransform(tr)
        info.setPos(pos)
        if self.current_gtrade:
            self.current_gtrade.annotation.setTransform(tr)

    # def mouseMoveEvent(self, e: QtGui.QMouseEvent):
    #     ...
    #     super().mouseMoveEvent(e)
    #     return e.ignore()

    # def mousePressEvent(self, e: QtGui.QMouseEvent):
    #     ...
    #     super().mousePressEvent(e)
    #     return e.ignore()

    def centerOnFirst(self):
        logger.debug(
            f"ChartView.centerOnFirst()"
            )
        scene = self.scene()
        first_bar_item = scene.gchart.childItems()[0]
        pos = first_bar_item.close_pos
        self.centerOn(pos)

    def centerOnLast(self):
        scene = self.scene()
        last_bar_item = scene.gchart.childItems()[-1]
        pos = last_bar_item.close_pos
        self.centerOn(pos)

    def centerOnTrade(self, gtrade: GTrade):
        logger.debug(
            f"ChartView.centerOnTrade(trade)"
            f"trade.dt = {gtrade.dt}"
            )
        if self.current_gtrade is not None:
            self.current_gtrade.hideAnnotation()
        self.current_gtrade = gtrade
        gtrade.showAnnotation()
        pos = gtrade.trade_pos
        self.centerOn(pos)


class ChartWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.__createDialogs()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__initUI()

    def __createDialogs(self):
        self.indicator_dial = IndicatorDialog()

    def __createWidgets(self):
        self.view = ChartView(self)
        self.scene = ChartScene(self)
        self.view.setScene(self.scene)
        self.btn_asset = QtWidgets.QPushButton("ASSET")
        self.combobox_timeframe1 = QtWidgets.QComboBox()
        self.combobox_timeframe2 = QtWidgets.QComboBox()
        self.dateedit_begin = QtWidgets.QDateEdit()
        self.dateedit_end = QtWidgets.QDateEdit(now().date())
        self.btn_indicator = QtWidgets.QPushButton("Indicator")
        self.btn_mark = QtWidgets.QPushButton("Mark")

    def __createLayots(self):
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.btn_asset)
        hbox1.addWidget(self.combobox_timeframe1)
        hbox1.addWidget(self.combobox_timeframe2)
        hbox1.addWidget(self.dateedit_begin)
        hbox1.addWidget(QtWidgets.QLabel("-"))
        hbox1.addWidget(self.dateedit_end)
        hbox1.addWidget(self.btn_indicator)
        hbox1.addWidget(self.btn_mark)
        hbox1.addStretch()
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.view)
        self.setLayout(vbox)

    def __connect(self):
        self.combobox_timeframe1.currentTextChanged.connect(
            self.__onTimeframe1Changed)
        self.combobox_timeframe2.currentTextChanged.connect(
            self.__onTimeframe2Changed)
        self.dateedit_begin.dateChanged.connect(self.__onBeginDateChanged)
        self.dateedit_end.dateChanged.connect(self.__onEndDateChanged)
        self.btn_asset.clicked.connect(self.__onButtonAsset)
        self.btn_indicator.clicked.connect(self.__onButtonIndicator)
        self.btn_mark.clicked.connect(self.__onButtonMark)

    def __initUI(self):
        for timeframe in TimeFrame.ALL:
            self.combobox_timeframe1.addItem(str(timeframe))
            self.combobox_timeframe2.addItem(str(timeframe))
        self.combobox_timeframe1.setCurrentIndex(3)
        self.combobox_timeframe2.setCurrentIndex(2)
        self.dateedit_begin.setMinimumDate(QtCore.QDate(2018, 1, 1))
        self.dateedit_begin.setMaximumDate(now().date() - ONE_DAY)
        self.dateedit_end.setMinimumDate(QtCore.QDate(2018, 1, 1))
        self.dateedit_end.setMaximumDate(now().date())

    def __readBeginDate(self):
        date = self.dateedit_begin.date()
        year, month, day = date.year(), date.month(), date.day()
        return datetime(year, month, day, tzinfo=UTC)

    def __readEndDate(self):
        date = self.dateedit_end.date()
        year, month, day = date.year(), date.month(), date.day()
        return datetime(year, month, day, tzinfo=UTC)

    def __readTimeframe1(self):
        text = self.combobox_timeframe1.currentText()
        return TimeFrame(text)

    def __readTimeframe2(self):
        text = self.combobox_timeframe2.currentText()
        return TimeFrame(text)

    def __setBegin(self, dt):
        self.dateedit_begin.setDate(dt.date())

    def __setEnd(self, dt):
        self.dateedit_end.setDate(dt.date())

    def __setTimeframe1(self, timeframe):
        assert isinstance(timeframe, TimeFrame)
        self.combobox_timeframe1.setCurrentText(str(timeframe))

    def __setTimeframe2(self, timeframe):
        assert isinstance(timeframe, TimeFrame)
        self.combobox_timeframe2.setCurrentText(str(timeframe))

    @QtCore.pyqtSlot()  #__onButtonAsset
    def __onButtonAsset(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonAsset()")
        ...

    @QtCore.pyqtSlot()  #__onButtonIndicator
    def __onButtonIndicator(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonIndicator()")
        indicators = self.indicator_dial.chooseIndicator()
        current_chart = self.scene.currentChart()
        if indicators and current_chart:
            for i in indicators:
                gindicator = i.createGItem(current_chart)
                self.scene.addIndicator(gindicator)

    @QtCore.pyqtSlot()  #__onButtonMark
    def __onButtonMark(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonMark()")
        ...

    @QtCore.pyqtSlot()  #__onTimeframe1Changed
    def __onTimeframe1Changed(self):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe1Changed()")
        text = self.combobox_timeframe1.currentText()
        self.__timeframe1 = TimeFrame(text)

    @QtCore.pyqtSlot()  #__onTimeframe2Changed
    def __onTimeframe2Changed(self):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe2Changed()")
        text = self.combobox_timeframe2.currentText()
        self.__timeframe2 = TimeFrame(text)

    @QtCore.pyqtSlot()  #__onBeginDateChanged
    def __onBeginDateChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onBeginDateChanged()")
        ...

    @QtCore.pyqtSlot()  #__onEndDateChanged
    def __onEndDateChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onEndDateChanged()")
        ...

    def showChart(self, iasset: Asset):
        logger.debug(f"{self.__class__.__name__}.showChart()")
        timeframe = self.__readTimeframe1()
        end = now()
        begin = now() - timeframe * Chart.DEFAULT_BARS_COUNT
        gchart = GChart(iasset, timeframe, begin, end)
        self.scene.setGChart(gchart)
        # self.view.scale(1.00, 0.5)
        self.view.centerOnLast()
        self.btn_asset.setText(iasset.ticker)

    def showTradeList(self, itlist):
        logger.debug(f"{self.__class__.__name__}.showTradeList()")
        if itlist.asset is None:
            self.scene.removeGTradeList()
            return
        gtlist = GTradeList(itlist)
        self.__setTimeframe1(TimeFrame("D"))
        self.__setTimeframe2(TimeFrame("5M"))
        self.__setBegin(gtlist.begin)
        self.__setEnd(gtlist.end)
        self.scene.setGTradeList(gtlist)
        self.view.centerOnFirst()

    def showTrade(self, itrade):
        gtrade = itrade.gtrade
        if gtrade:
            self.view.centerOnTrade(gtrade)

    def clearAll(self):
        logger.debug(
            f"ChartWidget.clearAll()"
            )
        self.scene.removeChart()
        self.scene.removeTradeList()
        self.scene.removeIndicator()
        self.scene.removeMark()
        self.view.resetTransform()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = ChartWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())

