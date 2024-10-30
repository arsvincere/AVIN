#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from typing import Optional, Union

from avin.core import (
    Account,
    Asset,
    BarChangedEvent,
    Broker,
    Event,
    LimitOrder,
    NewHistoricalBarEvent,
    Operation,
    Order,
    StopLoss,
    StopOrder,
    TakeProfit,
    TimeFrame,
    Transaction,
    TransactionEvent,
)
from avin.tester._stream import _BarStream
from avin.tester.test import Test
from avin.utils import AsyncSignal, logger


class _VirtualBroker(Broker):
    name = "_VirtualBroker"
    new_bar = AsyncSignal(NewHistoricalBarEvent)
    bar_changed = AsyncSignal(BarChangedEvent)
    new_transaction = AsyncSignal(TransactionEvent)

    __test: Optional[Test] = None
    __account: Optional[Account] = None
    __data_stream: Optional[_BarStream] = None
    __current_asset: Optional[Asset] = None
    __limit_orders: list[LimitOrder] = list()
    __stop_orders: list[Union[StopOrder, StopLoss, TakeProfit]] = list()

    @classmethod  # setTest  # {{{
    def setTest(cls, test: Test):
        logger.debug(f"{cls.__name__}.setTest()")
        cls.__test = test

    # }}}
    @classmethod  # getAccount  # {{{
    def getAccount(cls, account_name: str) -> Account:
        logger.debug(f"{cls.__name__}.getAccount({account_name})")

        # WARN: костыль
        # пока тестер работает только с одним аккаунтом,
        # так проще, потому если понадобится буду думать
        # как сделать работу с несколькими аккаунтами
        assert account_name == "_backtest"
        cls.__account = Account(account_name, broker=cls, meta=None)
        return cls.__account

    # }}}
    @classmethod  # postMarketOrder{{{
    async def postMarketOrder(cls, account: Account, order: Order) -> bool:
        logger.debug(f"{cls.__name__}.postMarketOrder({account}, {order})")

        # TODO:
        # в методах выставления ордеров - ебана куча повторяющегося кода
        # выпили все это в какой нибудь общий приватный метод

        # change order status
        # NOTE: аккаунт использует broker_id потом для
        # сопоставления ордеров, по другому с Тиньковым никак не придумал
        # в режиме тестера чтобы ничего не менять в логике работы
        # тупо присваиваю свой внутренний Id, как broker_id
        # там не важно, главное чтобы он был уникальным
        order.broker_id = order.order_id
        order.status = Order.Status.FILLED
        order.meta = "virtual executed"

        assert cls.__current_asset is not None
        chart = cls.__current_asset.chart(TimeFrame("1M"))
        bar = chart.now
        await cls.__executeOrder(order, bar)

        return True

    # }}}
    @classmethod  # postLimitOrder{{{
    async def postLimitOrder(
        cls, account: Account, order: LimitOrder
    ) -> bool:
        logger.debug(f"{cls.__name__}.postLimitOrder({account}, {order})")

        order.broker_id = order.order_id
        order.status = Order.Status.POSTED
        order.meta = "virtual posted"

        cls.__limit_orders.append(order)

        # check now bar
        assert cls.__current_asset is not None
        chart = cls.__current_asset.chart(TimeFrame("1M"))
        bar = chart.now
        if order.price in bar:
            await cls.__executeOrder(order, bar)

        return True

    # }}}
    @classmethod  # postStopOrder{{{
    async def postStopOrder(cls, account: Account, order: StopOrder) -> bool:
        logger.debug(f"{cls.__name__}.postStopOrder({account}, {order})")

        order.broker_id = order.order_id
        order.status = Order.Status.POSTED
        order.meta = "virtual posted"

        cls.__stop_orders.append(order)

        # check now bar
        assert cls.__current_asset is not None
        chart = cls.__current_asset.chart(TimeFrame("1M"))
        bar = chart.now
        if order.stop_price in bar:
            await cls.__executeOrder(order, bar)

        return True

    # }}}
    @classmethod  # postStopLoss{{{
    async def postStopLoss(cls, account: Account, order: StopLoss) -> bool:
        logger.debug(f"{cls.__name__}.postStopLoss({account}, {order})")

        order.broker_id = order.order_id
        order.status = Order.Status.POSTED
        order.meta = "virtual posted"

        cls.__stop_orders.append(order)

        # check now bar
        assert cls.__current_asset is not None
        chart = cls.__current_asset.chart(TimeFrame("1M"))
        bar = chart.now
        if order.stop_price in bar:
            await cls.__executeOrder(order, bar)

        return True

    # }}}
    @classmethod  # postTakeProfit{{{
    async def postTakeProfit(
        cls, account: Account, order: TakeProfit
    ) -> bool:
        logger.debug(f"{cls.__name__}.postTakeProfit({account}, {order})")

        order.broker_id = order.order_id
        order.status = Order.Status.POSTED
        order.meta = "virtual posted"

        cls.__stop_orders.append(order)

        return True

    # }}}

    @classmethod  # syncOrder{{{
    async def syncOrder(cls, account: Account, order: Order) -> bool:
        logger.debug(f"{cls.__name__}.syncOrder({order})")

        # Это метод заглушка, аккаунт использует вызов Broker.syncOrder
        # для синхронизации статуса ордера при торговле с Тинькофф
        # в режиме тестера просто ничего не делаем.
        return True

    # }}}
    @classmethod  # getOrderOperation  # {{{
    async def getOrderOperation(
        cls, account: Account, order: Order
    ) -> Operation:
        logger.debug(f"{cls.__name__}.getOrderOperation({account}, {order})")
        assert cls.__test is not None

        dt = order.transactions.last.dt
        price = order.transactions.average()
        amount = order.transactions.amount()
        commission = amount * cls.__test.commission

        operation = Operation(
            account_name=account.name,
            dt=dt,
            direction=order.direction,
            instrument=order.instrument,
            lots=order.lots,
            quantity=order.quantity,
            price=price,
            amount=amount,
            commission=commission,
            operation_id=None,
            order_id=order.order_id,
            trade_id=order.trade_id,
            meta="virtual operation",
        )

        return operation

    # }}}

    @classmethod  # createBarStream  # {{{
    def createBarStream(cls, asset: Asset, timeframe: TimeFrame) -> None:
        logger.info(f"  - create bar stream {asset}-{timeframe}")

        if not cls.__data_stream:
            cls.__data_stream = _BarStream()

        cls.__data_stream.subscribe(asset, timeframe)

        # WARN: костыль
        # пока режим работы по одному ассету прогоняет тестер
        # так проще, потом подумаю как лучше это сделать
        cls.__current_asset = asset

    # }}}
    @classmethod  # startDataStream  # {{{
    async def startDataStream(cls):
        logger.info("  - start data stream")

        await cls.__data_stream.loadData(cls.__test.begin, cls.__test.end)
        for event in cls.__data_stream:
            if event.type == Event.Type.BAR_CHANGED:
                await cls.bar_changed.async_emit(event)
                await cls.__checkOrders(event)
            elif event.type == Event.Type.NEW_HISTORICAL_BAR:
                await cls.new_bar.async_emit(event)
            else:
                assert False, "так не должно быть"

    # }}}

    @classmethod  # __checkOrders  # {{{
    async def __checkOrders(cls, event: BarChangedEvent) -> None:
        logger.debug(f"{cls.__name__}.__checkOrders()")

        # Смотрим сработку ордеров только на 1М таймфрейме
        # в эвенте приходит now bar
        if event.timeframe != "1M":
            return

        bar = event.bar

        # check limit orders
        i = 0
        while i < len(cls.__limit_orders):
            l_order = cls.__limit_orders[i]
            price = l_order.price
            if price in bar:
                await cls.__executeOrder(l_order, bar)
                cls.__limit_orders.pop(i)

            i += 1

        # check stop orders
        i = 0
        while i < len(cls.__stop_orders):
            s_order = cls.__stop_orders[i]
            # TODO: пока не парюсь с exec_price, считаю что
            # stop_price всегда равен exec_price
            # потом переделать нормально
            price = s_order.stop_price
            if price in bar:
                await cls.__executeOrder(s_order, bar)
                cls.__stop_orders.pop(i)

            i += 1

    # }}}
    @classmethod  # __executeOrder{{{
    async def __executeOrder(cls, order, bar):
        logger.debug(f"{cls.__name__}.__executeOrder()")

        # recognise execution price
        match order.type:
            case Order.Type.MARKET:
                price = bar.open
            case Order.Type.LIMIT:
                price = order.price
            case Order.Type.STOP:
                price = order.stop_price
            case Order.Type.STOP_LOSS:
                price = order.stop_price
            case Order.Type.TAKE_PROFIT:
                price = order.stop_price

        # create transaction, then attach to order
        transaction = Transaction(
            order_id=order.order_id,
            dt=bar.dt,
            quantity=order.quantity,
            price=price,
            broker_id=order.broker_id,
        )
        await order.attachTransaction(transaction)
        order.meta = "virtual executed"

        # create and send TransactionEvent
        event = TransactionEvent(
            account_name=cls.__account.name,
            figi=order.instrument.figi,
            direction=order.direction,
            order_broker_id=order.broker_id,
            transaction=transaction,
        )
        await cls.new_transaction.async_emit(event)
        await cls.__account.receive(event)

    # }}}


if __name__ == "__main__":
    ...
