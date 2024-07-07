#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations
import enum
from avin.core.gid import GId
from avin.core.order import Order
from avin.core.operation import Operation
from avin.core.position import Position
from avin.const import Usr
from avin.utils import Signal

class Position():# {{{
    def __str__(self):# {{{
        s = (
            f"Position[{self.status}] {self.asset.ticker} "
            f"{self.quantity()}x{self.average()} = {self.amount()}"
            )
        return s
    # }}}
    def __writePositionInfo(self):# {{{
        if self.status != self.Status.CLOSE:
            assert False, "Запись результатов для незакрытой позиции"
        info = dict()
        info["result"] = self.result()
        info["percent"] = self.percent()
        info["holding_days"] = self.holdingDays()
        info["percent_per_day"] = self.percentPerDay()
        info["buy_amount"] = self.buyAmount()
        info["sell_amount"] = self.sellAmount()
        info["commission"] = self.commission()
        info["open_datetime"] = self.openDatetime()
        info["open_price"] = self.openPrice()
        info["close_datetime"] = self.closeDatetime()
        info["close_price"] = self.closePrice()
        self.__signal.info.setdefault("position", info)
    # }}}
    def __writeOperationsInfo(self):# {{{
        assert False
        # сделать добавление через интерфейс трейда
        self.__signal.info.setdefault("operation", list())
        for op in self.operations:
            self.__signal.info["operation"].append(op)
    # }}}
