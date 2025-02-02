#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum
from typing import Any, Optional, TypeVar

from avin.config import Usr
from avin.const import ONE_DAY
from avin.core.asset import Asset, AssetList
from avin.core.chart import Chart
from avin.core.direction import Direction
from avin.core.id import Id
from avin.core.operation import Operation
from avin.core.order import Order, StopLoss, TakeProfit
from avin.core.range import Range
from avin.core.timeframe import TimeFrame
from avin.data import Instrument
from avin.keeper import Keeper
from avin.utils import AsyncSignal, Cmd, Date, DateTime, logger

Test = TypeVar("Test")
Trader = TypeVar("Trader")


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
        dt: DateTime,
        strategy: str,
        version: str,
        trade_type: Trate.Type,
        instrument: Instrument,
        status: Trade.Status = Status.INITIAL,
        trade_id: Optional[Id] = None,
        trade_list_name: Optional[str] = "",
        orders: Optional[list] = None,
        operations: Optional[list] = None,
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")

        if orders is None:
            orders = list()
        if operations is None:
            operations = list()

        self.dt = dt
        self.strategy = strategy
        self.version = version
        self.type = trade_type
        self.instrument = instrument
        self.status = status
        self.trade_id = trade_id
        self.trade_list_name = trade_list_name
        self.orders = orders if orders else list()
        self.operations = operations if operations else list()
        self.info: dict[str, Any] = dict()
        self.__blocked = False

        # signals
        self.opened = AsyncSignal(object)
        self.closed = AsyncSignal(object)
        self.statusChanged = AsyncSignal(object)

    # }}}
    def __str__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__str__()")

        dt = self.dt + Usr.TIME_DIF
        dt = dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"Trade="
            f"{dt} [{self.status.name}] {self.strategy}-{self.version} "
            f"{self.instrument.ticker} {self.type.name.lower()}"
        )
        return string

    # }}}
    def pretty(self) -> str:  # {{{
        logger.debug(f"{self.__class__.__name__}.pretty()")

        orders_text = ""
        for order in self.orders:
            text = order.pretty()
            orders_text += text

        operations_text = ""
        for operation in self.operations:
            text = operation.pretty()
            operations_text += text

        trade_text = f"""
id:         {self.trade_id}
dt:         {Usr.localTime(self.dt)}
strategy:   {self.strategy}
version:    {self.version}
type:       {self.type.name}
instrument: {self.instrument}
status:     {self.status.name}
trade_list: {self.trade_list_name}
blocked:    {self.__blocked}
------------------------------------------------------------------------------
buy:        {self.buyAverage()} * {self.buyQuantity()} = {self.buyAmount()}
sell:       {self.sellAverage()} * {self.sellQuantity()} = {self.sellAmount()}
commission: {self.commission()}
open_dt:    {Usr.localTime(self.openDateTime())}
close_dt:   {Usr.localTime(self.closeDateTime())}
open:       {self.openPrice()}
stop:       {self.stopPrice()} / {self.stopAbs()} / {self.stopPercent()}%
take:       {self.takePrice()} / {self.takeAbs()} / {self.takePercent()}%
------------------------------------------------------------------------------
result:     {self.result()}
days:       {self.holdingDays()}
percent:    {self.percent()}
ppd:        {self.percentPerDay()}
info:       {Cmd.toJson(self.info, indent=4)}

== Orders ====================================================================
{orders_text}
== Operations ================================================================
{operations_text}
"""
        return trade_text

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

        self.status = status
        await Trade.update(self)

        # emiting special signal for this status
        if status == Trade.Status.OPENED:
            await self.opened.aemit(self)
        elif status == Trade.Status.CLOSED:
            await self.closed.aemit(self)

        # emiting common signal
        await self.statusChanged.aemit(self)

    # }}}
    async def attachOrder(self, order: Order):  # {{{
        logger.debug(f"{self.__class__.__name__}.attachOrder()")

        await order.setParentTrade(self)
        await self.__connectOrderSignals(order)
        self.orders.append(order)

    # }}}
    async def attachOperation(self, operation: Operation):  # {{{
        logger.debug(f"{self.__class__.__name__}.attachOperation()")

        await operation.setParentTrade(self)
        self.operations.append(operation)

        # check lots count & update status
        if self.lots() == 0:
            await self.setStatus(Trade.Status.CLOSED)

    # }}}
    async def loadChart(  # {{{
        self, timeframe: TimeFrame | str, n=None
    ) -> Chart:
        logger.debug(f"{self.__class__.__name__}.chart()")
        assert self.instrument.type == Instrument.Type.SHARE

        if isinstance(timeframe, str):
            timeframe = TimeFrame(timeframe)

        if n is None:
            n = 5000  # default bars count

        end = self.dt
        begin = self.dt - n * timeframe

        chart = await Chart.load(self.instrument, timeframe, begin, end)
        chart.setHeadDatetime(self.dt)
        return chart

    # }}}

    def isLong(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.isLong()")

        return self.type == Trade.Type.LONG

    # }}}
    def isShort(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.isShort()")

        return self.type == Trade.Type.SHORT

    # }}}
    def isWin(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.isWin()")

        assert self.status == Trade.Status.CLOSED
        return self.result() > 0

    # }}}
    def isLoss(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.isLoss()")

        assert self.status == Trade.Status.CLOSED
        return self.result() <= 0

    # }}}
    def isBlocked(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.isBlocked()")

        return self.__blocked

    # }}}
    def setBlocked(self, val: bool):  # {{{
        logger.debug(f"{self.__class__.__name__}.setBlocked()")

        self.__blocked = val

    # }}}
    def lots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.lots()")

        total = 0
        for op in self.operations:
            if op.direction == Direction.BUY:
                total += op.lots
            elif op.direction == Direction.SELL:
                total -= op.lots
        return total

    # }}}
    def quantity(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.quantity()")

        total = 0
        for op in self.operations:
            if op.direction == Direction.BUY:
                total += op.quantity
            elif op.direction == Direction.SELL:
                total -= op.quantity
        return total

    # }}}
    def buyQuantity(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.buyQuantity()")

        total = 0
        for op in self.operations:
            if op.direction == Direction.BUY:
                total += op.quantity
        return total

    # }}}
    def sellQuantity(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.sellQuantity()")

        total = 0
        for op in self.operations:
            if op.direction == Direction.SELL:
                total += op.quantity
        return total

    # }}}
    def amount(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.amount()")

        if self.status == Trade.Status.CLOSED:
            return 0.0
        total = 0
        for op in self.operations:
            if op.direction == Direction.BUY:
                total += op.amount
            elif op.direction == Direction.SELL:
                total -= op.amount
        return total

    # }}}
    def buyAmount(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.buyAmount()")

        total = 0
        for op in self.operations:
            if op.direction == Direction.BUY:
                total += op.amount
        return total

    # }}}
    def sellAmount(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.sellAmount()")

        total = 0
        for op in self.operations:
            if op.direction == Direction.SELL:
                total += op.amount
        return total

    # }}}
    def commission(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.commission()")

        return self.buyCommission() + self.sellCommission()

    # }}}
    def buyCommission(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.buyCommission()")

        total = 0
        for op in self.operations:
            if op.direction == Direction.BUY:
                total += op.commission
        return total

    # }}}
    def sellCommission(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.sellCommission()")

        total = 0
        for op in self.operations:
            if op.direction == Direction.SELL:
                total += op.commission
        return total

    # }}}
    def average(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.average()")

        if self.quantity() == 0:
            return 0.0
        return self.amount() / self.quantity()

    # }}}
    def buyAverage(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.buyAverage()")

        if self.buyQuantity() == 0:
            return 0.0
        return self.buyAmount() / self.buyQuantity()

    # }}}
    def sellAverage(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.sellAverage()")

        if self.sellQuantity() == 0:
            return 0.0
        return self.sellAmount() / self.sellQuantity()

    # }}}
    def openDateTime(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.openDateTime()")

        assert self.status.value >= Trade.Status.OPENED.value
        return self.operations[0].dt

    # }}}
    def openPrice(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.openPrice()")

        assert self.status.value >= Trade.Status.OPENED.value
        assert self.status.value != Trade.Status.CANCELED.value

        if self.isLong():
            return self.buyAverage()

        return self.sellAverage()

    # }}}
    def closeDateTime(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.closeDateTime()")
        assert self.status == Trade.Status.CLOSED

        # FIX:
        # возможно из БД они в произвольном порядке загрузятся...
        # надо проверить, добавить сортировку по дате при загрузке

        return self.operations[-1].dt

    # }}}
    def closePrice(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.closePrice()")
        assert self.status == Trade.Status.CLOSED

        if self.isLong():
            return self.sellAverage()

        return self.buyAverage()

    # }}}
    def stopLoss(self) -> StopLoss | None:  # {{{
        for order in self.orders:
            if order.type == Order.Type.STOP_LOSS:
                return order

        return None

    # }}}
    def takeProfit(self) -> TakeProfit | None:  # {{{
        for order in self.orders:
            if order.type == Order.Type.TAKE_PROFIT:
                return order

        return None

    # }}}
    def stopPrice(self) -> float | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.stopPrice()")

        for order in self.orders:
            if order.type == Order.Type.STOP_LOSS:
                return order.stop_price

        return None

    # }}}
    def takePrice(self) -> float | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.takePrice()")

        for order in self.orders:
            if order.type == Order.Type.TAKE_PROFIT:
                return order.stop_price

        return None

    # }}}
    def stopAbs(self) -> float | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.stopAbs()")

        open_price = self.openPrice()
        stop_price = self.stopPrice()
        if stop_price is None:
            return None

        risk = abs(stop_price - open_price)
        return round(risk, 2)

    # }}}
    def takeAbs(self) -> float | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.takeAbs()")

        open_price = self.openPrice()
        take_price = self.takePrice()
        if take_price is None:
            return None

        profit = abs(take_price - open_price)
        return round(profit, 2)

    # }}}
    def stopPercent(self) -> float | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.stopPercent()")

        open_price = self.openPrice()
        stop_price = self.stopPrice()
        if stop_price is None:
            return None

        if self.type == Trade.Type.LONG:
            stop_range = Range(stop_price, open_price)
        else:
            stop_range = Range(open_price, stop_price)

        percent = stop_range.percent()
        return percent

    # }}}
    def takePercent(self) -> float | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.takePercent()")

        open_price = self.openPrice()
        take_price = self.takePrice()
        if take_price is None:
            return None

        if self.type == Trade.Type.LONG:
            take_range = Range(open_price, take_price)
        else:
            take_range = Range(take_price, open_price)

        percent = take_range.percent()
        return percent

    # }}}
    def result(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.result()")
        assert self.status == Trade.Status.CLOSED

        result = self.sellAmount() - self.buyAmount() - self.commission()
        return round(result, 2)

    # }}}
    def holdingDays(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.holdingDays()")

        opn_dt = self.operations[0].dt
        cls_dt = self.operations[-1].dt
        holding = cls_dt - opn_dt + ONE_DAY
        return holding.days

    # }}}
    def percent(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.percent()")
        assert self.status == Trade.Status.CLOSED

        persent = self.result() / self.buyAmount() * 100
        return round(persent, 2)

    # }}}
    def percentPerDay(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.percentPerDay()")
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

        # request instrument
        instrument = await Instrument.fromFigi(record["figi"])

        # create trade
        trade = Trade(
            dt=record["dt"],
            strategy=record["strategy"],
            version=record["version"],
            trade_type=Trade.Type.fromStr(record["trade_type"]),
            instrument=instrument,
            status=Trade.Status.fromStr(record["status"]),
            trade_id=Id.fromStr(record["trade_id"]),
            trade_list_name=record["trade_list"],
            orders=orders,
            operations=operations,
        )

        # create info
        trade.info = Cmd.fromJson(record["trade_info"], Trade.decoderJson)

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

    @staticmethod  # encoderJson# {{{
    def encoderJson(obj) -> Any:
        if isinstance(obj, (DateTime, Date)):
            return obj.isoformat()

    # }}}
    @staticmethod  # decoderJson# {{{
    def decoderJson(obj) -> Any:
        for k, v in obj.items():
            if isinstance(v, str) and "+00:00" in v:
                obj[k] = DateTime.fromisoformat(obj[k])
        return obj

    # }}}

    async def __connectOrderSignals(self, order: Order):  # {{{
        logger.debug(
            f"{self.__class__.__name__}.__connectOrderSignals('{order}')"
        )

        order.posted.aconnect(self.onOrderPosted)
        order.executed.aconnect(self.onOrderExecuted)

    # }}}


# }}}
class TradeList:  # {{{
    def __init__(  # {{{
        self,
        name: str,
        trades: Optional[list] = None,
        parent: Optional[TradeList] = None,
        subname: str = "",
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__name = name
        self.__trades = trades if trades else list()
        self.__parent_list = parent
        self.__subname = subname
        self.__childs: list[TradeList] = list()
        self.__asset = parent.asset if parent else None

        self.__owner: Optional[Any] = None  # Test | Trader

    # }}}
    def __str__(self):  # {{{
        return f"TradeList={self.__name}"

    # }}}
    def __getitem__(self, index: int) -> Trade:  # {{{
        assert index < len(self.__trades)
        return self.__trades[index]

    # }}}
    def __iter__(self):  # {{{
        return iter(self.__trades)

    # }}}
    def __len__(self) -> int:  # {{{
        return len(self.__trades)

    # }}}

    @property  # name  # {{{
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name: str):
        self.__name = new_name

    # }}}
    @property  # subname  # {{{
    def subname(self):
        return self.__subname

    # }}}
    @property  # trades  # {{{
    def trades(self):
        return self.__trades

    # }}}
    @property  # childs  # {{{
    def childs(self) -> list[TradeList]:
        return self.__childs

    # }}}
    @property  # asset  # {{{
    def asset(self):
        return self.__asset

    # }}}
    @property  # parent_list  # {{{
    def parent_list(self) -> TradeList | None:
        """Return parent trade list"""
        return self.__parent_list

    # }}}
    @property  # owner  # {{{
    def owner(self) -> Test | Trader | None:
        return self.__owner

    # }}}

    def add(self, trade: Trade) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")

        trade.trade_list_name = self.name
        self.__trades.append(trade)

    # }}}
    def remove(self, trade: Trade) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove()")

        trade.trade_list_name = ""
        self.__trades.remove(trade)

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")

        self.__trades.clear()

        # XXX:
        # тут глобально надо определить политику как взаимодействуют
        # и синхронизуется между собой рантайм и база данных.
        # И тут два варианта я вижу
        # 1. всегда синхронизовать - изменил объект и сразу пишем это
        #    изменение в бд.
        #    Минус - долго
        #    Плюс - всегда синхронизировано
        # 2. Записывать в бд только явно вызовом метода .save .update
        #    Минус - надо тщательно думать, чтобы не получить рассинхрон.
        #    Плюс - быстрее, и явно видно где синхронизация
        # Пока у меня тут каша. Часть методов, типо setStatus -
        # сразу пишут и в бд. А чать методов меняет только ран тайм.
        # это поведение нужно переделать. Выбрать одно и везде делать
        # только так.
        # Второе решение кажется мне более простым и понятным.
        # Как раньше было когда все в файлах хранилось.
        # Вот и думать о БД просто как о месте сохранения на диск.
        # Интерфейс объектов все равно я сохранил как был .save .load
        # а то что там внутри происходит теперь запись в БД это уже
        # низкоуровневая не важная информация.

    # }}}
    def find(self, trade_id: Id) -> Trade | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.find()")

        for trade in self.__trades:
            if trade.trade_id == trade_id:
                return trade
        return None

    # }}}
    def setOwner(self, owner: Test | Trader):  # {{{
        logger.debug(f"{self.__class__.__name__}.setOwner()")

        self.__owner = owner

    # }}}

    def createChild(self, trades: list[Trade], subname: str):  # {{{
        logger.debug(f"{self.__class__.__name__}.createChild()")

        child = TradeList(
            name=self.name,
            trades=trades,
            parent=self,
            subname=subname,
        )

        child.__asset = self.__asset
        child.__owner = self.__owner
        self.__childs.append(child)

        return child

    # }}}
    def removeChild(self, child: TradeList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeChild()")

        try:
            self.__childs.remove(child)
        except ValueError:
            logger.warning(f"{child} not in {self}")

    # }}}
    def clearChilds(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearChilds()")

        self.__childs.clear()

    # }}}

    async def selectFilter(self, f) -> TradeList:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectFilter()")

        selected = list()
        for trade in self.__trades:
            result = await f.acheck(trade)
            if result:
                selected.append(trade)

        child = self.createChild(selected, f.full_name)
        return child

    # }}}
    async def selectFilterList(self, filter_list) -> TradeList:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectFilterList()")

        child = self.createChild(self.__trades, filter_list.full_name)

        for f in filter_list:
            await child.selectFilter(f)

        return child

    # }}}
    async def anyOfFilterList(self, filter_list) -> TradeList:  # {{{
        logger.debug(f"{self.__class__.__name__}.anyOfFilterList()")

        selected = list()
        for trade in self:
            for f in filter_list:
                result = await f.acheck(trade)
                if result:
                    selected.append(trade)
                    break

        child = self.createChild(selected, f"{filter_list.full_name}")
        return child

    # }}}
    async def cascadeFilterList(self, filter_list) -> TradeList:  # {{{
        # здесь берутся фильтры верхнего уровня в фильтр листе
        # и применяются, но применяются каскадно!
        assert False, "TODO: me"

    # }}}
    async def deepFilterList(self, filter_list) -> TradeList:  # {{{
        logger.debug(f"{self.__class__.__name__}.deepFilterList()")

        # здесь бурутся все дочерние фильтр листы, и применяются
        # методом anyOfFilterList, но применяются каскадно!
        current = self
        for child_filter_list in filter_list:
            await self.deepFilterList(child_filter_list)

            if len(child_filter_list) > 0:
                child = await current.anyOfFilterList(child_filter_list)

    # }}}

    def selectStatus(self, status: Trade.Status) -> TradeList:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectStatus()")

        selected = list()
        for trade in self.__trades:
            if trade.status == status:
                selected.append(trade)

        child = self.createChild(selected, status.name)
        return child

    # }}}
    def selectStrategy(self, name: str, version: str) -> TradeList:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectStrategy()")

        selected = list()
        for trade in self.__trades:
            if trade.strategy == name and trade.version == version:
                selected.append(trade)

        child = self.createChild(selected, f"{name}-{version}")
        return child

    # }}}
    def selectStrategys(self) -> list[TradeList]:  # {{{
        logger.debug(f"{self.__class__.__name__}.collectStrategyList()")

        # all_strategys = {
        #     "strategy_name_1": ["v1", "v2", ...]
        #     "strategy_name_2": ["v1", "v2", ...]
        #     }
        all_strategys: dict[str, list[str]] = dict()
        for trade in self.__trades:
            name = trade.strategy
            version = trade.version

            if name not in all_strategys:
                all_strategys[name] = list()

            if version not in all_strategys[name]:
                all_strategys[name].append(version)

        all_childs = list()
        for name, versions in all_strategys.items():
            for ver in versions:
                child = self.selectStrategy(name, ver)
                all_childs.append(child)

        return all_childs

    # }}}
    def selectLong(self) -> TradeList:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectLong()")

        selected = list()
        for trade in self.__trades:
            if trade.isLong():
                selected.append(trade)

        child = self.createChild(selected, "long")
        return child

    # }}}
    def selectShort(self) -> TradeList:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectShort()")

        selected = list()
        for trade in self.__trades:
            if trade.isShort():
                selected.append(trade)

        child = self.createChild(selected, "short")
        return child

    # }}}
    def selectWin(self) -> TradeList:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectWin()")

        selected = list()
        for trade in self.__trades:
            if trade.status != Trade.Status.CLOSED:  # skip not closed
                continue
            if trade.isWin():
                selected.append(trade)

        child = self.createChild(selected, "win")
        return child

    # }}}
    def selectLoss(self) -> TradeList:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectLoss()")

        selected = list()
        for trade in self.__trades:
            if trade.status != Trade.Status.CLOSED:  # skip not closed
                continue
            if trade.isLoss():
                selected.append(trade)

        child = self.createChild(selected, "loss")
        return child

    # }}}
    def selectAsset(self, asset: Asset) -> TradeList:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectAsset()")

        selected = list()
        for trade in self.__trades:
            if trade.instrument.figi == asset.figi:
                selected.append(trade)

        child = self.createChild(selected, asset.ticker)
        child.__asset = asset
        return child

    # }}}
    def selectAssets(self) -> list[TradeList]:  # {{{
        logger.debug(f"{self.__class__.__name__}.collectAssetList()")

        asset_list = AssetList(name="")
        for i in self.__trades:
            instrument = i.instrument
            asset = Asset.fromInstrument(instrument)
            if asset not in asset_list:
                asset_list.add(asset)

        all_childs = list()
        for asset in asset_list:
            child = self.selectAsset(asset)
            all_childs.append(child)

        return all_childs

    # }}}
    def selectYear(self, year):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectYear()")

        selected = list()
        for trade in self.__trades:
            if trade.dt.year == year:
                selected.append(trade)

        child = self.createChild(selected, str(year))
        return child

    # }}}

    @classmethod  # fromRecord  # {{{
    async def fromRecord(cls, name, records: asyncpg.Record):
        logger.debug(f"{cls.__name__}.fromRecord()")

        tlist = TradeList(name)
        for i in records:
            trade = await Trade.fromRecord(i)
            tlist.add(trade)

        return tlist

    # }}}
    @classmethod  # save  # {{{
    async def save(cls, tlist) -> None:
        logger.debug(f"{cls.__name__}.save()")

        await cls.delete(tlist)
        await Keeper.add(tlist)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, name) -> TradeList | None:
        logger.debug(f"{cls.__name__}.load()")

        tlist = await Keeper.get(cls, name=name)
        return tlist

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, tlist):
        logger.debug(f"{cls.__name__}.delete()")

        await Keeper.delete(tlist)

    # }}}
    @classmethod  # deleteTrades  # {{{
    async def deleteTrades(cls, trade_list: TradeList):
        logger.debug(f"{cls.__name__}.deleteTrades()")

        await Keeper.delete(trade_list, only_trades=True)

    # }}}

    async def __deepFilterList(trade_list, filter_list):  # {{{
        for child_filter_list in filter_list:
            await self.__deepFilterList(child_filter_list)

    # }}}


# }}}


if __name__ == "__main__":
    ...
