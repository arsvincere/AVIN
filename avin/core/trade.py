#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from avin.config import Usr
from avin.const import ONE_DAY
from avin.core.asset import Asset
from avin.core.chart import Chart
from avin.core.id import Id
from avin.core.operation import Operation
from avin.core.order import Order
from avin.core.timeframe import TimeFrame
from avin.data import AssetType, InstrumentId
from avin.keeper import Keeper
from avin.utils import AsyncSignal, logger


class Trade:  # {{{
    class Type(enum.Enum):  # {{{
        UNDEFINE = 0
        LONG = 1
        SHORT = 2

        @classmethod  # fromStr
        def fromStr(cls, string: str) -> Trade.Type:
            types = {
                "LONG": Trade.Type.LONG,
                "SHORT": Trade.Type.SHORT,
            }
            return types[string]

    # }}}
    class Status(enum.Enum):  # {{{
        UNDEFINE = enum.auto()
        INITIAL = enum.auto()
        PENDING = enum.auto()
        TRIGGERED = enum.auto()

        MAKE_ORDER = enum.auto()
        POST_ORDER = enum.auto()
        AWAIT_EXEC = enum.auto()
        OPENED = enum.auto()

        MAKE_STOP = enum.auto()
        MAKE_TAKE = enum.auto()
        POST_STOP = enum.auto()
        POST_TAKE = enum.auto()

        ACTIVE = enum.auto()
        CLOSING = enum.auto()

        CLOSED = enum.auto()
        CANCELED = enum.auto()
        BLOCKED = enum.auto()

        @classmethod  # fromStr
        def fromStr(cls, string: str) -> Trade.Status:
            statuses = {
                "INITIAL": Trade.Status.INITIAL,
                "PENDING": Trade.Status.PENDING,
                "TRIGGERED": Trade.Status.TRIGGERED,
                "MAKE_ORDER": Trade.Status.MAKE_ORDER,
                "POST_ORDER": Trade.Status.POST_ORDER,
                "AWAIT_EXEC": Trade.Status.AWAIT_EXEC,
                "OPENED": Trade.Status.OPENED,
                "MAKE_STOP": Trade.Status.MAKE_STOP,
                "MAKE_TAKE": Trade.Status.MAKE_TAKE,
                "POST_STOP": Trade.Status.POST_STOP,
                "POST_TAKE": Trade.Status.POST_TAKE,
                "ACTIVE": Trade.Status.ACTIVE,
                "CLOSING": Trade.Status.CLOSING,
                "CLOSED": Trade.Status.CLOSED,
                "CANCELED": Trade.Status.CANCELED,
                "BLOCKED": Trade.Status.BLOCKED,
            }
            return statuses[string]

    # }}}
    def __init__(  # {{{
        self,
        dt: datetime,
        strategy: str,
        version: str,
        trade_type: Trate.Type,
        asset_id: InstrumentId,
        status: Trade.Status = Status.INITIAL,
        trade_id: Optional[Id] = None,
        orders: Optional[list] = None,
        operations: Optional[list] = None,
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")

        if orders is None:
            orders = list()
        if operations is None:
            operations = list()

        # TODO: это похоже на пережиток сохранения в json
        # сейчас это не нужно вообще можно просто поля класса сделать
        self.__info = {
            "trade_id": trade_id,
            "datetime": dt,
            "status": status,
            "strategy": strategy,
            "version": version,
            "type": trade_type,
            "asset_id": asset_id,
            # "result": None,
            # "percent": None,
            # "holding_days": None,
            # "percentPerDay": None,
            # "buy_amount": None,
            # "sell_amount": None,
            # "commission": None,
            # "open_datetime": None,
            # "open_price": None,
            # "close_datetime": None,
            # "close_price": None,
            # "stop_price": None,
            # "take_price": None,
        }
        self.__orders = orders
        self.__operations = operations
        self.__blocked = False

        # signals
        self.opened = AsyncSignal(object)
        self.closed = AsyncSignal(object)
        self.statusChanged = AsyncSignal(object)

    # }}}
    def __str__(self):  # {{{
        dt = self.dt + Usr.TIME_DIF
        dt = dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"{dt} [{self.status.name}] {self.strategy}-{self.version} "
            f"{self.asset_id.ticker} {self.type.name.lower()}"
        )
        return string

    # }}}
    @property  # trade_id# {{{
    def trade_id(self):
        return self.__info["trade_id"]

    # }}}
    @property  # dt# {{{
    def dt(self):
        return self.__info["datetime"]

    # }}}
    @property  # status# {{{
    def status(self):
        return self.__info["status"]

    # }}}
    @property  # strategy# {{{
    def strategy(self):
        return self.__info["strategy"]

    # }}}
    @property  # version# {{{
    def version(self):
        return self.__info["version"]

    # }}}
    @property  # type# {{{
    def type(self):
        return self.__info["type"]

    # }}}
    @property  # asset_id# {{{
    def asset_id(self):
        return self.__info["asset_id"]

    # }}}
    @property  # orders# {{{
    def orders(self):
        return self.__orders

    # }}}
    @property  # operations# {{{
    def operations(self):
        return self.__operations

    # }}}
    # @async_slot  #onOrderPosted # {{{
    async def onOrderPosted(self, order):
        assert order.trade_id == self.trade_id
        if self.status.value < Trade.Status.AWAIT_EXEC.value:
            await self.setStatus(Trade.Status.AWAIT_EXEC)

        # otherwise trade already open, and this order is stop/take
        # or another. Essence - trade already open - do nothing with status
        pass

    # }}}
    # @async_slot  #onOrderExecuted # {{{
    async def onOrderExecuted(self, order, operation):
        assert order.trade_id == self.trade_id
        await self.attachOperation(operation)

        if self.status.value < Trade.Status.OPENED.value:
            await self.setStatus(Trade.Status.OPENED)

    # }}}
    async def setStatus(self, status: Trade.Status):  # {{{
        logger.debug(f"{self.__class__.__name__}.setStatus()")

        self.__info["status"] = status
        await Trade.update(self)

        # emiting special signal for this status
        if status == Trade.Status.OPENED:
            await self.opened.async_emit(self)
        elif status == Trade.Status.CLOSED:
            await self.closed.async_emit(self)

        # emiting common signal
        await self.statusChanged.async_emit(self)

    # }}}
    async def attachOrder(self, order: Order):  # {{{
        logger.debug(f"{self.__class__.__name__}.attachOrder()")

        await order.setParentTrade(self)
        await self.__connectOrderSignals(order)
        self.__orders.append(order)

    # }}}
    async def attachOperation(self, operation: Operation):  # {{{
        logger.debug(f"{self.__class__.__name__}.attachOperation()")

        await operation.setParentTrade(self)
        self.__operations.append(operation)

        # check lots count & update status
        if self.lots() == 0:
            await self.setStatus(Trade.Status.CLOSED)

    # }}}
    async def chart(self, timeframe: TimeFrame) -> Chart:  # {{{
        logger.debug(f"{self.__class__.__name__}.chart()")

        assert self.asset_id.type == AssetType.SHARE
        end = self.dt
        begin = self.dt - Chart.DEFAULT_BARS_COUNT * timeframe
        chart = await Chart.load(self.asset_id, timeframe, begin, end)
        return chart

    # }}}
    def isLong(self):  # {{{
        return self.__info["type"] == Trade.Type.LONG

    # }}}
    def isShort(self):  # {{{
        return self.__info["type"] == Trade.Type.SHORT

    # }}}
    def isWin(self):  # {{{
        assert self.status == Trade.Status.CLOSED
        return self.result > 0

    # }}}
    def isLoss(self):  # {{{
        assert self.status == Trade.Status.CLOSED
        return self.result <= 0

    # }}}
    def isBlocked(self):  # {{{
        return self.__blocked

    # }}}
    def setBlocked(self, val: bool):  # {{{
        self.__blocked = val

    # }}}
    def lots(self):  # {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.BUY:
                total += op.lots
            elif op.direction == Operation.Direction.SELL:
                total -= op.lots
        return total

    # }}}
    def quantity(self):  # {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.BUY:
                total += op.quantity
            elif op.direction == Operation.Direction.SELL:
                total -= op.quantity
        return total

    # }}}
    def buyQuantity(self):  # {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.BUY:
                total += op.quantity
        return total

    # }}}
    def sellQuantity(self):  # {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.SELL:
                total += op.quantity
        return total

    # }}}
    def amount(self):  # {{{
        if self.status == Trade.Status.CLOSED:
            return 0.0
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.BUY:
                total += op.amount
            elif op.direction == Operation.Direction.SELL:
                total -= op.amount
        return total

    # }}}
    def buyAmount(self):  # {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.BUY:
                total += op.amount
        return total

    # }}}
    def sellAmount(self):  # {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.SELL:
                total += op.amount
        return total

    # }}}
    def commission(self):  # {{{
        return self.buyCommission() + self.sellCommission()

    # }}}
    def buyCommission(self):  # {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.BUY:
                total += op.commission
        return total

    # }}}
    def sellCommission(self):  # {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.SELL:
                total += op.commission
        return total

    # }}}
    def average(self):  # {{{
        if self.quantity() == 0:
            return 0.0
        return self.amount() / self.quantity()

    # }}}
    def buyAverage(self):  # {{{
        if self.buyQuantity() == 0:
            return 0.0
        return self.buyAmount() / self.buyQuantity()

    # }}}
    def sellAverage(self):  # {{{
        if self.sellQuantity() == 0:
            return 0.0
        return self.sellAmount() / self.sellQuantity()

    # }}}
    def openDateTime(self):  # {{{
        assert self.status.value >= Trade.Status.OPENED.value
        return self.__operations[0].dt

    # }}}
    def openPrice(self):  # {{{
        assert self.status.value >= Trade.Status.OPENED.value
        assert self.status.value != Trade.Status.CANCELED.value

        if self.isLong():
            return self.buyAverage()

        return self.sellAverage()

    # }}}
    def closeDateTime(self):  # {{{
        assert self.status in (
            Trade.Status.CLOSED,
            Trade.Status.ARCHIVE,
        )
        return self.__operations[-1].dt

    # }}}
    def closePrice(self):  # {{{
        assert self.status == Trade.Status.CLOSED
        if self.isLong():
            return self.sellAverage()

        return self.buyAverage()

    # }}}
    # def stop_price(self):# {{{
    #   # NOTE: может быть стоит сделать отдельное добавление стопа и тейка
    #   # не через общее addOrder, а через addStopLoss addTakeProfit
    #   # тогда там и можно будет легко выцепить цену стопа тейка...
    #   # и вообще нужы ли эти параметры в трейде?
    #   # ну на графике хорошо смотреть где был стоп тейк...
    #   # а если стратегия не пользуется стоп тейком? Всмысле не пользуется!
    #   # стоп должен быть ВСЕГДА.
    #   # а тейк? какой смысл делать его не фиксированным к цене?
    #   # пока не знаю таких кейсов
    #     return self.__info["stop_price"]
    # # }}}
    # def take_price(self):# {{{
    #     return self.__info["take_price"]
    # # }}}
    def result(self):  # {{{
        assert self.status == Trade.Status.CLOSED
        result = (
            self.sellAmount()
            - self.buyAmount()
            - self.buyCommission()
            - self.sellCommission()
        )
        return round(result, 2)

    # }}}
    def holdingDays(self):  # {{{
        opn_dt = self.__operations[0].dt
        cls_dt = self.__operations[-1].dt
        holding = cls_dt - opn_dt + ONE_DAY
        return holding.days

    # }}}
    def percent(self):  # {{{
        assert self.status == Trade.Status.CLOSED
        persent = self.result() / self.buyAmount() * 100
        return round(persent, 2)

    # }}}
    def percentPerDay(self):  # {{{
        assert self.status == Trade.Status.CLOSED
        persent = self.result() / self.buyAmount() * 100
        holding = self.holdingDays()
        persent_per_day = persent / holding
        return round(persent_per_day, 2)

    # }}}
    @classmethod  # fromRecord{{{
    async def fromRecord(cls, record):
        logger.debug(f"{cls.__name__}.fromRecord()")

        trade_id = record["trade_id"]

        # request operations of trade
        operations = await Keeper.get(
            Operation,
            trade_id=trade_id,
        )

        # request orders of trade
        orders = await Keeper.get(
            Order,
            trade_id=trade_id,
        )

        # create trade
        ID = await InstrumentId.byFigi(record["figi"])
        trade = Trade(
            dt=record["dt"],
            strategy=record["strategy"],
            version=record["version"],
            trade_type=Trade.Type.fromStr(record["type"]),
            asset_id=ID,
            status=Trade.Status.fromStr(record["status"]),
            trade_id=Id.fromStr(record["trade_id"]),
            orders=orders,
            operations=operations,
        )

        # connect signals of attached orders
        for order in trade.orders:
            await trade.__connectOrderSignals(order)

        return trade

    # }}}
    @classmethod  # save  # {{{
    async def save(cls, trade: Trade) -> None:
        logger.debug(f"{cls.__name__}.save()")
        await Keeper.add(trade)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, trade_id: Id) -> Trade:
        logger.debug(f"{cls.__name__}.load()")

        response = await Keeper.get(cls, trade_id=trade_id)
        if len(response) == 1:  # response == [ Trade, ]
            return response[0]

        # else: error, trade not found
        logger.error(f"trade_id='{trade_id}' does not exist!")
        exit(3)

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, trade: Trade) -> None:
        logger.debug(f"{cls.__name__}.delete()")
        await Keeper.delete(trade)

    # }}}
    @classmethod  # update  # {{{
    async def update(cls, trade: Trade) -> None:
        logger.debug(f"{cls.__name__}.update()")
        await Keeper.update(trade)

    # }}}
    async def __connectOrderSignals(self, order: Order):  # {{{
        logger.debug(
            f"{self.__class__.__name__}.__connectOrderSignals('{order}')"
        )
        await order.posted.async_connect(self.onOrderPosted)
        await order.executed.async_connect(self.onOrderExecuted)

    # }}}


