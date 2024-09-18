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
from typing import Optional

from avin.core.id import Id
from avin.core.operation import Operation
from avin.core.transaction import Transaction
from avin.data import InstrumentId
from avin.keeper import Keeper
from avin.utils import AsyncSignal, logger

# TODO: а может сюда транзакции подключить.

# TODO: стоп ордер.. POSTED... потом он срабатывает
# на стороне брокера то он все, считается исчезшим
# вместо него создает лимит ордер.
# надо мне тоже такую логику завести,
# возможно прямо вот так же: StopStatus...
# ---
# пока поменял статусы местами немного... пойдет для начала
# надо синхронизировать с БД только статусы
# а таймаут вообще пока выпилил, впизду когда понадобится
# тогда и добавлю.


class Order(metaclass=abc.ABCMeta):  # {{{
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
        UNDEFINE = enum.auto()
        NEW = enum.auto()

        SUBMIT = enum.auto()

        PENDING = enum.auto()
        TRIGGERED = enum.auto()

        POSTED = enum.auto()
        PARTIAL = enum.auto()
        OFF = enum.auto()
        FILLED = enum.auto()
        EXECUTED = enum.auto()

        CANCELED = enum.auto()
        BLOCKED = enum.auto()
        REJECTED = enum.auto()
        EXPIRED = enum.auto()

        ARCHIVE = enum.auto()

        @classmethod  # fromStr
        def fromStr(cls, string: str) -> Order.Status:
            statuses = {
                "NEW": Order.Status.NEW,
                "SUBMIT": Order.Status.SUBMIT,
                "PENDING": Order.Status.PENDING,
                "TRIGGERED": Order.Status.TRIGGERED,
                "POSTED": Order.Status.POSTED,
                "PARTIAL": Order.Status.PARTIAL,
                "OFF": Order.Status.OFF,
                "FILLED": Order.Status.FILLED,
                "EXECUTED": Order.Status.EXECUTED,
                "CANCELED": Order.Status.CANCELED,
                "REJECTED": Order.Status.REJECTED,
                "EXPIRED": Order.Status.EXPIRED,
                "ARCHIVE": Order.Status.ARCHIVE,
            }
            return statuses[string]

    # }}}
    class Direction(enum.Enum):  # {{{
        UNDEFINE = 0
        BUY = 1
        SELL = 2

        def toOperationDirection(self):
            if self == Order.Direction.BUY:
                return Operation.Direction.BUY

            if self == Order.Direction.SELL:
                return Operation.Direction.SELL

        @classmethod  # fromStr
        def fromStr(cls, string: str) -> Order.Direction:
            directions = {
                "BUY": Order.Direction.BUY,
                "SELL": Order.Direction.SELL,
            }
            return directions[string]

    # }}}

    @abc.abstractmethod  # __init__# {{{
    def __init__(
        self,
        order_type,
        account_name,
        direction,
        asset_id,
        lots,
        quantity,
        status,
        order_id,
        trade_id,
        exec_lots,
        exec_quantity,
        meta,
        broker_id,
        transactions,
    ):
        logger.debug("Order.__init__()")

        self.type = order_type
        self.account_name = account_name
        self.direction = direction
        self.asset_id = asset_id
        self.lots = lots
        self.quantity = quantity
        self.status = status

        self.order_id = order_id
        self.trade_id = trade_id
        self.exec_lots = exec_lots
        self.exec_quantity = exec_quantity

        self.meta = meta
        self.broker_id = broker_id
        self.transactions = transactions if transactions else list()

        # Signals
        self.statusChanged = AsyncSignal(Order)
        self.posted = AsyncSignal(Order)
        self.partial = AsyncSignal(Order)
        self.filled = AsyncSignal(Order)
        self.executed = AsyncSignal(Order, Operation)
        self.rejected = AsyncSignal(Order)
        self.canceled = AsyncSignal(Order)

    # }}}
    def __str__(self):  # {{{
        string = (
            f"type={self.type.name} "
            f"status={self.status.name} "
            f"acc={self.account_name} "
            f"{self.direction.name} "
            f"{self.asset_id.ticker} "
            f"{self.exec_lots}/{self.lots} lot"
        )

        if self.type == Order.Type.MARKET:
            pass
        elif self.type == Order.Type.LIMIT:
            string += f", {self.quantity}x{self.price}"
        elif self.type == Order.Type.STOP:
            string += f", stop={self.stop_price}, exec={self.exec_price}"

        return string

    # }}}
    async def setStatus(self, status: Order.Status):  # {{{
        logger.debug(f"Order.setStatus({status})")

        # NOTE: бывает когда маркет ордер сразу исполняется, или лимитка
        # сразу исполняется. После этого акканут запрашивает Broker.syncOrder
        # получает FILLED.
        # А через доли секунды прилетает TransactionEvent, и в его
        # обработке снова вызывается Broker.syncOrder и снова получаем
        # статус FILLED.
        # --
        # Не синхронизировать ордер сразу после выставления не вариант
        # нужне же узнать поставилась ли лимитка/стоп...
        # --
        # Как решить этот косяк на уровне общения Account / Broker
        # не придумал, так что костыляю тут - повторное присвоение
        # статуса просто пропускаем.
        if self.status == status:
            return

        self.status = status
        await Order.update(self)

        # emitting special signal for this status
        if status == Order.Status.POSTED:
            await self.posted.async_emit(self)
        if status == Order.Status.REJECTED:
            await self.rejected.async_emit(self)
        if status == Order.Status.CANCELED:
            await self.canceled.async_emit(self)

        # emiting common signal
        await self.statusChanged.async_emit(self)

    # }}}
    async def setParentTrade(self, trade):  # {{{
        logger.debug(f"Order.setParentTrade({trade})")

        self.trade_id = trade.trade_id
        await Order.update(self)

    # }}}
    async def setMeta(self, broker_response: str):  # {{{
        logger.debug(f"Order.setMeta({broker_response})")

        self.meta = broker_response
        await Order.update(self)

    # }}}
    async def attachTransaction(self, transaction: Transaction):  # {{{
        logger.debug(f"Order.attachTransaction({transaction})")

        assert transaction.order_id == self.order_id
        self.transactions.append(transaction)

        # TODO: пересчитать на основе транзакций количество
        # выполненных лотов? или у брокера это все таки
        # из ордер стэйта просто получать?
        assert False

        await Order.update(self)

    # }}}

    @classmethod  # save  # {{{
    async def save(cls, order) -> None:
        logger.debug(f"Order.save({order})")
        await Keeper.add(order)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, order_id: Id):
        logger.debug(f"Order.load({order_id})")

        order_list = await Keeper.get(cls, order_id=order_id)
        assert len(order_list) == 1
        order = order_list[0]
        return order

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, order) -> None:
        logger.debug(f"Order.delete({order})")
        await Keeper.delete(order)

    # }}}
    @classmethod  # update  # {{{
    async def update(cls, order) -> None:
        logger.debug(f"Order.update({order})")
        await Keeper.update(order)

    # }}}
    @classmethod  # fromRecord{{{
    async def fromRecord(cls, record):
        logger.debug(f"Order.fromRecord({record})")

        methods = {
            "MARKET": Order.__marketOrderFromRecord,
            "LIMIT": Order.__limitOrderFromRecord,
            "STOP": Order.__stopOrderFromRecord,
            "STOP_LOSS": Order.__stopLossFromRecord,
            "TAKE_PROFIT": Order.__takeProfitFromRecord,
        }
        method = methods[record["type"]]
        order = await method(record)
        return order

    # }}}
    @classmethod  # __marketOrderFromRecord{{{
    async def __marketOrderFromRecord(cls, record):
        logger.debug(f"Order.__marketOrderFromRecord({record})")

        ID = await InstrumentId.byFigi(figi=record["figi"])
        order = MarketOrder(
            account_name=record["account"],
            direction=Order.Direction.fromStr(record["direction"]),
            asset_id=ID,
            lots=record["lots"],
            quantity=record["quantity"],
            status=Order.Status.fromStr(record["status"]),
            order_id=record["order_id"],
            trade_id=record["trade_id"],
            exec_lots=record["exec_lots"],
            exec_quantity=record["exec_quantity"],
            meta=record["meta"],
            broker_id=record["broker_id"],
        )
        return order

    # }}}
    @classmethod  # __limitOrderFromRecord{{{
    async def __limitOrderFromRecord(cls, record):
        logger.debug(f"Order.__limitOrderFromRecord({record})")

        ID = await InstrumentId.byFigi(figi=record["figi"])
        order = LimitOrder(
            account_name=record["account"],
            direction=Order.Direction.fromStr(record["direction"]),
            asset_id=ID,
            lots=record["lots"],
            quantity=record["quantity"],
            price=record["price"],
            status=Order.Status.fromStr(record["status"]),
            order_id=Id.fromStr(record["order_id"]),
            trade_id=Id.fromStr(record["trade_id"]),
            exec_lots=record["exec_lots"],
            exec_quantity=record["exec_quantity"],
            meta=record["meta"],
            broker_id=record["broker_id"],
        )
        return order

    # }}}
    @classmethod  # __stopOrderFromRecord{{{
    async def __stopOrderFromRecord(cls, record):
        logger.debug(f"Order.__stopOrderFromRecord({record})")

        ID = await InstrumentId.byFigi(figi=record["figi"])
        order = StopOrder(
            account_name=record["account"],
            direction=Order.Direction.fromStr(record["direction"]),
            asset_id=ID,
            lots=record["lots"],
            quantity=record["quantity"],
            stop_price=record["stop_price"],
            exec_price=record["exec_price"],
            status=Order.Status.fromStr(record["status"]),
            order_id=record["order_id"],
            trade_id=record["trade_id"],
            exec_lots=record["exec_lots"],
            exec_quantity=record["exec_quantity"],
            meta=record["meta"],
            broker_id=record["broker_id"],
        )
        return order

    # }}}
    @classmethod  # __stopLossFromRecord{{{
    async def __stopLossFromRecord(cls, record):
        logger.debug(f"Order.__stopLossFromRecord({record})")

        ID = await InstrumentId.byFigi(figi=record["figi"])
        order = StopLoss(
            account_name=record["account"],
            direction=Order.Direction.fromStr(record["direction"]),
            asset_id=ID,
            lots=record["lots"],
            quantity=record["quantity"],
            stop_price=record["stop_price"],
            exec_price=record["exec_price"],
            status=Order.Status.fromStr(record["status"]),
            order_id=record["order_id"],
            trade_id=record["trade_id"],
            exec_lots=record["exec_lots"],
            exec_quantity=record["exec_quantity"],
            meta=record["meta"],
            broker_id=record["broker_id"],
        )
        return order

    # }}}
    @classmethod  # __takeProfitFromRecord{{{
    async def __takeProfitFromRecord(cls, record):
        logger.debug(f"Order.__takeProfitFromRecord({record})")

        ID = await InstrumentId.byFigi(figi=record["figi"])
        order = TakeProfit(
            account_name=record["account"],
            direction=Order.Direction.fromStr(record["direction"]),
            asset_id=ID,
            lots=record["lots"],
            quantity=record["quantity"],
            stop_price=record["stop_price"],
            exec_price=record["exec_price"],
            status=Order.Status.fromStr(record["status"]),
            order_id=record["order_id"],
            trade_id=record["trade_id"],
            exec_lots=record["exec_lots"],
            exec_quantity=record["exec_quantity"],
            meta=record["meta"],
            broker_id=record["broker_id"],
        )
        return order


