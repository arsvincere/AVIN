#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime, time

from avin.core.broker import Broker
from avin.core.event import TransactionEvent
from avin.core.id import Id
from avin.core.operation import Operation
from avin.core.order import Order
from avin.utils import logger, now

# TODO: а тут соответственно может быть сигнал
# order_executed = AsyncSignal(Order)
# раз у брокера сигналы
#    new_bar = AsyncSignal(NewHistoricalBarEvent)
#    new_transaction = AsyncSignal(TransactionEvent)
# то логично у аккаунта такой сигнал иметь..
# и наверное можно не отменять сигналы у ордера и трейдов...
# пусть они будут.
# пусть на них тоже можно будет подписываться. Мало ли для чего
# понадобятся, они внутри этих классов тоже логично смотрятся...
# а вот поток данных глобальный при работе тестера и трейдера
# лучше провести через тестера и трейдера соответственно а не напрямую
# от ордера трейду... И там стратегия свой трейд ловит...
# Возможно лучше будет подобно тому как аккаунт получает операцию от
# брокера, через метод receive, так же стратегия пусть получает
# выполненный свой ордер...
# А то получается при загрузке ордеров и трейдов их надо снова линковать...
# а тут если бы данные шли по крупным магистралям через трейдера/тестера
# то перелинковка не понадобилась бы, они бы сами внутри себя находили
# ownera и ему передавали это событие...
# Тут еще подумать надо над событийной моделью, и сигнальной моделью...
# И изучить в Qt в чем разница между Event и Signal по какому принципу
# их там разделил...


class Account:
    def __init__(self, name: str, broker: Broker, meta: object):  # {{{
        logger.debug(f"Account.__init__({name}, {broker}, {meta})")
        self.__name = name
        self.__broker = broker
        self.__meta = meta
        self.__active_orders = list()

    # }}}
    def __str__(self):  # {{{
        return f"Account={self.__name}"

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
        logger.debug("Account.post()")
        logger.info(f":: Post: {order}")

        self.__active_orders.append(order)

        post_methods = {
            Order.Type.MARKET: self.__broker.postMarketOrder,
            Order.Type.LIMIT: self.__broker.postLimitOrder,
            Order.Type.STOP: self.__broker.postStopOrder,
            Order.Type.STOP_LOSS: self.__broker.postStopLoss,
            Order.Type.TAKE_PROFIT: self.__broker.postTakeProfit,
        }
        method = post_methods[order.type]
        result = await method(self, order)

        if not result:
            assert False, "чет не палучилась, подумай что делать тогда"

        await self.broker.syncOrder(self, order)

        # TODO:
        # обработать неудачные попытки Order.Status: UNDEFINE, REJECTED

        return result

    # }}}
    async def cancel(self, order) -> bool:  # {{{
        logger.debug("Account.cancel()")
        # logger.info(f":: Cancel: {order}")

        # TODO: а что если такого ордера нет?
        # что sync тогда вернте?
        await self.broker.syncOrder(self, order)

        t = Order.Type
        if order.type == t.LIMIT:
            result = await self.__broker.cancelLimitOrder(self, order)
        elif order.type in (t.STOP, t.STOP_LOSS, t.TAKE_PROFIT):
            result = await self.__broker.cancelStopOrder(self, order)
        else:
            assert False, f"че за тип ордера? {order.type}"

        # remove order from self.__active_orders
        self.__active_orders.remove(order)

        return result

    # }}}
    async def receive(self, event: TransactionEvent):  # {{{
        logger.debug("Account.receive()")
        assert isinstance(event, TransactionEvent)

        order = None
        for i in self.__active_orders:
            if i.broker_id == event.order_broker_id:
                order = i
                break
        if not order:
            logger.warning(f"{self} received {event}, but order not found")
            return

        logger.info(f"-> {self} receive {event}")

        await self.broker.syncOrder(self, order)
        if order.status == Order.Status.FILLED:
            await self.__onOrderFilled(order)

    # }}}
    async def __onOrderFilled(self, order: Order):  # {{{
        logger.debug(f"Account.__onOrderFilled({order})")
        assert order.status == Order.Status.FILLED

        # get order operation, save
        operation = await self.__broker.getOrderOperation(self, order)
        operation.operation_id = Id.newId()
        await Operation.save(operation)

        # remove order from active, send signal 'executed'
        await order.setStatus(Order.Status.EXECUTED)
        self.__active_orders.remove(order)
        await order.executed.aemit(order, operation)

        # await commission for operation
        if operation.commission == 0:
            await self.__requestCommission(order, operation)

    # }}}
    async def __requestCommission(self, order, operation):  # {{{
        logger.info("Account.__requestCommission()")

        while operation.commission == 0:
            await asyncio.sleep(10)
            c = await self.__broker.getExecutedCommission(self, order)
            operation.commission = c

        await Operation.update(operation)
        logger.info(
            f"Account '{self.name}' receive commission for: {operation}"
        )


# }}}


if __name__ == "__main__":
    ...