# }}}
class TradeList:  # {{{
    def __init__(  # {{{
        self, name: str, trades=None, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__name = name
        self.__trades = trades if trades else list()
        self.__parent = parent
        self.__childs: list[TradeList] = list()
        self.__asset = parent.asset if parent else None

    # }}}
    def __iter__(self):  # {{{
        return iter(self.__trades)

    # }}}
    def _createChild(self, trades, suffix):  # {{{
        child_name = f"- {suffix}"
        child = TradeList(name=child_name, trades=trades, parent=self)
        child.__asset = self.asset
        self.__childs.append(child)
        return child

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__name

    # }}}
    @property  # trades# {{{
    def trades(self):
        return self.__trades

    # }}}
    @property  # count# {{{
    def count(self):
        return len(self.__trades)

    # }}}
    @property  # asset# {{{
    def asset(self):
        return self.__asset

    # }}}
    def parent(self):  # {{{
        """Return parent trade list"""
        logger.debug(f"{self.__class__.__name__}.parent()")

        return self.__parent

    # }}}
    def add(self, trade: Trade) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")
        self.__trades.append(trade)

    # }}}
    def remove(self, trade: Trade) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove()")
        self.__trades.remove(trade)

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")
        self.__trades.clear()

    # }}}
    def find(self, trade_id: Id) -> Trade | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.find()")

        for trade in self.__trades:
            if trade.trade_id == trade_id:
                return trade
        return None

    # }}}
    def selectLong(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectLong()")

        selected = list()
        for trade in self.__trades:
            if trade.isLong():
                selected.append(trade)
        child = self._createChild(selected, "long")
        return child

    # }}}
    def selectShort(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectShort()")

        selected = list()
        for trade in self.__trades:
            if trade.isShort():
                selected.append(trade)
        child = self._createChild(selected, "short")
        return child

    # }}}
    def selectWin(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectWin()")

        selected = list()
        for trade in self.__trades:
            if trade.isWin():
                selected.append(trade)
        child = self._createChild(selected, "win")
        return child

    # }}}
    def selectLoss(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectLoss()")

        selected = list()
        for trade in self.__trades:
            if trade.isLoss():
                selected.append(trade)
        child = self._createChild(selected, "loss")
        return child

    # }}}
    def selectAsset(self, asset: Asset):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectAsset()")

        selected = list()
        for trade in self.__trades:
            if trade.asset_id.figi == asset.figi:
                selected.append(trade)
        child = self._createChild(selected, suffix=asset.ticker)
        child.__asset = asset
        return child

    # }}}
    def selectStatus(self, status: Trade.Status):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectStatus()")

        selected = list()
        for trade in self.__trades:
            if trade.status == status:
                selected.append(trade)
        child = self._createChild(selected, suffix=status.name)
        return child

    # }}}
    def selectFilter(f):
        assert False

    @classmethod  # fromRecord # {{{
    async def fromRecord(cls, record: asyncpg.Record):
        logger.debug(f"{cls.__name__}.fromRecord()")
        name = record["name"]
        trade_ids = record["trades"]

        trades = list()
        for trade_id in trade_ids:
            trade = await Trade.load(trade_id)
            trades.append(trade)

        tlist = cls(name, trades)
        return tlist

    # }}}
    @classmethod  # save# {{{
    async def save(cls, trade_list) -> None:
        logger.debug(f"{cls.__name__}.save()")
        await Keeper.add(trade_list)

    # }}}
    @classmethod  # load# {{{
    async def load(cls, name) -> TradeList | None:
        logger.debug(f"{cls.__name__}.load()")

        response = await Keeper.get(cls, name=name)
        if len(response) == 1:  # response == [ TradeList, ]
            return response[0]

        # else: error, trade list not found
        logger.error(f"Trade list '{name}' not found!")
        return None

    # }}}
    @classmethod  # update# {{{
    async def update(cls, trade_list) -> None:
        logger.debug(f"{cls.__name__}.update()")
        await Keeper.update(trade_list)

    # }}}
    @classmethod  # delete# {{{
    async def delete(cls, tlist):
        logger.debug(f"{cls.__name__}.delete()")
        await Keeper.delete(tlist)

    # }}}


# }}}
