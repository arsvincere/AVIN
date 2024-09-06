#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum

from avin.const import ONE_DAY, Usr
from avin.core.chart import Chart
from avin.core.id import Id
from avin.core.operation import Operation
from avin.core.order import Order
from avin.data import AssetType, InstrumentId
from avin.keeper import Keeper
from avin.utils import AsyncSignal, logger

# FIX: при удалении трейда, его ID остается в трейд листе..
# с одной стороны - трейды вообще никогда удаляться то не будут...
# с другой стороны во время юнит тестов или в работе тестера
# будут возникать ошибки, нарушение целостности данных


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
        UNDEFINE = 0
        INITIAL = 1
        PENDING = 2
        TRIGGERED = 3

        MAKE_ORDER = 10
        POST_ORDER = 11
        POSTED = 13
        OPENED = 14

        MAKE_STOP = 21
        MAKE_TAKE = 22
        POST_STOP = 23
        POST_TAKE = 24

        ACTIVE = 30

        OFF = 40

        FINISH = 50
        CLOSING = 51
        REMOVING = 52

        CLOSED = 60
        ARCHIVE = 70

        CANCELED = 90
        BLOKED = 91

        @classmethod  # fromStr
        def fromStr(cls, string: str) -> Trade.Type:
            statuses = {
                "INITIAL": Trade.Status.INITIAL,
                "PENDING": Trade.Status.PENDING,
                "TRIGGERED": Trade.Status.TRIGGERED,
                "MAKE_ORDER": Trade.Status.MAKE_ORDER,
                "POST_ORDER": Trade.Status.POST_ORDER,
                "POSTED": Trade.Status.POSTED,
                "OPENED": Trade.Status.OPENED,
                "MAKE_STOP": Trade.Status.MAKE_STOP,
                "MAKE_TAKE": Trade.Status.MAKE_TAKE,
                "POST_STOP": Trade.Status.POST_STOP,
                "POST_TAKE": Trade.Status.POST_TAKE,
                "ACTIVE": Trade.Status.ACTIVE,
                "OFF": Trade.Status.OFF,
                "FINISH": Trade.Status.FINISH,
                "CLOSING": Trade.Status.CLOSING,
                "REMOVING": Trade.Status.REMOVING,
                "CLOSED": Trade.Status.CLOSED,
                "CANCELED": Trade.Status.CANCELED,
                "BLOKED": Trade.Status.BLOKED,
                "ARCHIVE": Trade.Status.ARCHIVE,
            }
            return statuses[string]

    # }}}
    def __init__(  # {{{
        self,
        dt: datetime,
        strategy: str,
        version: str,
        trade_type: Trade.Type,
        asset_id: str,
        status: Trade.Status = None,
        trade_id: Id = None,
        orders: list = None,
        operations: list = None,
    ):
        if status is None:
            status = Trade.Status.INITIAL
        if trade_id is None:
            trade_id = Id.newId(self)
        if orders is None:
            orders = list()
        if operations is None:
            operations = list()

        # XXX: а в нынешних условиях может нахуй не нужен тут словарь?
        # в json больше не сохраняю... может просто поля сделать?
        # ну по крайней мере ордера и операции достать из словаря...
        # в остальном то да... словарь можно оставить словарем..
        # и дописывать его в виде json в БД, и то... не весь, а только
        # те поля которые не включены в таблицу основную...
        # и еще!
        # думать какие поля держать в таблице. Результаты трейдов
        # закрытых, архивированных - их можно сразу прописать, хуйли
        # их считать то каждый раз...
        # но это все потом потом потом...
        # если понадобится быстродействие... пока пусть неуклюже и излишне
        # но подтягивается все все все. И все считать в реалтайме.
        self.__info = {
            "trade_id": trade_id,
            "datetime": dt,
            "status": status,
            "strategy": strategy,
            "version": version,
            "type": trade_type,
            "asset_id": asset_id,
            "orders": orders,
            "operations": operations,
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
        return self.__info["orders"]

    # }}}
    @property  # operations# {{{
    def operations(self):
        return self.__info["operations"]

    # }}}
    # @async_slot  #onOrderPosted # {{{
    async def onOrderPosted(self, order):
        assert order.trade_id == self.trade_id
        if self.status.value < Trade.Status.POSTED.value:
            await self.setStatus(Trade.Status.POSTED)

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
        # TODO:  self.__info["orders"] -> self.__orders
        await order.setParentTrade(self)
        await self.__connectOrderSignals(order)
        self.__info["orders"].append(order)

    # }}}
    async def attachOperation(self, operation: Operation):  # {{{
        # TODO:  self.__info["operations"] -> self.__operations

        await operation.setParentTrade(self)
        self.__info["operations"].append(operation)

        # check lots count & update status
        if self.lots() == 0:
            await self.setStatus(Trade.Status.CLOSED)

    # }}}
    async def chart(self, timeframe: TimeFrame) -> Chart:  # {{{
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
        for op in self.__info["operations"]:
            if op.direction == Operation.Direction.BUY:
                total += op.lots
            elif op.direction == Operation.Direction.SELL:
                total -= op.lots
        return total

    # }}}
    def quantity(self):  # {{{
        total = 0
        for op in self.__info["operations"]:
            if op.direction == Operation.Direction.BUY:
                total += op.quantity
            elif op.direction == Operation.Direction.SELL:
                total -= op.quantity
        return total

    # }}}
    def buyQuantity(self):  # {{{
        total = 0
        for op in self.__info["operations"]:
            if op.direction == Operation.Direction.BUY:
                total += op.quantity
        return total

    # }}}
    def sellQuantity(self):  # {{{
        total = 0
        for op in self.__info["operations"]:
            if op.direction == Operation.Direction.SELL:
                total += op.quantity
        return total

    # }}}
    def amount(self):  # {{{
        if self.status == Trade.Status.CLOSED:
            return 0.0
        total = 0
        for op in self.__info["operations"]:
            if op.direction == Operation.Direction.BUY:
                total += op.amount
            elif op.direction == Operation.Direction.SELL:
                total -= op.amount
        return total

    # }}}
    def buyAmount(self):  # {{{
        total = 0
        for op in self.__info["operations"]:
            if op.direction == Operation.Direction.BUY:
                total += op.amount
        return total

    # }}}
    def sellAmount(self):  # {{{
        total = 0
        for op in self.__info["operations"]:
            if op.direction == Operation.Direction.SELL:
                total += op.amount
        return total

    # }}}
    def commission(self):  # {{{
        return self.buyCommission() + self.sellCommission()

    # }}}
    def buyCommission(self):  # {{{
        total = 0
        for op in self.__info["operations"]:
            if op.direction == Operation.Direction.BUY:
                total += op.commission
        return total

    # }}}
    def sellCommission(self):  # {{{
        total = 0
        for op in self.__info["operations"]:
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
    def openDatetime(self):  # {{{
        assert self.status.value >= Trade.Status.OPENED.value
        return self.__info["operations"][0].dt

    # }}}
    def openPrice(self):  # {{{
        assert self.status.value >= Trade.Status.OPENED.value
        assert self.status.value != Trade.Status.CANCELED.value

        if self.isLong():
            return self.buyAverage()

        return self.sellAverage()

    # }}}
    def closeDatetime(self):  # {{{
        assert self.status in (
            Trade.Status.CLOSED,
            Trade.Status.ARCHIVE,
        )
        return self.__info["operations"][-1].dt

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
        opn_dt = self.__info["operations"][0].dt
        cls_dt = self.__info["operations"][-1].dt
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
            trade_id=Id.fromFloat(record["trade_id"]),
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
        await Keeper.add(trade)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, trade_id: Id) -> Trade:
        response = await Keeper.get(cls, trade_id=trade_id)
        if len(response) == 1:  # response == [ Trade, ]
            return response[0]

        # else: error, trade not found
        logger.error(f"trade_id='{trade_id}' does not exist!")
        exit(3)

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, trade: Trade) -> None:
        await Keeper.delete(trade)

    # }}}
    @classmethod  # update  # {{{
    async def update(cls, trade: Trade) -> None:
        await Keeper.update(trade)

    # }}}
    async def __connectOrderSignals(self, order: Order):  # {{{
        logger.debug(f"__connectOrderSignals {order}")
        await order.posted.async_connect(self.onOrderPosted)
        await order.executed.async_connect(self.onOrderExecuted)

    # }}}


