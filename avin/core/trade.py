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
from avin.core.id import Id
from avin.core.operation import Operation
from avin.core.order import Order
from avin.data import InstrumentId
from avin.keeper import Keeper


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
        EXPECTATION = 2
        MAKE_ORDER = 3

        TRIGGERED = 10
        POST_ORDER = 11
        POSTED = 13

        NEW = 20
        MAKE_STOP = 21
        MAKE_TAKE = 22
        POST_STOP = 23
        POST_TAKE = 24

        OPEN = 30

        OFF = 40

        FINISH = 50
        CLOSING = 51
        REMOVING = 52

        CLOSE = 60

        CANCELED = 90
        BLOKED = 91

        ARCHIVE = 100

        @classmethod  # fromStr
        def fromStr(cls, string: str) -> Trade.Type:
            statuses = {
                "INITIAL": Trade.Status.INITIAL,
                "EXPECTATION": Trade.Status.EXPECTATION,
                "MAKE_ORDER": Trade.Status.MAKE_ORDER,
                "TRIGGERED": Trade.Status.TRIGGERED,
                "POST_ORDER": Trade.Status.POST_ORDER,
                "POSTED": Trade.Status.POSTED,
                "NEW": Trade.Status.NEW,
                "MAKE_STOP": Trade.Status.MAKE_STOP,
                "MAKE_TAKE": Trade.Status.MAKE_TAKE,
                "STOP_STOP": Trade.Status.STOP_STOP,
                "STOP_TAKE": Trade.Status.STOP_TAKE,
                "OPEN": Trade.Status.OPEN,
                "OFF": Trade.Status.OFF,
                "FINISH": Trade.Status.FINISH,
                "CLOSING": Trade.Status.CLOSING,
                "REMOVING": Trade.Status.REMOVING,
                "CLOSE": Trade.Status.CLOSE,
                "CANCELED": Trade.Status.CANCELED,
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

    # }}}
    def __str__(self):  # {{{
        dt = self.dt + Usr.TIME_DIF
        dt = dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"=> Trade {dt} {self.strategy}-{self.version} "
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
    # @slot  #orderPosted # {{{
    def orderPosted(self, order):
        assert order.trade_id == self.trade_id
        if self.status == Trade.Status.INITIAL:
            self.status = Trade.Status.NEW

    # }}}
    # @slot  #orderFulfilled # {{{
    def orderFulfilled(self, order, operations: list[Operation]):
        assert order.trade_id == self.trade_id
        for op in operations:
            self.addOperation(op)

    # }}}
    async def setStatus(self, status: Trade.Status):  # {{{
        self.__info["status"] = status
        await Trade.update(self)

    # }}}
    async def addOrder(self, order: Order):  # {{{
        order.trade_id = self.trade_id
        order.posted.connect(self.orderPosted)
        order.fulfilled.connect(self.orderFulfilled)
        self.__info["orders"].append(order)
        await Order.save(order)

    # }}}
    async def addOperation(self, operation: Operation):  # {{{
        operation.trade_id = self.trade_id
        self.__info["operations"].append(operation)

        if self.lots() == 0:
            self.status = Trade.Status.CLOSE
        else:
            self.status = Trade.Status.OPEN

        await Operation.save(operation)
        await Trade.update(self)

    # }}}
    def chart(self, timeframe: TimeFrame) -> Chart:  # {{{
        assert self.asset.type == Type.SHARE
        end = self.dt
        begin = self.dt - Chart.DEFAULT_BARS_COUNT * timeframe
        chart = Chart(self.asset, timeframe, begin, end)
        return chart

    # }}}
    def isLong(self):  # {{{
        return self.__info["type"] == Trade.Type.LONG

    # }}}
    def isShort(self):  # {{{
        return self.__info["type"] == Trade.Type.SHORT

    # }}}
    def isWin(self):  # {{{
        assert self.status == Trade.Status.CLOSE
        return self.result > 0

    # }}}
    def isLoss(self):  # {{{
        assert self.status == Trade.Status.CLOSE
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
        if self.status == Trade.Status.CLOSE:
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
        assert self.status in (
            Trade.Status.OPEN,
            Trade.Status.CLOSE,
        )
        return self.__info["operations"][0].dt

    # }}}
    def openPrice(self):  # {{{
        assert self.status in (
            Trade.Status.OPEN,
            Trade.Status.CLOSE,
        )
        if self.isLong():
            return self.buyAverage()

        return self.sellAverage()

    # }}}
    def closeDatetime(self):  # {{{
        assert self.status == Trade.Status.CLOSE
        return self.__info["operations"][-1].dt

    # }}}
    def closePrice(self):  # {{{
        assert self.status == Trade.Status.CLOSE
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
        assert self.status == Trade.Status.CLOSE
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
        assert self.status == Trade.Status.CLOSE
        persent = self.result() / self.buyAmount() * 100
        return round(persent, 2)

    # }}}
    def percentPerDay(self):  # {{{
        assert self.status == Trade.Status.CLOSE
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
        t = Trade(
            dt=record["dt"],
            strategy=record["strategy"],
            version=record["version"],
            trade_type=Trade.Type.fromStr(record["type"]),
            asset_id=ID,
            status=Trade.Status.fromStr(record["status"]),
            trade_id=record["trade_id"],
            orders=orders,
            operations=operations,
        )
        return t

    # }}}
    @classmethod  # save  # {{{
    async def save(cls, trade: Trade) -> None:
        await Keeper.add(trade)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, trade_id: Id) -> Trade:
        trade_list = await Keeper.get(cls, trade_id=trade_id)
        assert len(trade_list) == 1
        return trade_list[0]

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, trade: Trade) -> None:
        await Keeper.delete(trade)

    # }}}
    @classmethod  # update  # {{{
    async def update(cls, trade: Trade) -> None:
        await Keeper.update(trade)

    # }}}