# }}}
class Trade():# {{{
    class Type(enum.Enum):# {{{
        UNDEFINE =  0
        LONG =      1
        SHORT =     2
    # }}}
    class Status(enum.Enum):# {{{
        UNDEFINE = 0
        INITIAL =  1
        NEW =      2
        POST =     3
        OPEN =     4
        CLOSE =    5
        ARCHIVE =  7
        CANCELED = 8
    # }}}
    def __init__(# {{{
        self,
        dt:         datetime,
        strategy:   Strategy,
        trade_type: Type,
        asset:      Asset,
        status:     Trade.Status=None,
        ID:         GId=None,
        ):

        if status is None:
            status = Trade.Status.INITIAL
        if ID is None:
            ID = GId.newGId(self)

        self.__info = {
            "ID":               ID,
            "status":           status,
            "datetime":         dt,
            "strategy":         strategy.name,
            "version":          strategy.version,
            "type":             trade_type,
            "asset":            asset,
            "orders":           list(),
            "operations":       list(),

            "result":           None,
            "percent":          None,
            "holding_days":     None,
            "percentPerDay":    None,
            "buy_amount":       None,
            "sell_amount":      None,
            "commission":       None,
            "open_datetime":    None,
            "open_price":       None,
            "close_datetime":   None,
            "close_price":      None,
            "stop_price":       None,
            "take_price":       None,


            }
        self.__blocked = False
    # }}}
    def __str__(self):# {{{
        dt = self.dt + Usr.TIME_DIF
        dt = dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"=> Trade {dt} {self.strategy}-{self.version} "
            f"{self.asset.ticker} {self.type.name.lower()}"
            )
        return string
    # }}}
    @property  #ID# {{{
    def ID(self):
        return self.__info["ID"]
    # }}}
    @property  #status# {{{
    def status(self):
        return self.__info["status"]
    @status.setter
    def status(self, status):
        self.__info["status"] = status
    # }}}
    @property  #dt# {{{
    def dt(self):
        return self.__info["datetime"]
    # }}}
    @property  #strategy# {{{
    def strategy(self):
        return self.__info["strategy"]
    # }}}
    @property  #version# {{{
    def version(self):
        return self.__info["version"]
    # }}}
    @property  #type# {{{
    def type(self):
        return self.__info["type"]
    # }}}
    @property  #asset# {{{
    def asset(self):
        return self.__info["asset"]
    # }}}
    @property  #orders# {{{
    def orders(self):
        return self.__info["orders"]
    # }}}
    @property  #operations# {{{
    def operations(self):
        return self.__info["operations"]
    # }}}
    #@slot  #... # {{{
    def orderExecuted(self, order, operations):
        assert order.trade_ID == self.ID
        for op in operations:
            self.addOperation(op)
    # }}}
    def addOrder(self, order: Order):# {{{
        order.trade_ID = self.ID
        order.fulfilled.connect(self.orderExecuted)
        self.__info["orders"].append(order)
    # }}}
    def addOperation(self, operation: Operation):# {{{
        assert False, "TODO"
    # }}}
    def chart(self, timeframe: TimeFrame) -> Chart:# {{{
        assert self.asset.type == Type.SHARE
        end = self.dt
        begin = self.dt - Chart.DEFAULT_BARS_COUNT * timeframe
        chart = Chart(self.asset, timeframe, begin, end)
        return chart
    # }}}
    def isLong(self):# {{{
        return self._info["strategy"]["type"] == Signal.Type.LONG
    # }}}
    def isShort(self):# {{{
        return self._info["strategy"]["type"] == Signal.Type.SHORT
    # }}}
    def isWin(self):# {{{
        return self.result > 0
    # }}}
    def isLoss(self):# {{{
        return self.result <= 0
    # }}}
    def isBlocked(self):# {{{
        return self.__blocked
    # }}}
    def setBlocked(self, val: bool):# {{{
        self.__blocked = val
    # }}}
    def lots(self):# {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.BUY:
                total += op.lots
            elif op.direction == Operation.Direction.SELL:
                total -= op.lots
        return total
    # }}}
    def quantity(self):# {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.BUY:
                total += op.quantity
            elif op.direction == Operation.Direction.SELL:
                total -= op.quantity
        return total
    # }}}
    def buyQuantity(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.BUY:
                total += op.quantity
        return total
    # }}}
    def sellQuantity(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.SELL:
                total += op.quantity
        return total
    # }}}
    def amount(self):# {{{
        if self.__status == self.Status.CLOSE:
            return 0.0
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.BUY:
                total += op.amount
            elif op.direction == Operation.Direction.SELL:
                total -= op.amount
        return total
    # }}}
    def buyAmount(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.BUY:
                total += op.amount
        return total
    # }}}
    def sellAmount(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.SELL:
                total += op.amount
        return total
    # }}}
    def commission(self):# {{{
        return self.buyCommission() + self.sellCommission()
    # }}}
    def buyCommission(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.BUY:
                total += op.commission
        return total
    # }}}
    def sellCommission(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.SELL:
                total += op.commission
        return total
    # }}}
    def average(self):# {{{
        return self.amount() / self.quantity()
    # }}}
    def averageBuy(self):# {{{
        if self.buyQuantity() == 0:
            return 0.0
        else:
            return self.buyAmount() / self.buyQuantity()
    # }}}
    def averageSell(self):# {{{
        if self.sellQuantity() == 0:
            return 0.0
        else:
            return self.sellAmount() / self.sellQuantity()
    # }}}
    def open_dt(self):# {{{
        return self._info["open_datetime"]
    # }}}
    def open_price(self):# {{{
        # TODO: возвращать avg позиции
        return self.__info["open_price"]
    # }}}
    def close_dt(self):# {{{
        return self._info["close_datetime"]
    # }}}
    def close_price(self):# {{{
        # TODO: возвращать avg позиции
        return self.__info["close_price"]
    # }}}
    def stop_price(self):# {{{
        return self.__info["stop_price"]
    # }}}
    def take_price(self):# {{{
        return self.__info["take_price"]
    # }}}
    def result(self):# {{{
        if self.__status != self.Status.CLOSE:
            assert False, "Вызов результата для незакрытой позиции"
        result = (
            self.sellAmount() -
            self.buyAmount() - self.buyCommission() - self.sellCommission()
            )
        return round(result, 2)
    # }}}
    def result(self):# {{{
        result = self._info["result"]
        return round(result, 2)
    # }}}
    def holding(self):# {{{
        return self._info["holding_days"]
    # }}}
    def holdingDays(self):# {{{
        # TODO можно возвращать холдинг дейс и для открытой позиции
        # главное чтобы там хоть одна операция была
        if self.__status != self.Status.CLOSE:
            assert False, "Вызов времени удержания для незакрытой позиции"
        opn_dt = self.operations[0].dt
        cls_dt = self.operations[-1].dt
        holding = cls_dt - opn_dt + ONE_DAY
        return holding.days
    # }}}
    def percent(self):# {{{
        if self.__status != self.Status.CLOSE:
            assert False, "Вызов результата в процентах для незакрытой позиции"
        persent = self.result() / self.buyAmount() * 100
        return round(persent, 2)
    # }}}
    def percentPerDay(self):# {{{
        if self.__status != self.Status.CLOSE:
            assert False, "Вызов результата в процентах для незакрытой позиции"
        persent = self.result() / self.buyAmount() * 100
        holding = self.holdingDays()
        persent_per_day = persent / holding
        return round(persent_per_day, 2)
    # }}}
    def percent_per_day(self):# {{{
        assert False
        return self._info["percent_per_day"]
    # }}}
    @classmethod  #toJSON# {{{
    def toJSON(cls, trade):
        return trade._info
    # }}}
    @classmethod  #fromJSON# {{{
    def fromJSON(cls, obj):
        assert False
    # }}}
# }}}
class TradeList():# {{{
    def __init__(self, name: str="unnamed", trades=None, parent=None):# {{{
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
    def __iter__(self):# {{{
        return iter(self._trades)
    # }}}
    def _createChild(self, trades, suffix):# {{{
        child_name = f"- {suffix}"
        child = TradeList(
            name=child_name,
            trades=trades,
            parent=self
            )
        child._asset = self.asset
        self._childs.append(child)
        return child
    # }}}
    def _selectStrategy(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["strategy"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" strategy-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectAnalytic(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["analytic"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" analytic-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectMarket(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["market analytic"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" market-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectRisk(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["risk manager"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" risk-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectRuler(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["ruler"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" risk-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectAdviser(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["adviser"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" adviser-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectPosition(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["position"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" position-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    @staticmethod  #save# {{{
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
    @staticmethod  #load# {{{
    def load(file_path, parent=None):
        name = Cmd.name(file_path, extension=False)
        info_list = Cmd.loadJSON(file_path)
        tlist = TradeList(name, parent=parent)
        for info in info_list:
            trade = Trade(info, parent=tlist)
            tlist.add(trade)
        return tlist
    # }}}
    @staticmethod  #delete# {{{
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
    @property  #name# {{{
    def name(self):
        return self._name
    # }}}
    @property  #trades# {{{
    def trades(self):
        return self._trades
    # }}}
    @property  #count# {{{
    def count(self):
        return len(self._trades)
    # }}}
    @property  #asset# {{{
    def asset(self):
        return self._asset
    # }}}
    @property  #test# {{{
    def test(self):
        return self._test
    # }}}
    @property  #dir_path# {{{
    def dir_path(self):
        if self._test is not None:
            return self._test.dir_path
        else:
            assert False, "WTF???"
    # }}}
    @property  #path# {{{
    def path(self):
        path = Cmd.join(self.dir_path, "tlist.tl")
        return path
    # }}}
    def parent(self):# {{{
        return self._parent
    # }}}
    def add(self, trade: Trade) -> None:# {{{
        self._trades.append(trade)
        trade._parent = self
    # }}}
    def remove(self, trade: Trade) -> None:# {{{
        self._trades.remove(trade)
    # }}}
    def clear(self) -> None:# {{{
        self._trades.clear()
    # }}}
    def selectLong(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isLong():
                selected.append(trade)
        child = self._createChild(selected, "long")
        return child
    # }}}
    def selectShort(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isShort():
                selected.append(trade)
        child = self._createChild(selected, "short")
        return child
    # }}}
    def selectWin(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isWin():
                selected.append(trade)
        child = self._createChild(selected, "win")
        return child
    # }}}
    def selectLoss(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isLoss():
                selected.append(trade)
        child = self._createChild(selected, "loss")
        return child
    # }}}
    def selectBack(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isBack():
                selected.append(trade)
        child = self._createChild(selected, "back")
        return child
    # }}}
    def selectForward(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isForward():
                selected.append(trade)
        child = self._createChild(selected, "forward")
        return child
    # }}}
    def selectFilter(f):# {{{
        assert False
    # }}}
# }}}