# }}}
class TradeList:  # {{{
    def __init__(  # {{{
        self, name: str, trades=None, parent=None
    ):
        self._name = name
        self._trades = trades if trades else list()
        self._parent = parent
        self._childs = list()
        self._asset = parent.asset if parent else None

    # }}}
    def __iter__(self):  # {{{
        return iter(self._trades)

    # }}}
    def _createChild(self, trades, suffix):  # {{{
        child_name = f"- {suffix}"
        child = TradeList(name=child_name, trades=trades, parent=self)
        child._asset = self.asset
        self._childs.append(child)
        return child

    # }}}
    @property  # name# {{{
    def name(self):
        return self._name

    # }}}
    @property  # trades# {{{
    def trades(self):
        return self._trades

    # }}}
    @property  # count# {{{
    def count(self):
        return len(self._trades)

    # }}}
    @property  # asset# {{{
    def asset(self):
        return self._asset

    # }}}
    def parent(self):  # {{{
        return self._parent

    # }}}
    def add(self, trade: Trade) -> None:  # {{{
        self._trades.append(trade)
        trade._parent = self

    # }}}
    def remove(self, trade: Trade) -> None:  # {{{
        self._trades.remove(trade)

    # }}}
    def clear(self) -> None:  # {{{
        self._trades.clear()

    # }}}
    def find(self, trade_id: Id) -> Trade:  # {{{
        for trade in self._trades:
            if trade.trade_id == trade_id:
                return trade
        return None

    # }}}
    def selectLong(self):  # {{{
        selected = list()
        for trade in self._trades:
            if trade.isLong():
                selected.append(trade)
        child = self._createChild(selected, "long")
        return child

    # }}}
    def selectShort(self):  # {{{
        selected = list()
        for trade in self._trades:
            if trade.isShort():
                selected.append(trade)
        child = self._createChild(selected, "short")
        return child

    # }}}
    def selectWin(self):  # {{{
        selected = list()
        for trade in self._trades:
            if trade.isWin():
                selected.append(trade)
        child = self._createChild(selected, "win")
        return child

    # }}}
    def selectLoss(self):  # {{{
        selected = list()
        for trade in self._trades:
            if trade.isLoss():
                selected.append(trade)
        child = self._createChild(selected, "loss")
        return child

    # }}}
    def selectAsset(self, asset: Asset):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectAsset()")
        selected = list()
        for trade in self._trades:
            if trade.asset_id.figi == asset.figi:
                selected.append(trade)
        child = self._createChild(selected, suffix=asset.ticker)
        child._asset = asset
        return child

    # }}}
    def selectStatus(self, status: Trade.Status):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectStatus()")
        selected = list()
        for trade in self._trades:
            if trade.status == status:
                selected.append(trade)
        child = self._createChild(selected, suffix=status.name)
        return child

    # }}}
    def selectFilter(f):
        assert False

    @classmethod  # fromRecord # {{{
    async def fromRecord(cls, record):
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
        await Keeper.add(trade_list)

    # }}}
    @classmethod  # load# {{{
    async def load(cls, name) -> TradeList:
        response = await Keeper.get(cls, name=name)
        if len(response) == 1:  # response == [ TradeList, ]
            return response[0]

        # else: error, trade list not found
        logger.error(f"Trade list '{name}' not found!")
        return None

    # }}}
    @classmethod  # update# {{{
    async def update(cls, trade_list) -> None:
        await Keeper.update(trade_list)

    # }}}
    @classmethod  # delete# {{{
    async def delete(cls, tlist):
        await Keeper.delete(tlist)

    # }}}


# }}}
