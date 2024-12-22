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
    Direction,
    Event,
    LimitOrder,
    MarketOrder,
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
from avin.tester.stream import BarStream
from avin.tester.test import Test
from avin.utils import AsyncSignal, logger


class VirtualBroker(Broker):
    name = "_VirtualBroker"

    new_bar = AsyncSignal(NewHistoricalBarEvent)
    bar_changed = AsyncSignal(BarChangedEvent)
    new_transaction = AsyncSignal(TransactionEvent)

    __test: Optional[Test] = None
    __account: Optional[Account] = None
    __data_stream: Optional[BarStream] = None
    __current_asset: Optional[Asset] = None
    __market_orders: list[MarketOrder] = list()
    __limit_orders: list[LimitOrder] = list()
    __stop_orders: list[Union[StopOrder, StopLoss, TakeProfit]] = list()

    @classmethod  # setTest  # {{{
    def setTest(cls, test: Test):
        logger.debug(f"{cls.__name__}.setTest()")
        cls.__test = test

    # }}}
    @classmethod  # reset  # {{{
    def reset(cls):
        logger.debug(f"{cls.__name__}.reset()")

        cls.__test = None
        cls.__account = None
        cls.__data_stream = None
        cls.__current_asset = None
        cls.__market_orders = list()
        cls.__limit_orders = list()
        cls.__stop_orders = list()

        # сброс конектов к сигналам...
        # TODO: а может сделать прямо new_bar.disconnect(slot) ??
        # и new_bar.disconnectAll() ??
        cls.new_bar = AsyncSignal(NewHistoricalBarEvent)
        cls.bar_changed = AsyncSignal(BarChangedEvent)
        cls.new_transaction = AsyncSignal(TransactionEvent)

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

    @classmethod  # syncOrder  # {{{
    async def syncOrder(cls, account: Account, order: Order) -> bool:
        logger.debug(f"{cls.__name__}.syncOrder({order})")

        # Это метод заглушка, аккаунт использует вызов Broker.syncOrder
        # для синхронизации статуса ордера при торговле с Тинькофф
        # в режиме тестера просто ничего не делаем.
        # статус ордерам ставится в методах postLimitOrder, __executeOrder...
        return True

    # }}}
    @classmethod  # postMarketOrder  # {{{
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

        cls.__market_orders.append(order)
        await order.setStatus(Order.Status.POSTED)

        return True

    # }}}
    @classmethod  # postLimitOrder  # {{{
    async def postLimitOrder(
        cls, account: Account, order: LimitOrder
    ) -> bool:
        logger.debug(f"{cls.__name__}.postLimitOrder({account}, {order})")

        order.broker_id = order.order_id
        order.status = Order.Status.POSTED
        order.meta = "virtual posted"

        cls.__limit_orders.append(order)
        await order.setStatus(Order.Status.POSTED)

        # check now bar
        assert cls.__current_asset is not None
        chart = cls.__current_asset.chart(TimeFrame("1M"))
        bar = chart.now

        if order.price in bar:
            await cls.__executeOrder(order, bar)

        return True

    # }}}
    @classmethod  # postStopOrder  # {{{
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
    @classmethod  # postStopLoss  # {{{
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
    @classmethod  # postTakeProfit  # {{{
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
    @classmethod  # cancelLimitOrder  # {{{
    async def cancelLimitOrder(
        cls, account: Account, order: LimitOrder
    ) -> bool:
        logger.debug(f"{cls.__name__}.cancelLimitOrder({account}, {order})")

        # TODO: а что если ордер частично исполнен?
        # ну пока такое не возможно, но в будущем в тестере это надо
        # учесть..

        for posted_order in cls.__limit_orders:
            if posted_order.order_id == order.order_id:
                cls.__limit_orders.remove(posted_order)
                await order.setStatus(Order.Status.CANCELED)
                return True

        logger.warning(
            f"VirtualBroker.cancelLimitOrder() - not found {order}"
        )
        return True

    # }}}
    @classmethod  # cancelStopOrder  # {{{
    async def cancelStopOrder(
        cls, account: Account, order: StopOrder
    ) -> bool:
        logger.debug(f"{cls.__name__}.cancelStopOrder({account}, {order})")

        for posted_order in cls.__stop_orders:
            if posted_order.order_id == order.order_id:
                cls.__stop_orders.remove(posted_order)
                await order.setStatus(Order.Status.CANCELED)

                return True

        logger.warning(f"VirtualBroker.cancelStopOrder() - not found {order}")
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
        logger.debug(f"{cls.__name__}.createBarStream({asset}, {timeframe})")

        if not cls.__data_stream:
            cls.__data_stream = BarStream()

        cls.__data_stream.subscribe(asset, timeframe)

        # WARN: костыль
        # пока режим работы по одному ассету прогоняет тестер
        # так проще, потом подумаю как лучше это сделать
        cls.__current_asset = asset

    # }}}
    @classmethod  # runDataStream  # {{{
    async def runDataStream(cls):
        logger.debug(f"{cls.__name__}.runDataStream()")

        await cls.__data_stream.loadData(cls.__test.begin, cls.__test.end)
        for event in cls.__data_stream:
            if event.type == Event.Type.NEW_HISTORICAL_BAR:
                await cls.new_bar.aemit(event)
            if event.type == Event.Type.BAR_CHANGED:
                await cls.bar_changed.aemit(event)
                await cls.__checkOrders(event)

    # }}}

    @classmethod  # __checkOrders  # {{{
    async def __checkOrders(cls, event: BarChangedEvent) -> None:
        logger.debug(f"{cls.__name__}.__checkOrders()")

        # Смотрим сработку ордеров только на 1М таймфрейме
        # в эвенте приходит now bar
        if event.timeframe != "1M":
            return

        bar = event.bar

        # check market orders
        i = 0
        while i < len(cls.__market_orders):
            m_order = cls.__market_orders[i]
            await cls.__executeOrder(m_order, bar)

        # FIX: Ахтунг!!!!!!!!!!!
        # надо же проверять выполнение лимитных и стоп ордеров не
        # только при попадании цены в бар, но и больше меньше цены
        # сработки, наступал уже на эти грабли в старом тестере
        # ..................................

        # check limit orders
        i = 0
        while i < len(cls.__limit_orders):
            l_order = cls.__limit_orders[i]
            price = l_order.price
            if price in bar:
                await cls.__executeOrder(l_order, bar)
                continue

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
                continue

            if s_order.type == Order.Type.STOP_LOSS:
                # Трейд в лонг.
                # Если цена открылась ниже стоп прайса, то стоп лосс
                # срабатывает по цене открытия бара
                if s_order.direction == Direction.SELL:
                    if bar.open < s_order.stop_price:
                        await cls.__executeOrder(s_order, bar.dt, bar.open)
                        continue

                # Трейд в шорт.
                # Если цена открылась выше стоп прайса, то стоп лосс
                # срабатывает по цене открытия бара
                if s_order.direction == Direction.BUY:
                    if bar.open > s_order.stop_price:
                        await cls.__executeOrder(s_order, bar.dt, bar.open)
                        continue

            if s_order.type == Order.Type.TAKE_PROFIT:
                # Трейд в лонг.
                # Если цена открылась выше стоп прайса, то тейк профит
                # срабатывает по цене открытия бара
                if s_order.direction == Direction.SELL:
                    if bar.open > s_order.stop_price:
                        await cls.__executeOrder(s_order, bar.dt, bar.open)
                        continue

                # Трейд в шорт.
                # Если цена открылась ниже стоп прайса, то тейк профит
                # срабатывает по цене открытия бара
                if s_order.direction == Direction.BUY:
                    if bar.open < s_order.stop_price:
                        await cls.__executeOrder(s_order, bar.dt, bar.open)
                        continue

            i += 1

    # }}}
    @classmethod  # __executeOrder  # {{{
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
        await order.setStatus(Order.Status.FILLED)
        cls.__removeOrder(order)

        # create and send TransactionEvent
        event = TransactionEvent(
            account_name=cls.__account.name,
            figi=order.instrument.figi,
            direction=order.direction,
            order_broker_id=order.broker_id,
            transaction=transaction,
        )
        await cls.new_transaction.aemit(event)
        await cls.__account.receive(event)

    # }}}
    @classmethod  # __removeOrder  #{{{
    def __removeOrder(cls, order: Order):
        logger.debug(f"{cls.__name__}.__executeOrder()")

        match order.type:
            case Order.Type.MARKET:
                all_orders = cls.__market_orders
            case Order.Type.LIMIT:
                all_orders = cls.__limit_orders
            case Order.Type.STOP:
                all_orders = cls.__stop_orders
            case Order.Type.STOP_LOSS:
                all_orders = cls.__stop_orders
            case Order.Type.TAKE_PROFIT:
                all_orders = cls.__stop_orders
            case _:
                assert False, f"че за ордер? {order}"

        for i in all_orders:
            if i.order_id == order.order_id:
                all_orders.remove(i)
                return

    # }}}


if __name__ == "__main__":
    ...
