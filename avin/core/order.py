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


class Order(metaclass=abc.ABCMeta):
    Market = None
    Limit = None
    Stop = None
    Wait = None
    Trailing = None
    StopLoss = None
    TakeProfit = None


    class Status(enum.Enum):# {{{
        UNDEFINE =    0
        NEW =         1
        POST =        2
        PARTIAL =     5  # частично исполнен
        FILL =        6  # исполнен
        OFF =         7  # для убранных на вечерку или выходные стопы
        CANCEL =      8  # отменен
        REJECT =      9  # отклонен брокером
    # }}}

    class Direction(enum.Enum):# {{{
        UNDEFINE =    0
        BUY =         1
        SELL =        2
    # }}}


    @abc.abstractmethod  #__init__# {{{
    def __init__(self, signal, direction, asset, lots, uid, status):
        self.signal = signal
        self.direction = direction
        self.asset = asset
        self.lots = lots
        self.uid = uid
        self.status = status

        # self.__delattr__("Market")
        # self.__delattr__("Limit")
        # self.__delattr__("Stop")
        # self.__delattr__("Wait")
        # self.__delattr__("Trailing")
        # self.__delattr__("StopLoss")
        # self.__delattr__("TakeProfit")

        # if self.ID is None:
        #     self.ID = uuid.uuid4().hex
    # }}}

#     signal: object
#     direction: Direction
#     asset: Asset
#     lots: int
#     ID: str=None
#     status: Status=Status.NEW

class _Market(Order):
    def __init__(self, signal, direction, asset, lots, uid, status):
        self.type = "Market"
        Order.__init__(self, signal, direction, asset, lots, uid, status)

class _Limit(Order):
    ...
    price: float

class _Stop(Order):
    ...
    stop_price: float
    exec_price: float=None

class _Wait(Order):# {{{
    """ это теперь свойства его будут а не в одной куче с остальными
    ордерами """
    WAIT =        3  # ожидающий внутри системы, не выставлен у брокера
    TIMEOUT =     4  # задержка перед срабатыванием
# }}}
class _Trailing(Order): ...
class _StopLoss(Order): ...
class _TakeProfit(Order): ...


Order.Market = _Market
Order.Limit = _Limit
Order.Stop = _Stop
Order.Wait = _Wait
Order.Trailing = _Trailing
Order.StopLoss = _StopLoss
Order.TakeProfit = _Market

# class Order():
#
#     @staticmethod  # toJSON{{{
#     def toJSON(order) -> dict:
#         assert False, "не написана функция"
#         obj = {
#             "signal":   "ID сохранить?"
#             "type":     str(order.type),
#             "direction":str(order.direction),
#             "asset":    Asset.toJSON(order.asset),
#             "lots":     order.lots,
#             "price":    order.price,
#             "status":   str(order.status),
#             }
#         return obj
#     # }}}
#     @staticmethod  # fromJSON{{{
#     def fromJSON(obj):
#         assert False, "не написана функция"
#         asset = ...
#         ID = Asset.fromJSON(obj["asset"])
#         assert ID.type == Type.SHARE
#         share = Share(ID.ticker)
#         o = Order(
#             signal=     "???????????????????????",
#             type=       eval(obj["type"]),
#             direction=  eval(obj["direction"]),
#             asset=      share,
#             lots=       obj["lots"],
#             price=      obj["price"],
#             status=     eval(obj["status"]),
#             ID=         obj["ID"],
#             )
#         return o
#     # }}}
#     def parent(self):# {{{
#         return self.signal
#     # }}}