# }}}


# }}}
class MarketOrder(Order):  # {{{
    def __init__(
        self,
        account_name: str,
        direction: Order.Direction,
        asset_id: InstrumentId,
        lots: int,
        quantity: int,
        status: Order.Status = Order.Status.NEW,
        order_id: Optional[Id] = None,
        trade_id: Optional[Id] = None,
        exec_lots: int = 0,
        exec_quantity: int = 0,
        meta: str = "",
        broker_id: str = "",
        transactions=Optional[list],
    ):
        # TODO: в базовом классе значения по умолчанию пожалуй не нужны
        # наоборот пусть явно все передается. Явное лучше неявного.
        # А вот в производных классах для удобства можно в конструкторах
        # поставить значения по умолчанию.
        super().__init__(
            Order.Type.MARKET,
            account_name,
            direction,
            asset_id,
            lots,
            quantity,
            status,
            order_id,
            trade_id,
            exec_lots,
            exec_quantity,
            meta=meta,
            broker_id=broker_id,
            transactions=transactions,
        )


# }}}
class LimitOrder(Order):  # {{{
    def __init__(
        self,
        account_name: str,
        direction: Order.Direction,
        asset_id: InstrumentId,
        lots: int,
        quantity: int,
        price: float,
        status: Order.Status = Order.Status.NEW,
        order_id: Optional[Id] = None,
        trade_id: Optional[Id] = None,
        exec_lots: int = 0,
        exec_quantity: int = 0,
        meta: str = "",
        broker_id: str = "",
        transactions=Optional[list],
    ):
        super().__init__(
            Order.Type.LIMIT,
            account_name,
            direction,
            asset_id,
            lots,
            quantity,
            status,
            order_id,
            trade_id,
            exec_lots,
            exec_quantity,
            meta=meta,
            broker_id=broker_id,
            transactions=transactions,
        )
        self.price = price


