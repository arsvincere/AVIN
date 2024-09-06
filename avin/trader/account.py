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

from avin.core import Operation, Order
from avin.logger import logger
from avin.utils import now


class Account:  # {{{
    def __init__(self, name: str, broker: str, meta: object):  # {{{
        logger.debug("Account.__init__()")
        self.__name = name
        self.__broker = broker
        self.__meta = meta

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
    def addMoney(self, money):  # {{{
        logger.debug(f"Account.addMoney({money})")
        self.__broker.addMoney(self.__meta, money)

    # }}}
    def money(self):  # {{{
        logger.debug("Account.money()")
        return self.__broker.getMoney(self.__meta)

    # }}}
    def orders(self):  # {{{
        logger.debug("Account.orders()")
        limit_orders = self.__broker.getLimitOrders(self.__meta)
        if self.__broker.TARGET == Sandbox.TARGET:
            stop_orders = list()
        else:
            stop_orders = self.__broker.getStopOrders(self.__meta)
        return limit_orders + stop_orders

    # }}}
    def operations(self, begin=None, end=None):  # {{{
        logger.debug("Account.operations()")
        if begin is None:
            end = now()
            begin = datetime.combine(date.today(), time(0, 0), UTC)
        operations = self.__broker.getOperations(self.__meta, begin, end)
        return operations

    # }}}
    def portfolio(self) -> Portfolio:  # {{{
        logger.debug("Account.positions()")
        portfolio = self.__broker.getPositions(self.__meta)
        return portfolio

    # }}}
    def detailedPortfolio(self) -> Portfolio:  # {{{
        logger.debug("Account.portfolio()")
        p = self.__broker.getDetailedPortfolio(self.__meta)
        return p

    # }}}
    def withdrawLimits(self):  # {{{
        logger.debug("Account.withdrawLimits()")
        return self.__broker.getWithdrawLimits(self.__meta)

    # }}}
    async def post(self, order: Order):  # {{{
        logger.info(f":: Account {self.__name} post order: {order}")

        await order.filled.async_connect(self.onOrderFilled)

        if order.type == Order.Type.MARKET:
            order = await self.__broker.postMarketOrder(order, self.__meta)
        elif order.type == Order.Type.LIMIT:
            order = await self.__broker.postLimitOrder(order, self.__meta)
        elif order.type in (
            Order.Type.STOP,
            Order.Type.STOP_LOSS,
            Order.Type.TAKE_PROFIT,
        ):
            order = await self.__broker.postStopOrder(order, self.__meta)
        elif (
            order.type == Order.Type.WAIT or order.type == Order.Type.TRAILING
        ):
            assert False

        return order

    # }}}
    def cancel(self, order):  # {{{
        logger.info(
            f"Cancel order: {order.type.name} "
            f"{order.direction.name} "
            f"{order.asset.ticker} "
            f"{order.lots} x ({order.asset.lot}) x {order.price}, "
            f"exec_price={order.exec_price} "
            f"ID={order.ID}"
        )
        if order.type == Order.Type.LIMIT:
            response = self.__broker.cancelLimitOrder(order, self.__meta)
        else:
            response = self.__broker.cancelStopOrder(order, self.__meta)
        logger.info(f"Cancel order: Response='{response}'")
        return response

    # }}}
    async def onOrderFilled(self, order: Order):
        logger.debug(f"{self.__class__.__name__}.onOrderFilled({order})")
        assert order.status == Order.Status.FILLED

        # TODO: здесь конечно надо чтото другое придумать
        # лучше всего наверное записывать операции в БД как есть
        # без комиссии, а потом, через некоторое время уже чекать снова
        # ордер и доставать комиссию по операции
        # можно сделать например так:
        # Keeper.update(Operation, order_id=xxx, commission=xxx)
        print("sleep 1 sec, wait commission")
        await asyncio.sleep(1)
        print("wake up")

        operation = self.__broker.getOrderOperation(self.__meta, order)

        await Operation.save(operation)
        await order.setStatus(Order.Status.EXECUTED)
        await order.executed.async_emit(order, operation)

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


# }}}
