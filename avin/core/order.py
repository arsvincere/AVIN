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

from avin.core.id import Id
from avin.utils import Signal


class Order(metaclass=abc.ABCMeta):  # {{{
    """doc# {{{
    This class is used only as a namespace

    To get syntax like Order.Market, Order.Limit, Order.StopLoss
    I think it looks better than MarketOrder, LimitOrder, StopLossOrder...

    In addition, this simplifies imports, it is enough to import one
    class Order for get access to all order types.
    """

    # }}}
    @abc.abstractmethod  # __init__# {{{
    def __init__(self): ...

    # }}}
    class Type(enum.Enum):  # {{{
        UNDEFINE = 0
        MARKET = 1
        LIMIT = 2
        STOP = 3
        WAIT = 4
        TRAILING = 5
        STOP_LOSS = 6
        TAKE_PROFIT = 7

    # }}}
    class Status(enum.Enum):  # {{{
        UNDEFINE = 0
        NEW = 1
        POST = 2
        PARTIAL = 5  # частично исполнен
        EXECUTED = 6  # исполнен

        # TEST: тест можно ли выставить на тинькоф ордер
        # с тем же ключом идемпотентности после того как ордер
        # отменен на вечерку / ночь / выходные

        OFF = 7  # для убранных на вечерку или выходные стопы

        CANCEL = 8  # отменен
        REJECT = 9  # отклонен брокером
        WAIT = 10  # ожидает выполнения условий для выставления

        @classmethod  # fromStr
        def fromStr(cls, string: str) -> Order.Status:
            statuses = {
                "NEW": Order.Status.NEW,
                "POST": Order.Status.POST,
                "PARTIAL": Order.Status.PARTIAL,
                "EXECUTED": Order.Status.EXECUTED,
                "OFF": Order.Status.OFF,
                "CANCEL": Order.Status.CANCEL,
                "REJECT": Order.Status.REJECT,
                "WAIT": Order.Status.WAIT,
            }
            return statuses[string]

    # }}}
    class Direction(enum.Enum):  # {{{
        UNDEFINE = 0
        BUY = 1
        SELL = 2

        @classmethod  # fromStr
        def fromStr(cls, string: str) -> Order.Direction:
            directions = {
                "BUY": Order.Direction.BUY,
                "SELL": Order.Direction.SELL,
            }
            return directions[string]

    # }}}

    class _BaseOrder(metaclass=abc.ABCMeta):  # {{{
        @abc.abstractmethod  # __init__# {{{
        def __init__(
            self,
            direction,
            figi,
            lots,
            quantity,
            account_name,
            status,
            order_id,
            trade_id,
            meta,
        ):
            self.direction = direction
            self.figi = figi
            self.lots = lots
            self.quantity = quantity

            self.account_name = account_name
            self.status = status if status else Order.Status.NEW
            self.order_id = order_id if order_id else Id.newId(self)
            self.trade_id = trade_id
            self.meta = meta

            # Signals
            self.posted = Signal(Order._BaseOrder)
            self.changed = Signal(Order._BaseOrder)
            self.partial = Signal(Order._BaseOrder, list)
            self.fulfilled = Signal(Order._BaseOrder, list)
            self.canceled = Signal(Order._BaseOrder)
            self.reqected = Signal(Order._BaseOrder)

        # }}}
        def __str__(self):  # {{{
            string = (
                f"Order.{self.type.name} "
                f"{self.direction.name} "
                f"{self.asset.ticker} "
                f"{self.lots} lot"
            )

            if self.type == Order.Type.MARKET:
                pass
            elif self.type == Order.Type.LIMIT:
                string += f", {self.quantity}x{self.price}"
            elif self.type == Order.Type.STOP:
                string += f", stop={self.stop_price}, exec={self.exec_price}"

            return string

        # }}}
        @classmethod  # save{{{
        def save(cls, order) -> bool:
            assert False, "не написана функция"

            # записываем в базу данных через кипера.

        # }}}
        @classmethod  # load{{{
        def load(cls, ID: Id):
            assert False, "не написана функция"
            # подумать ордер от сюда отправляет свой запрос?
            # или запрос к киперу идет только по части трейда?
            # а там дальше внутри загрузки трейда грузить все
            # его ордера??? Странная хуйня а если я просто
            # хочу посмотреть все активные ордера?
            # мне нужно сделать селект по статусу, а потом
            # загрузить каждый такой ордер из таблицы
            #
            # ордер  ордер ордер..
            # если кипер будет ковырять и создавать ордер внутри себя?
            # то при изменении ордера ковырять кипера тоже
            #
            # а если ордер будет ковыряться в бд строке сам?
            # то при изменении класса надо будет поменять только метод
            # Order.fromRecord(record)
            #
            # киперу просто кидают объекты и он их сохраняет правильно.
            # если меняется класс то придется менять и БД
            # если меняется БД меняется только кипер. ОК
            #
            # как киперу загружать объекты и выдавать списки объектов
            # по запросу? Выдавать ему сами объекты? Да.
            # Однозначно сами объекты а не записи из БД
            #
            # Кто где как собирает объект из записи в БД?
            # варианты
            # сам объект - он лучше всего себя знает.
            # и может удобно все разложить по полочкам.
            # но объект не должен ничего знать про БД...
            # с БД должен общаться только кипер.
            # У кипера тогда будет много методов... Да не так
            # уж и много...
            # Просто для каждого объекта у кипера есть метод
            # для записи его к БД и для создания его из БД

        # }}}

    # }}}
    class Market(_BaseOrder):  # {{{
        def __init__(
            self,
            direction: Order.Direction,
            figi: str,
            lots: int,
            quantity: int,
            account_name: str = None,
            status: Order.Status = None,
            order_id: Id = None,
            trade_id: Id = None,
            meta=None,
        ):
            super().__init__(
                direction,
                figi,
                lots,
                quantity,
                account_name,
                status,
                order_id,
                trade_id,
                meta=None,
            )
            self.type = Order.Type.MARKET

    # }}}
    class Limit(_BaseOrder):  # {{{
        def __init__(
            self,
            direction: Order.Direction,
            figi: str,
            lots: int,
            quantity: int,
            price: float,
            account_name: str = None,
            status: Order.Status = None,
            order_id: Id = None,
            trade_id: Id = None,
            meta=None,
        ):
            super().__init__(
                direction,
                figi,
                lots,
                quantity,
                account_name,
                status,
                order_id,
                trade_id,
                meta=None,
            )
            self.type = Order.Type.LIMIT
            self.price = price

    # }}}
    class Stop(_BaseOrder):  # {{{
        def __init__(
            self,
            direction: Order.Direction,
            figi: str,
            lots: int,
            quantity: int,
            stop_price: float,
            exec_price: float,
            account_name: str = None,
            status: Order.Status = None,
            order_id: Id = None,
            trade_id: Id = None,
            meta=None,
        ):
            super().__init__(
                direction,
                asset,
                lots,
                quantity,
                account_name,
                status,
                order_id,
                trade_id,
                meta=None,
            )
            self.type = Order.Type.STOP
            self.stop_price = stop_price
            self.exec_price = exec_price

    # }}}
    class StopLoss(_BaseOrder):  # {{{
        def __init__(
            self,
            position: Position,  # ??? XXX: подумай еще раз
            stop_price: float,
            exec_price: float,
            trade_id: Id = None,
            status: Order.Status = None,
        ):
            assert False

    # }}}
    class TakeProfit(_BaseOrder):  # {{{
        def __init__(
            self,
            position: Position,  # ??? XXX: подумай еще раз
            stop_price: float,
            exec_price: float,
            trade_id: Id = None,
            status: Order.Status = None,
        ):
            assert False

    # }}}
    class Wait(_BaseOrder):  # {{{
        ...

    # }}}
    class Trailing(_BaseOrder):  # {{{
        ...

    # }}}

    @classmethod  # fromRecord{{{
    def fromRecord(cls, record):
        methods = {
            "MARKET": Order.__marketOrderFromRecord,
            "LIMIT": Order.__limitOrderFromRecord,
            "STOP": Order.__stopOrderFromRecord,
        }
        method = methods[record["type"]]
        return method(record)

    # }}}
    @classmethod  # __marketOrderFromRecord{{{
    def __marketOrderFromRecord(cls, record):
        order = Order.Market(
            direction=Order.Direction.fromStr(record["direction"]),
            figi=record["figi"],
            lots=record["lots"],
            quantity=record["quantity"],
            account_name=record["account"],
            status=Order.Status.fromStr(record["status"]),
            order_id=record["order_id"],
            trade_id=record["trade_id"],
            meta=None,
        )
        return order

    # }}}
    @classmethod  # __limitOrderFromRecord{{{
    def __limitOrderFromRecord(cls, record):
        order = Order.Limit(
            direction=Order.Direction.fromStr(record["direction"]),
            figi=record["figi"],
            lots=record["lots"],
            quantity=record["quantity"],
            price=record["price"],
            account_name=record["account"],
            status=Order.Status.fromStr(record["status"]),
            order_id=record["order_id"],
            trade_id=record["trade_id"],
            meta=None,
        )
        return order

    # }}}
    @classmethod  # __stopOrderFromRecord{{{
    def __stopOrderFromRecord(cls, record):
        order = Order.Stop(
            direction=Order.Direction.fromStr(record["direction"]),
            figi=record["figi"],
            lots=record["lots"],
            quantity=record["quantity"],
            stop_price=record["stop_price"],
            exec_price=record["exec_price"],
            account_name=record["account"],
            status=Order.Status.fromStr(record["status"]),
            order_id=record["order_id"],
            trade_id=record["trade_id"],
            meta=None,
        )
        return order


# }}}

# }}}