# }}}
class StopOrder(Order):  # {{{
    def __init__(
        self,
        account_name: str,
        direction: Order.Direction,
        asset_id: InstrumentId,
        lots: int,
        quantity: int,
        stop_price: float,
        exec_price: float,
        status: Order.Status = Order.Status.NEW,
        order_id: Optional[Id] = None,
        trade_id: Optional[Id] = None,
        exec_lots: int = 0,
        exec_quantity: int = 0,
        meta: str = "",
        broker_id: str = "",
        transactions=Optional[list],
    ):
        super().__init__(
            Order.Type.STOP,
            account_name,
            direction,
            asset_id,
            lots,
            quantity,
            status,
            order_id,
            trade_id,
            exec_lots,
            exec_quantity,
            meta=meta,
            broker_id=broker_id,
            transactions=transactions,
        )
        self.stop_price = stop_price
        self.exec_price = exec_price


# }}}
class StopLoss(Order):  # {{{
    def __init__(
        self,
        account_name: str,
        direction: Order.Direction,
        asset_id: InstrumentId,
        lots: int,
        quantity: int,
        stop_price: float,
        exec_price: float,
        status: Order.Status = Order.Status.NEW,
        order_id: Optional[Id] = None,
        trade_id: Optional[Id] = None,
        exec_lots: int = 0,
        exec_quantity: int = 0,
        meta: str = "",
        broker_id: str = "",
        transactions=Optional[list],
    ):
        super().__init__(
            Order.Type.STOP_LOSS,
            account_name,
            direction,
            asset_id,
            lots,
            quantity,
            status,
            order_id,
            trade_id,
            exec_lots,
            exec_quantity,
            meta=meta,
            broker_id=broker_id,
            transactions=transactions,
        )
        self.stop_price = stop_price
        self.exec_price = exec_price


