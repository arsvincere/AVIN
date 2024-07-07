#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations
import abc
import enum
from dataclasses import dataclass
from avin.core.asset import Asset
from avin.core.operation import Operation
from avin.utils import Signal

class Order(metaclass=abc.ABCMeta):# {{{
    """ doc# {{{
    This class is used only as a namespace

    To get syntax like Order.Market, Order.Limit, Order.StopLoss
    I think it looks better than MarketOrder, LimitOrder, StopLossOrder...

    In addition, this simplifies imports, it is enough to import one
    class Order for get access to all order types.
    """
    # }}}
    @abc.abstractmethod  #__init__# {{{
    def __init__(self):
        ...
    # }}}
    class Type(enum.Enum):# {{{
        UNDEFINE =    0
        MARKET =      1
        LIMIT =       2
        STOP =        3
        WAIT =        4
        TRAILING =    5
        STOP_LOSS =   6
        TAKE_PROFIT = 7
    # }}}
    class Status(enum.Enum):# {{{
        UNDEFINE =    0
        NEW =         1
        POST =        2
        PARTIAL =     5  # частично исполнен
        EXECUTED =    6  # исполнен
        OFF =         7  # для убранных на вечерку или выходные стопы
        CANCEL =      8  # отменен
        REJECT =      9  # отклонен брокером
        WAIT =        10 # ожидает выполнения условий для выставления
    # }}}
    class Direction(enum.Enum):# {{{
        UNDEFINE =    0
        BUY =         1
        SELL =        2
    # }}}

    class _BaseOrder(metaclass=abc.ABCMeta):# {{{
        @abc.abstractmethod  #__init__# {{{
        def __init__(self):
            # Signals
            self.posted = Signal(object)
            self.changed = Signal(object)
            self.partial = Signal(object, list[Operation])
            self.fulfilled = Signal(object, list[Operation])
            self.canceled = Signal(object)
        # }}}
        @classmethod  # toJson{{{
        def toJson(cls, order) -> dict:
            assert False, "не написана функция"
        # }}}
        @classmethod  # fromJson{{{
        def fromJson(cls, obj):
            assert False
        # }}}
    # }}}
    class Market(_BaseOrder):# {{{
        def __init__(
            self,
            direction:  Order.Direction,
            asset:      Asset,
            lots:       int,
            trade_ID:   GId=None,
            status:     Order.Status=None,
            ):

            super().__init__()
            self.direction = direction
            self.asset = asset
            self.lots = lots
            self.trade_ID = trade_ID
            self.type = Order.Type.MARKET
            self.status = status if status is not None else Order.Status.NEW

        def __str__(self):
            string = (
                f"{self.type.name} "
                f"{self.direction.name} "
                f"{self.asset.ticker} "
                f"{self.lots} x 'market_price'"
                )
            return string
    # }}}
    class Limit(_BaseOrder):# {{{
        def __init__(
            self,
            direction: Order.Direction,
            asset: Asset,
            lots: int,
            price: float,
            trade_ID: GId=None,
            status: Order.Status=None,
            ):

            super().__init__()
            self.direction = direction
            self.asset = asset
            self.lots = lots
            self.price = price
            self.trade_ID = trade_ID
            self.status = status if status is not None else Order.Status.NEW
            self.type = Order.Type.LIMIT
    # }}}
    class Stop(_BaseOrder):# {{{
        def __init__(
            self,
            direction: Order.Direction,
            asset: Asset,
            lots: int,
            stop_price: float,
            exec_price: float,
            trade_ID: GId=None,
            status: Order.Status=None,
            ):

            super().__init__()
            self.direction = direction
            self.asset = asset
            self.lots = lots
            self.stop_price = stop_price
            self.exec_price = exec_price
            self.trade_ID = trade_ID
            self.status = status if status is not None else Order.Status.NEW
            self.type = Order.Type.STOP
    # }}}
    class StopLoss(_BaseOrder):# {{{
        def __init__(
            self,
            position: Position,
            stop_price: float,
            exec_price: float,
            trade_ID: GId=None,
            status: Order.Status=None,
            ):

            super().__init__()
            self.position = position
            self.stop_price = stop_price
            self.exec_price = exec_price
            self.position = position
            self.trade_ID = trade_ID
            self.status = status if status is not None else Order.Status.NEW
            self.type = Order.Type.STOP_LOSS
    # }}}
    class TakeProfit(_BaseOrder):# {{{
        def __init__(
            self,
            position: Position,
            stop_price: float,
            exec_price: float,
            trade_ID: GId=None,
            status: Order.Status=None,
            ):

            super().__init__()
            self.position = position
            self.stop_price = stop_price
            self.exec_price = exec_price
            self.position = position
            self.trade_ID = trade_ID
            self.status = status if status is not None else Order.Status.NEW
            self.type = Order.Type.TAKE_PROFIT
    # }}}
    class Wait(_BaseOrder):# {{{
        ...
    # }}}
    class Trailing(_BaseOrder):# {{{
        ...
    # }}}
# }}}

if __name__ == "avin.logger":
    configure(logger)
