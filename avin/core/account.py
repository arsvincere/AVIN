#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""doc"""

from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime, time

from avin.core.broker import Broker
from avin.core.event import TransactionEvent
from avin.core.operation import Operation
from avin.core.order import Order
from avin.utils import logger, now


class Account:
    def __init__(self, name: str, broker: Broker, meta: object):  # {{{
        logger.debug("Account.__init__()")
        self.__name = name
        self.__broker = broker
        self.__meta = meta
        self.__active_orders = list()

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__name

    # }}}
    @property  # broker# {{{
    def broker(self):
        return self.__broker

    # }}}
    @property  # meta# {{{
    def meta(self):
        return self.__meta

    # }}}
    async def addMoney(self, money: float):  # {{{
        logger.debug(f"Account.addMoney({money})")
        await self.__broker.addMoney(self, money)

    # }}}
    async def money(self):  # {{{
        logger.debug("Account.money()")
        money = await self.__broker.getMoney(self)
        return money

    # }}}
    async def orders(self):  # {{{
        logger.debug("Account.orders()")

        limit_orders = await self.__broker.getLimitOrders(self)

        if self.__broker.TARGET == Sandbox.TARGET:
            stop_orders = list()
        else:
            stop_orders = await self.__broker.getStopOrders(self)

        return limit_orders + stop_orders

    # }}}
    async def operations(self, begin=None, end=None):  # {{{
        logger.debug("Account.operations()")

        if begin is None and end is None:
            end = now()
            begin = datetime.combine(date.today(), time(0, 0), UTC)

        operations = await self.__broker.getOperations(self, begin, end)
        return operations

    # }}}
    async def positions(self) -> Portfolio:  # {{{
        logger.debug("Account.positions()")

        positions = await self.__broker.getPositions(self)
        return positions

    # }}}
    async def portfolio(self) -> Portfolio:  # {{{
        logger.debug("Account.portfolio()")
        portfolio = await self.__broker.getPortfolio(self)
        return portfolio

    # }}}
    async def withdrawLimits(self):  # {{{
        logger.debug("Account.withdrawLimits()")
        limits = await self.__broker.getWithdrawLimits(self)
        return limits

    # }}}
    async def post(self, order: Order) -> bool:  # {{{
        logger.info(f":: Account {self.__name} post order: {order}")

        post_methods = {
            Order.Type.MARKET: self.__broker.postMarketOrder,
            Order.Type.LIMIT: self.__broker.postLimitOrder,
            Order.Type.STOP: self.__broker.postStopOrder,
            Order.Type.STOP_LOSS: self.__broker.postStopLoss,
            Order.Type.TAKE_PROFIT: self.__broker.postTakeProfit,
        }
        method = post_methods[order.type]
        result = method(self, order)

        if result:
            self.__active_orders.append(order)
            await order.filled.async_connect(self.__onOrderFilled)
            await self.__broker.syncOrder(self, order)

        return result

    # }}}
    async def cancel(self, order):  # {{{
        assert False, "Не переписывал еще этот метод, на обновленного Брокера"
        logger.info(
            f"Cancel order: {order.type.name} "
            f"{order.direction.name} "
            f"{order.asset.ticker} "
            f"{order.lots} x ({order.asset.lot}) x {order.price}, "
            f"exec_price={order.exec_price} "
            f"ID={order.ID}"
        )
        if order.type == Order.Type.LIMIT:
            response = self.__broker.cancelLimitOrder(self, order)
        else:
            response = self.__broker.cancelStopOrder(self, order)
        logger.info(f"Cancel order: Response='{response}'")
        return response

    # }}}
    async def receiveTransaction(self, event: TransactionEvent):  # {{{
        logger.info(f"{event}")

        self.__active_orders.sort
        for i in self.__active_orders:
            if order.broker_id == event.order_broker_id:
                order = i
                break

        await self.broker.syncOrder(self, order)

    # }}}
    @classmethod  # fromRecord  # {{{
    def fromRecord(cls, record):
        # FIX:
        # пока захардкорил в аккаунте имя и броке - это тупо строки.
        # потом надо будет сделать что-то типо account.setConnection(broker)
        # и там внутри проверяется что broker.isConnected()
        # а что там с переменной meta делать пока вообще вопрос.. подумаю...
        # При этом весь код в классе - подразумевает что broker - это не
        # строка а объект класса брокер. Надо будет переделать потом.
        acc = Account(name=record["name"], broker=record["broker"], meta=None)
        return acc

    # }}}

    async def __onOrderFilled(self, order: Order):  # {{{
        logger.debug(f"Account.__onOrderFilled({order})")
        assert order.status == Order.Status.FILLED

        operation = self.__broker.getOrderOperation(self, order)

        await Operation.save(operation)
        await order.setStatus(Order.Status.EXECUTED)
        await order.executed.async_emit(order, operation)

        # await commission for operation
        if operation.commission == 0:
            asyncio.create_task(self.__requestCommission(order, operation))

    # }}}
    async def __requestCommission(self, order, operation):  # {{{
        logger.debug("Account.__requestCommission()")

        while operation.commission == 0:
            await asyncio.sleep(10)
            c = await self.__broker.getExecutedCommission(self, order)
            operation.commission = c

        await Operation.update(operation)


# }}}