# }}}
class TradeList:  # {{{
    def __init__(  # {{{
        self, name: str = "unnamed", trades=None, parent=None
    ):
        self._name = name
        self._trades = trades if trades is not None else list()
        self._childs = list()
        self._asset = None
        self._parent = parent
        if isinstance(parent, Test):
            self._test = parent
        elif isinstance(parent, TradeList):
            self._asset = parent._asset
            self._test = parent._test

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
    def _selectStrategy(self, key, value):  # {{{
        selected = list()
        for trade in self._trades:
            x = trade["strategy"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" strategy-{key}-{value}",
            trades=selected,
            parent=self,
        )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist

    # }}}
    def _selectAnalytic(self, key, value):  # {{{
        selected = list()
        for trade in self._trades:
            x = trade["analytic"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" analytic-{key}-{value}",
            trades=selected,
            parent=self,
        )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist

    # }}}
    def _selectMarket(self, key, value):  # {{{
        selected = list()
        for trade in self._trades:
            x = trade["market analytic"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" market-{key}-{value}",
            trades=selected,
            parent=self,
        )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist

    # }}}
    def _selectRisk(self, key, value):  # {{{
        selected = list()
        for trade in self._trades:
            x = trade["risk manager"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" risk-{key}-{value}",
            trades=selected,
            parent=self,
        )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist

    # }}}
    def _selectRuler(self, key, value):  # {{{
        selected = list()
        for trade in self._trades:
            x = trade["ruler"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" risk-{key}-{value}",
            trades=selected,
            parent=self,
        )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist

    # }}}
    def _selectAdviser(self, key, value):  # {{{
        selected = list()
        for trade in self._trades:
            x = trade["adviser"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" adviser-{key}-{value}",
            trades=selected,
            parent=self,
        )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist

    # }}}
    def _selectPosition(self, key, value):  # {{{
        selected = list()
        for trade in self._trades:
            x = trade["position"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" position-{key}-{value}",
            trades=selected,
            parent=self,
        )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist

    # }}}
    @staticmethod  # save# {{{
    def save(trade_list, file_path=None):
        if file_path is None:
            file_path = trade_list.path  # default in parent dir
        obj = list()
        for trade in trade_list:
            trade_info_dict = Trade.toJSON(trade)
            obj.append(trade_info_dict)
        Cmd.saveJSON(obj, file_path)
        return True

    # }}}
    @staticmethod  # load# {{{
    def load(file_path, parent=None):
        name = Cmd.name(file_path, extension=False)
        info_list = Cmd.loadJSON(file_path)
        tlist = TradeList(name, parent=parent)
        for info in info_list:
            trade = Trade(info, parent=tlist)
            tlist.add(trade)
        return tlist

    # }}}
    @staticmethod  # delete# {{{
    def delete(tlist):
        path = tlist.path
        if not Cmd.isExist(path):
            # logger.warning(
            #     f"Can't delete TradeList: '{path}', file not found"
            #     )
            return False
        Cmd.delete(path)
        return True

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
    @property  # test# {{{
    def test(self):
        return self._test

    # }}}
    @property  # dir_path# {{{
    def dir_path(self):
        if self._test is not None:
            return self._test.dir_path
        else:
            assert False, "WTF???"

    # }}}
    @property  # path# {{{
    def path(self):
        path = Cmd.join(self.dir_path, "tlist.tl")
        return path

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
    def selectBack(self):  # {{{
        selected = list()
        for trade in self._trades:
            if trade.isBack():
                selected.append(trade)
        child = self._createChild(selected, "back")
        return child

    # }}}
    def selectForward(self):  # {{{
        selected = list()
        for trade in self._trades:
            if trade.isForward():
                selected.append(trade)
        child = self._createChild(selected, "forward")
        return child

    # }}}
    def selectFilter(f):  # {{{
        assert False

    # }}}


# }}}