# }}}
class TakeProfit(Order):  # {{{
    def __init__(
        self,
        account_name: str,
        direction: Order.Direction,
        asset_id: InstrumentId,
        lots: int,
        quantity: int,
        stop_price: float,
        exec_price: float,
        status: Order.Status = Order.Status.NEW,
        order_id: Optional[Id] = None,
        trade_id: Optional[Id] = None,
        exec_lots: int = 0,
        exec_quantity: int = 0,
        meta: str = "",
        broker_id: str = "",
        transactions=Optional[list],
    ):
        # TODO: InstrumentId.min_price_step - все таки надо грузить
        # сразу при создании из базы, иначе тут жопа, каждый раз загружать
        # эту хуйню...
        # инфо же один хер загружается - так вот пусть к инфо полю
        # и лепится в конструкторе сразу. Будут проблемы с памятью, тогда
        # и буду решать, а то пока проблемы только с тем что везде
        # это количество лотов и мин прайс степ приходится грузить.

        super().__init__(
            Order.Type.TAKE_PROFIT,
            account_name,
            direction,
            asset_id,
            lots,
            quantity,
            status,
            order_id,
            trade_id,
            exec_lots,
            exec_quantity,
            meta=meta,
            broker_id=broker_id,
            transactions=transactions,
        )
        self.stop_price = stop_price
        self.exec_price = exec_price


#
#
# # }}}
class WaitOrder(Order):  # {{{
    ...


# }}}
class TrailingOrder(Order):  # {{{
    ...


# }}}
