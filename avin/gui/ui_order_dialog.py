#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import os
import enum
import logging
import time as timer
from datetime import datetime, date, time
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from avin.core import Order, Asset
from avin.gui.custom import Palette, Font
logger = logging.getLogger("LOGGER")


class UAssetInfo(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.current_asset = None
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.current_asset = None

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        L = QtWidgets.QLabel
        self.asset = L("ASSET", self)
        self.margin = L("x5 x5", self)
        self.price = L("0.00 rub", self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.asset)
        hbox.addWidget(self.margin)
        hbox.addWidget(self.price)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        sp = QtWidgets.QSizePolicy.Policy.Minimum
        self.setSizePolicy(sp, sp)

    def setAsset(self, asset: Asset):
        logger.debug(f"{self.__class__.__name__}.__setAsset({asset})")
        self.current_asset = asset
        self.asset.setText(asset.ticker)
        self.margin.setText("none-none")
        self.price.setText(str(asset.last_price))

    def updateWidget(self):
        logger.debug(f"{self.__class__.__name__}.updateWidget()")


class UOrderType(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__configButtons()
        self.__connect()
        self.current_type = None

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        p = self.palette()
        p.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#484848"))
        self.setPalette(p)

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.market = QtGui.QAction("Market", self)
        self.limit = QtGui.QAction("Limit", self)
        self.stop = QtGui.QAction("Stop", self)
        self.wait = QtGui.QAction("Wait", self)
        self.trailing = QtGui.QAction("Trailing", self)
        self.addAction(self.market)
        self.addAction(self.limit)
        self.addAction(self.stop)
        self.addAction(self.wait)
        self.addAction(self.trailing)

    def __configButtons(self):
        self.widgetForAction(self.market).setCheckable(True)
        self.widgetForAction(self.limit).setCheckable(True)
        self.widgetForAction(self.stop).setCheckable(True)
        self.widgetForAction(self.wait).setCheckable(True)
        self.widgetForAction(self.trailing).setCheckable(True)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.actionTriggered.connect(self.__onTriggered)
        self.market.triggered.connect(self.__onMarket)
        self.limit.triggered.connect(self.__onLimit)
        self.stop.triggered.connect(self.__onStop)
        self.wait.triggered.connect(self.__onWait)
        self.trailing.triggered.connect(self.__onTrailing)

    def __uncheckActions(self):
        for i in self.actions():
            btn = self.widgetForAction(i)
            btn.setChecked(False)

    @QtCore.pyqtSlot(QtGui.QAction)
    def __onTriggered(self, action: QtGui.QAction):
        self.__uncheckActions()
        btn = self.widgetForAction(action)
        state = btn.isChecked()
        btn.setChecked(not state)

    @QtCore.pyqtSlot()  #__onMarket
    def __onMarket(self):
        logger.debug(f"{self.__class__.__name__}.__onMarket()")
        self.current_type = Order.Type.MARKET
        self.parent().updateWidget()

    @QtCore.pyqtSlot()  #__onLimit
    def __onLimit(self):
        logger.debug(f"{self.__class__.__name__}.___onLimit()")
        self.current_type = Order.Type.LIMIT
        self.parent().updateWidget()

    @QtCore.pyqtSlot()  #__onStop
    def __onStop(self):
        logger.debug(f"{self.__class__.__name__}.___onLimit()")
        self.current_type = Order.Type.STOP
        self.parent().updateWidget()

    @QtCore.pyqtSlot()  #__onWait
    def __onWait(self):
        logger.debug(f"{self.__class__.__name__}.___onWait()")
        self.current_type = Order.Type.WAIT
        self.parent().updateWidget()

    @QtCore.pyqtSlot()  #__onTrailing
    def __onTrailing(self):
        logger.debug(f"{self.__class__.__name__}.___onTrailing()")
        self.current_type = Order.Type.TRAILING
        self.parent().updateWidget()


class UOrderPrice(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGroupBox.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__config()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.market_check = QtWidgets.QCheckBox("Market price", self)
        self.market_price = QtWidgets.QDoubleSpinBox(self)
        self.active_check = QtWidgets.QCheckBox("Price", self)
        self.active_price = QtWidgets.QDoubleSpinBox(self)
        self.execute_check = QtWidgets.QCheckBox("Execute price ", self)
        self.execute_price = QtWidgets.QDoubleSpinBox(self)
        self.timeout_check = QtWidgets.QCheckBox("Timeout", self)
        self.timeout_val = QtWidgets.QTimeEdit(time(1, 5), self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.market_check)
        hbox1.addWidget(self.market_price)
        hbox1.addWidget(self.active_check)
        hbox1.addWidget(self.active_price)
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.execute_check)
        hbox2.addWidget(self.execute_price)
        hbox3 = QtWidgets.QHBoxLayout()
        hbox3.addWidget(self.timeout_check)
        hbox3.addWidget(self.timeout_val)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        self.setLayout(vbox)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.execute_check.stateChanged.connect(self.__onCheckExecPrice)
        self.timeout_check.stateChanged.connect(self.__onCheckTimeout)

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.market_check.setMaximumWidth(128)
        self.market_price.setRange(0, 1000000000)
        self.market_price.setMinimumWidth(100)
        self.market_price.setReadOnly(True)
        self.active_check.setMaximumWidth(128)
        self.active_price.setRange(0, 1000000000)
        self.active_price.setMinimumWidth(100)
        self.execute_check.setMaximumWidth(128)
        self.execute_price.setRange(0, 1000000000)
        self.execute_price.setSpecialValueText("market")
        self.execute_price.setValue(0)
        self.execute_price.setMinimumWidth(128)
        self.timeout_val.setMinimumWidth(100)
        self.timeout_check.setMaximumWidth(128)
        sp = QtWidgets.QSizePolicy.Policy.Minimum
        self.setSizePolicy(sp, sp)

    def __setStep(self):
        logger.debug(f"{self.__class__.__name__}.__setStep()")
        step = self.parent().currentAsset().min_price_step
        precision = len(str(step).split(".")[1])
        self.active_price.setSingleStep(step)
        self.active_price.setDecimals(precision)
        self.execute_price.setSingleStep(step)
        self.execute_price.setDecimals(precision)

    @QtCore.pyqtSlot()  #__forMarket
    def __forMarket(self):
        logger.debug(f"{self.__class__.__name__}.__onMarket()")
        self.market_check.setVisible(True)
        self.market_check.setEnabled(False)
        self.market_check.setChecked(True)
        self.market_price.setVisible(True)
        self.active_check.setVisible(False)
        self.active_check.setEnabled(False)
        self.active_check.setChecked(False)
        self.active_price.setVisible(False)
        self.execute_check.setChecked(False)
        self.execute_check.setEnabled(False)
        self.execute_price.setEnabled(False)
        self.timeout_check.setChecked(False)
        self.timeout_check.setEnabled(False)
        self.timeout_val.setEnabled(False)
        self.current_type = Order.Type.MARKET
        asset = self.parent().currentAsset()
        if asset:
            self.market_price.setSpecialValueText(f"~{asset.last_price}")

    @QtCore.pyqtSlot()  #__forLimit
    def __forLimit(self):
        logger.debug(f"{self.__class__.__name__}.___onLimit()")
        self.market_check.setVisible(False)
        self.market_check.setEnabled(False)
        self.market_check.setChecked(False)
        self.market_price.setVisible(False)
        self.active_check.setVisible(True)
        self.active_check.setEnabled(True)
        self.active_check.setChecked(True)
        self.active_price.setVisible(True)
        self.active_price.setFocus(Qt.FocusReason.MouseFocusReason)
        self.execute_check.setChecked(False)
        self.execute_check.setEnabled(False)
        self.execute_price.setEnabled(False)
        self.timeout_check.setEnabled(False)
        self.timeout_check.setChecked(False)
        self.timeout_val.setEnabled(False)
        self.current_type = Order.Type.LIMIT

    @QtCore.pyqtSlot()  #__forStop
    def __forStop(self):
        logger.debug(f"{self.__class__.__name__}.___onLimit()")
        self.market_check.setVisible(False)
        self.market_check.setEnabled(False)
        self.market_check.setChecked(False)
        self.market_price.setVisible(False)
        self.active_check.setVisible(True)
        self.active_check.setEnabled(True)
        self.active_check.setChecked(True)
        self.active_price.setVisible(True)
        self.active_price.setFocus(Qt.FocusReason.MouseFocusReason)
        self.execute_check.setEnabled(True)
        self.execute_check.setChecked(False)
        self.execute_price.setEnabled(False)
        self.timeout_check.setEnabled(False)
        self.timeout_check.setChecked(False)
        self.timeout_val.setEnabled(False)
        self.current_type = Order.Type.STOP

    @QtCore.pyqtSlot()  #__forWait
    def __forWait(self):
        logger.debug(f"{self.__class__.__name__}.___onWait()")
        self.market_check.setVisible(False)
        self.market_check.setEnabled(False)
        self.market_check.setChecked(False)
        self.market_price.setVisible(False)
        self.active_check.setVisible(True)
        self.active_check.setEnabled(True)
        self.active_check.setChecked(True)
        self.active_price.setVisible(True)
        self.active_price.setFocus(Qt.FocusReason.MouseFocusReason)
        self.execute_check.setEnabled(True)
        self.execute_check.setChecked(False)
        self.execute_price.setEnabled(False)
        self.timeout_check.setEnabled(True)
        self.timeout_check.setChecked(False)
        self.timeout_val.setEnabled(False)
        self.current_type = Order.Type.WAIT

    @QtCore.pyqtSlot()  #__forTrailing
    def __forTrailing(self):
        logger.debug(f"{self.__class__.__name__}.___onTrailing()")
        self.current_type = Order.Type.TRAILING

    @QtCore.pyqtSlot()  #__onCheckExecPrice
    def __onCheckExecPrice(self):
        logger.debug(f"{self.__class__.__name__}.__onCheckExecPrice()")
        state = self.execute_check.isChecked()
        self.execute_price.setEnabled(state)
        if state:
            val = self.active_price.value()
            self.execute_price.setValue(val)
        else:
            val = self.execute_price.minimum()
            self.execute_price.setValue(val)

    @QtCore.pyqtSlot()  #__onCheckTimeout
    def __onCheckTimeout(self):
        logger.debug(f"{self.__class__.__name__}.__onCheckTimeout()")
        state = self.timeout_check.isChecked()
        self.timeout_val.setEnabled(state)

    def setPrice(self, price):
        logger.debug(f"{self.__class__.__name__}.__setPrice()")
        last_price = self.parent().currentAsset().last_price
        if price is None:
            price = last_price
        self.active_price.setValue(price)
        if self.execute_check.isChecked():
            self.execute_price.setValue(price)
        self.market_price.setSpecialValueText(f"~{last_price}")
        self.__setStep()

    def updateWidget(self):
        order_type = self.parent().currentType()
        types = {
            Order.Type.MARKET:   self.__forMarket,
            Order.Type.LIMIT:    self.__forLimit,
            Order.Type.STOP:     self.__forStop,
            Order.Type.WAIT:     self.__forWait,
            Order.Type.TRAILING: self.__forTrailing,
            }
        types[order_type]()


class UQuantity(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__current_asset = None
        self.__config()
        self.__createWidgets()
        self.__createLayots()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.lots = QtWidgets.QSpinBox(self)
        self.lots.setRange(1, 1_000_000)
        self.lots_label = QtWidgets.QLabel("Lots", self)
        self.quantity = QtWidgets.QSpinBox(self)
        self.quantity.setRange(1, 1_000_000_000)
        self.quantity.setReadOnly(True)
        self.quantity_label = QtWidgets.QLabel("Quantity", self)
        self.amount = QtWidgets.QDoubleSpinBox(self)
        self.amount.setRange(1, 1_000_000_000)
        self.amount.setReadOnly(True)
        self.amount_label = QtWidgets.QLabel("Amount", self)
        self.max_buy = QtWidgets.QLabel("Max buy: n (N)", self)
        self.max_sell = QtWidgets.QLabel("Max sell: n (N)", self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.max_buy)
        hbox.addWidget(self.max_sell)
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.lots_label,     0, 0)
        grid.addWidget(self.quantity_label, 0, 1)
        grid.addWidget(self.amount_label,   0, 2)
        grid.addWidget(self.lots,           1, 0)
        grid.addWidget(self.quantity,       1, 1)
        grid.addWidget(self.amount,         1, 2)
        grid.addLayout(hbox,                2, 0, 1, 3)
        self.setLayout(grid)

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        sp = QtWidgets.QSizePolicy.Policy.Minimum
        self.setSizePolicy(sp, sp)

    def updateWidget(self):
        asset = self.parent().currentAsset()
        if asset:
            price = self.parent().currentPrice()
            lots = self.lots.value()
            quantity = int(asset.lot * lots)
            amount = price * quantity
            self.lots_label.setText(f"Lots x{asset.lot}")
            self.quantity.setValue(quantity)
            self.amount.setValue(amount)


class UStopTake(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createStopGroup()
        self.__createTakeGroup()
        self.__createLabels()
        self.__createLayots()
        self.__config()

    def __createStopGroup(self):
        logger.debug(f"{self.__class__.__name__}.__createStopGroup()")
        self.stop_percent = QtWidgets.QDoubleSpinBox(self)
        self.stop_price = QtWidgets.QDoubleSpinBox(self)
        self.stop_change = QtWidgets.QDoubleSpinBox(self)
        stop = QtWidgets.QVBoxLayout()
        stop.addWidget(self.stop_percent)
        stop.addWidget(self.stop_price)
        stop.addWidget(self.stop_change)
        self.group_stop = QtWidgets.QGroupBox("stop-loss", self)
        self.group_stop.setLayout(stop)
        self.group_stop.setCheckable(True)
        self.group_stop.setChecked(False)

    def __createTakeGroup(self):
        logger.debug(f"{self.__class__.__name__}.__createTakeGroup()")
        self.take_percent = QtWidgets.QDoubleSpinBox(self)
        self.take_price = QtWidgets.QDoubleSpinBox(self)
        self.take_change = QtWidgets.QDoubleSpinBox(self)
        take = QtWidgets.QVBoxLayout()
        take.addWidget(self.take_percent)
        take.addWidget(self.take_price)
        take.addWidget(self.take_change)
        self.group_take = QtWidgets.QGroupBox("take-profit", self)
        self.group_take.setLayout(take)
        self.group_take.setCheckable(True)
        self.group_take.setChecked(False)

    def __createLabels(self):
        logger.debug(f"{self.__class__.__name__}.__createLabels()")
        L = QtWidgets.QLabel
        labels = QtWidgets.QVBoxLayout()
        labels.addWidget(L("<center>%</center>", self))
        labels.addWidget(L("<center>Price</center>", self))
        labels.addWidget(L("<center>Change</center>", self))
        self.group_labels = QtWidgets.QGroupBox(" ", self)
        self.group_labels.setLayout(labels)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.group_stop, 0, 0)
        grid.addWidget(self.group_labels, 0, 1)
        grid.addWidget(self.group_take, 0, 2)
        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        sp = QtWidgets.QSizePolicy.Policy.Minimum
        self.setSizePolicy(sp, sp)


class UBuySellButton(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configButtons()
        self.__connection = False

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.buy = QtWidgets.QPushButton("Buy ____ lots\n0.00 rub", self)
        self.sell = QtWidgets.QPushButton("Sell ____ lots\n0.00 rub", self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.buy, 0, 0)
        grid.addWidget(self.sell, 0, 1)
        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)

    def __configButtons(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.buy.setStyleSheet(
            "QPushButton {"
                "color: white;"
                "padding: 1px;"
                "border-width: 0px;"
                "border-radius: 3px;"
                "background-color: #AA98BB6C;"
                "}"
            "QPushButton:hover {"
                "color: white;"
                "background-color: #CC98BB6C;"
                "}"
            "QPushButton:pressed {"
                "color: white;"
                "background-color: #98BB6C;"
                "}"
            "QPushButton:disabled {"
                "color: #848388;"
                "border-width: 1px;"
                "border-style: solid;"
                "border-color: #5d5e60;"
                "background-color: #373737;"
                "}"
            )
        self.sell.setStyleSheet(
            "QPushButton {"
                "color: white;"
                "padding: 1px;"
                "border-width: 0px;"
                "border-radius: 3px;"
                "background-color: #AAFF5D62;"
                "}"
            "QPushButton:hover {"
                "color: white;"
                "background-color: #CCFF5D62;"
                "}"
            "QPushButton:pressed {"
                "color: white;"
                "background-color: #FF5D62"
                "}"
            "QPushButton:disabled {"
                "color: #848388;"
                "border-style: solid;"
                "border-width: 1px;"
                "border-color: #5d5e60;"
                "background-color: #373737;"
                "}"
            )

    def updateWidget(self):
        logger.debug(f"{self.__class__.__name__}.updateWidget()")
        account = self.parent().currentAccount()
        asset = self.parent().currentAsset()
        if account is not None and asset is not None:
            self.buy.setEnabled(True)
            self.sell.setEnabled(True)
        else:
            self.buy.setEnabled(False)
            self.sell.setEnabled(False)
        lots = self.parent().currentLots()
        price = self.parent().currentPrice()
        ticker = asset.ticker if asset else "____"
        amount = lots * asset.lot * price if asset else 0.0
        self.buy.setText(f"Buy {ticker} {lots} lots\n {amount:.2f} rub")
        self.sell.setText(f"Sell {ticker} {lots} lots\n {amount:.2f} rub")



class OrderDialog(QtWidgets.QDialog):
    """ Signal """
    newOrder = QtCore.pyqtSignal(Order)

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__current_account = None
        self.__current_asset = None
        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__initUI()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFont(Font.MONO)

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.asset =        UAssetInfo(self)
        self.type =         UOrderType(self)
        self.price =        UOrderPrice(self)
        self.quantity =     UQuantity(self)
        self.stop_take =    UStopTake(self)
        self.button =       UBuySellButton(self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.asset)
        vbox.addWidget(self.type)
        vbox.addWidget(self.price)
        vbox.addWidget(self.quantity)
        vbox.addWidget(self.stop_take)
        vbox.addWidget(self.button)
        vbox.addStretch()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.price.market_price.valueChanged.connect(self.__onPriceChanged)
        self.price.active_price.valueChanged.connect(self.__onPriceChanged)
        self.price.execute_price.valueChanged.connect(self.__onPriceChanged)
        self.quantity.lots.valueChanged.connect(self.__onLotsChanged)
        self.button.buy.clicked.connect(self.__onBuy)
        self.button.sell.clicked.connect(self.__onSell)

    def __initUI(self):
        logger.debug(f"{self.__class__.__name__}.__initUI()")
        # self.button.buy.setDisabled(True)
        # self.button.sell.setDisabled(True)
        self.type.market.trigger()

    def __createBuyOrder(self):
        logger.debug(f"{self.__class__.__name__}.__createBuyOrder()")
        iorder = IOrder(
            signal= Signal.Type.MANUAL,
            TYPE= self.currentType(),
            direction= Order.Direction.BUY,
            asset= self.currentAsset(),
            lots= self.currentLots(),
            price= self.currentActivePrice(),
            exec_price= self.currentExecutePrice(),
            timeout= self.currentTimeout(),
            status= Order.Status.NEW,
            parent= None,
            )
        return iorder

    def __createSellOrder(self):
        logger.debug(f"{self.__class__.__name__}.__createSellOrder()")
        iorder = IOrder(
            signal= Signal.Type.MANUAL,
            TYPE= self.currentType(),
            direction= Order.Direction.SELL,
            asset= self.currentAsset(),
            lots= self.currentLots(),
            price= self.currentActivePrice(),
            exec_price= self.currentExecutePrice(),
            timeout= self.currentTimeout(),
            status= Order.Status.NEW,
            parent= None,
            )
        return iorder

    @QtCore.pyqtSlot()  #__onPriceChanged
    def __onPriceChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onPriceChanged()")
        self.quantity.updateWidget()
        self.button.updateWidget()

    @QtCore.pyqtSlot()  #__onLotsChanged
    def __onLotsChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onLotsChanged()")
        self.quantity.updateWidget()
        self.button.updateWidget()

    @QtCore.pyqtSlot()  #__onBuy
    def __onBuy(self):
        logger.debug(f"{self.__class__.__name__}.__onBuy()")
        order = self.__createBuyOrder()
        self.newOrder.emit(order)
        self.__current_account.post(order)

    @QtCore.pyqtSlot()  #__onSell
    def __onSell(self):
        logger.debug(f"{self.__class__.__name__}.__onSell()")
        order = self.__createSellOrder()
        self.newOrder.emit(order)
        self.__current_account.post(order)

    def setAsset(self, asset, price=None):
        logger.debug(f"{self.__class__.__name__}.setAsset()")
        self.__current_asset = asset
        self.asset.setAsset(asset)
        self.price.setPrice(price)
        self.updateWidget()

    def connectAccount(self, iaccount):
        logger.debug(f"{self.__class__.__name__}.connectAccount()")
        self.__current_account = iaccount
        self.updateWidget()

    def disconnectAccount(self, iaccount):
        logger.debug(f"{self.__class__.__name__}.disconnectAccount()")
        self.__current_account = None
        self.updateWidget()

    def updateWidget(self):
        logger.debug(f"{self.__class__.__name__}.updateWidget()")
        self.asset.updateWidget()
        self.price.updateWidget()
        self.quantity.updateWidget()
        self.button.updateWidget()

    def currentAccount(self):
        logger.debug(f"{self.__class__.__name__}.currentAccount()")
        return self.__current_account

    def currentAsset(self):
        logger.debug(f"{self.__class__.__name__}.currentAsset()")
        return self.asset.current_asset

    def currentType(self):
        logger.debug(f"{self.__class__.__name__}.currentType()")
        return self.type.current_type

    def currentPrice(self):
        if self.currentAsset() is None:
            return
        if self.currentType() == Order.Type.MARKET:
            price = self.currentAsset().last_price
        elif self.price.execute_check.isChecked():
            price = float(self.price.execute_price.cleanText())
        elif self.price.active_check.isChecked():
            price = float(self.price.active_price.cleanText())
        else:
            price = 0.0
        return price

    def currentActivePrice(self):
        if self.price.active_check.isChecked():
            price = float(self.price.active_price.cleanText())
            return price
        else:
            return None

    def currentExecutePrice(self):
        if self.price.execute_check.isChecked():
            price = float(self.price.execute_price.cleanText())
            return price
        else:
            return None

    def currentTimeout(self):
        if self.price.timeout_check.isChecked():
            timeout = self.price.timeout_val.time
            print("TODO: РАЗБЕРИСЬ С ВИДЖЕТОМ ВРЕМЕНИ")
            print(timeout)
            return None
        else:
            return None

    def currentLots(self):
        logger.debug(f"{self.__class__.__name__}.currentLots()")
        return self.quantity.lots.value()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = OrderDialog()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())

