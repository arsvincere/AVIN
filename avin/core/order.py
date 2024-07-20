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
from avin.core.gid import GId
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
        def __init__(
            self,
            direction,
            asset,
            lots,
            quantity,
            order_ID,
            trade_ID,
            status,
            account,
            ):

            self.direction = direction
            self.asset = asset
            self.lots = lots
            self.quantity = quantity

            self.ID = order_ID if order_ID else GId.newGId(self)
            self.trade_ID = trade_ID
            self.status = status if status else Order.Status.NEW
            self.account = account

            # Signals
            self.posted = Signal(Order._BaseOrder)
            self.changed = Signal(Order._BaseOrder)
            self.partial = Signal(Order._BaseOrder, list)
            self.fulfilled = Signal(Order._BaseOrder, list)
            self.canceled = Signal(Order._BaseOrder)
            self.reqected = Signal(Order._BaseOrder)
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
            quantity:   int,
            order_ID:   GId=None,
            trade_ID:   GId=None,
            status:     Order.Status=None,
            account:    Account=None,
            ):

            super().__init__(
                direction,
                asset,
                lots,
                quantity,
                order_ID,
                trade_ID,
                status,
                account,
                )
            self.type = Order.Type.MARKET
    # }}}
    class Limit(_BaseOrder):# {{{
        def __init__(
            direction:  Order.Direction,
            asset:      Asset,
            lots:       int,
            quantity:   int,
            price:      float,
            order_ID:   GId=None,
            trade_ID:   GId=None,
            status:     Order.Status=None,
            account:    Account=None,
            ):

            super().__init__(
                direction,
                asset,
                lots,
                quantity,
                order_ID,
                trade_ID,
                status,
                account,
                )
            self.type = Order.Type.LIMIT
            self.price = price
    # }}}
    class Stop(_BaseOrder):# {{{
        def __init__(
            self,
            direction:  Order.Direction,
            asset:      Asset,
            lots:       int,
            quantity:   int,
            stop_price: float,
            exec_price: float,
            order_ID:   GId=None,
            trade_ID:   GId=None,
            status:     Order.Status=None,
            account:    Account=None,
            ):

            super().__init__(
                direction,
                asset,
                lots,
                quantity,
                order_ID,
                trade_ID,
                status,
                account,
                )
            self.type = Order.Type.STOP
            self.stop_price = stop_price
            self.exec_price = exec_price
    # }}}
    class StopLoss(_BaseOrder):# {{{
        def __init__(
            self,
            position: Position,  # ??? NOTE подумай еще раз
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
            position: Position,  # ??? NOTE подумай еще раз
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
