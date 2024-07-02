#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations
import enum
from avin.const import ONE_DAY
from avin.core.operation import Operation

class Position():# {{{
    class Status(enum.Enum):# {{{
        UNDEFINE =     0
        OPEN =         1
        CLOSE =        2
    # }}}
    def __init__(self, operations: list[Operation], meta: object):# {{{
        self.__operations = operations
        self.__status = Position.Status.OPEN
        self.__meta = meta
    # }}}
    def __str__(self):# {{{
        s = (
            f"Position[{self.status}] {self.asset.ticker} "
            f"{self.quantity()}x{self.average()} = {self.amount()}"
            )
        return s
    # }}}
    @property  #asset# {{{
    def asset(self):
        return self.__operations[0].asset
    # }}}
    @property  #status# {{{
    def status(self):
        return self.__status
    # }}}
    @property  #operations# {{{
    def operations(self):
        return self.__operations
    # }}}
    def add(self, operation):# {{{
        assert self.__status == Position.Status.OPEN
        self.__operations.append(operation)
        # Проверим не закрылась ли позиция
        if self.quantity() == 0:
            self.__status = Position.Status.CLOSE
            self.__writePositionInfo()
            self.__writeOperationsInfo()
    # }}}
    def openPrice(self):# {{{
        return self.__operations[0].price
    # }}}
    def closePrice(self):# {{{
        assert self.__status == Position.Status.CLOSE
        return self.__operations[-1].price
    # }}}
    def openDatetime(self):# {{{
        return self.operations[0].dt
    # }}}
    def closeDatetime(self):# {{{
        assert self.__status == Position.Status.CLOSE
        return self.operations[-1].dt
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
    def result(self):# {{{
        if self.__status != self.Status.CLOSE:
            assert False, "Вызов результата для незакрытой позиции"
        result = (
            self.sellAmount() -
            self.buyAmount() - self.buyCommission() - self.sellCommission()
            )
        return round(result, 2)
    # }}}
    def holdingDays(self):# {{{
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
