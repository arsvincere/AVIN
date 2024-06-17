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

class Order(metaclass=abc.ABCMeta):# {{{
    """ doc# {{{
    This class is used only as a namespace

    To get syntax Order.Market, Order.Limit, Order.StopLoss
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
        FILL =        6  # исполнен
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

    class __Order(metaclass=abc.ABCMeta):# {{{
        @abc.abstractmethod  #__init__# {{{
        def __init__(self, parent, uid, status):
            if uid is None:
                self.uid = None  # TODO class Uid generate uid
            if status is None:
                self.status = Order.Status.NEW
            self.__parent = parent
        # }}}
        def parent(self):# {{{
            return self.__parent
        # }}}
        def setParent(self, parent):# {{{
            self.__parent = parent
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
    class Market(__Order):# {{{
        def __init__(
            self,
            direction: Order.Direction,
            asset: Asset,
            lots: int,
            parent: Signal | Position=None,
            uid: str=None,
            status: Order.Status=None,
            ):

            self.direction = direction
            self.asset = asset
            self.lots = lots
            self.type = Order.Type.MARKET
            super().__init__(parent, uid, status)
    # }}}
    class Limit(__Order):# {{{
        def __init__(
            self,
            direction: Order.Direction,
            asset: Asset,
            lots: int,
            price: float,
            parent: Signal | Position=None,
            uid: str=None,
            status: Order.Status=None,
            ):

            self.direction = direction
            self.asset = asset
            self.lots = lots
            self.price = price
            self.type = Order.Type.LIMIT
            super().__init__(parent, uid, status)
    # }}}
    class Stop(__Order):# {{{
        def __init__(
            self,
            direction: Order.Direction,
            asset: Asset,
            lots: int,
            stop_price: float,
            exec_price: float,
            parent: Signal | Position=None,
            uid: str=None,
            status: Order.Status=None,
            ):

            self.direction = direction
            self.asset = asset
            self.lots = lots
            self.stop_price = stop_price
            self.exec_price = exec_price
            self.type = Order.Type.STOP
            super().__init__(parent, uid, status)
    # }}}
    class StopLoss(__Order):# {{{
        def __init__(
            self,
            position: Position,
            stop_price: float,
            exec_price: float,
            uid: str=None,
            status: Order.Status=None,
            ):

            self.position = position
            self.stop_price = stop_price
            self.exec_price = exec_price
            self.type = Order.Type.STOP_LOSS
            super().__init__(position, uid, status)
    # }}}
    class TakeProfit(__Order):# {{{
        def __init__(
            self,
            position: Position,
            stop_price: float,
            exec_price: float,
            uid: str=None,
            status: Order.Status=None,
            ):

            self.position = position
            self.stop_price = stop_price
            self.exec_price = exec_price
            self.type = Order.Type.TAKE_PROFIT
            super().__init__(position, uid, status)
    # }}}
    class Wait(__Order):# {{{
        ...
    # }}}
    class Trailing(__Order):# {{{
        ...
    # }}}
# }}}

if __name__ == "avin.logger":
    configure(logger)
