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
    Bar,
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
        cls.__current_asset = test.asset

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
        order.meta = "virtual posted"
        await order.setStatus(Order.Status.POSTED)

        cls.__market_orders.append(order)

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
        await order.setStatus(Order.Status.POSTED)

        cls.__limit_orders.append(order)

        return True

    # }}}
    @classmethod  # postStopOrder  # {{{
    async def postStopOrder(cls, account: Account, order: StopOrder) -> bool:
        logger.debug(f"{cls.__name__}.postStopOrder({account}, {order})")

        order.broker_id = order.order_id
        order.status = Order.Status.POSTED
        order.meta = "virtual posted"
        await order.setStatus(Order.Status.POSTED)

        cls.__stop_orders.append(order)

        return True

    # }}}
    @classmethod  # postStopLoss  # {{{
    async def postStopLoss(cls, account: Account, order: StopLoss) -> bool:
        logger.debug(f"{cls.__name__}.postStopLoss({account}, {order})")

        order.broker_id = order.order_id
        order.status = Order.Status.POSTED
        order.meta = "virtual posted"
        await order.setStatus(Order.Status.POSTED)

        cls.__stop_orders.append(order)

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
        await order.setStatus(Order.Status.POSTED)

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
    def createBarStream(cls, timeframe: TimeFrame) -> None:
        logger.debug(f"{cls.__name__}.createBarStream({asset}, {timeframe})")

        if not cls.__data_stream:
            cls.__data_stream = BarStream()
            cls.__data_stream.setAsset(self.__current_asset)

        cls.__data_stream.subscribe(timeframe)

    # }}}
    @classmethod  # runDataStream  # {{{
    async def runDataStream(cls):
        logger.debug(f"{cls.__name__}.runDataStream()")

        await cls.__data_stream.loadData(cls.__test.begin, cls.__test.end)

        for event in cls.__data_stream:
            if event.type == Event.Type.NEW_HISTORICAL_BAR:
                await cls.new_bar.aemit(event)
            if event.type == Event.Type.BAR_CHANGED:
                # NOTE:
                # перед приходом нового реал тайм бара, до отправки
                # этого события, проверям сначала сработку ордеров
                # в текущем реал тайм баре.
                # Суть.
                # Аккаунт выставляет ордер. Он попадаем в виртуал
                # брокера сюда в соответствующий список маркет, лимит, стоп
                # ордеров. Ставится статус - POSTED.
                # Все это происходит в ответ на предыдущий эвент -
                # Event.NEW_HISTORICAL_BAR, которые все стратегии и
                # используют сейчас. Я дожидаюсь полного завершения
                # обработки этого эвента всеми, все свои ордера поставят.
                # И только потом вот здесь - чекаю ордера.
                # В текущем реал тайм баре. То есть в том, который и был
                # на момент выставления ордеров стратегиями.
                # Смотрим сработку ордеров только на 1М таймфрейме
                # в эвенте если приходит другой таймфрейм - пропускам
                # просто отправляем его сигналом
                # А если 1М то беру бар из текущего графика, а не новый
                # из эвента.
                if event.timeframe == "1M":
                    bar = cls.__current_asset.chart("1M").now
                    await cls.__checkOrders(bar)
                # Теперь отправляем новый реал тайм бар всем.
                await cls.bar_changed.aemit(event)

    # }}}

    @classmethod  # __checkOrders  # {{{
    async def __checkOrders(cls, bar: Bar) -> None:
        logger.debug(f"{cls.__name__}.__checkOrders()")

        await cls.__checkOrdersMarket(bar)
        await cls.__checkOrdersLimit(bar)
        await cls.__checkOrdersStop(bar)

    # }}}
    @classmethod  # __checkOrdersMarket  # {{{
    async def __checkOrdersMarket(cls, bar: Bar):
        logger.debug(f"{cls.__name__}.__checkOrdersMarket()")

        i = 0
        while i < len(cls.__market_orders):
            m_order = cls.__market_orders[i]
            await cls.__executeOrder(m_order, bar.dt, bar.open)

    # }}}
    @classmethod  # __checkOrdersLimit  # {{{
    async def __checkOrdersLimit(cls, bar: Bar):
        logger.debug(f"{cls.__name__}.__checkOrdersLimit()")

        i = 0
        while i < len(cls.__limit_orders):
            order = cls.__limit_orders[i]
            if order.price in bar:
                await cls.__executeOrder(order, bar.dt, order.price)
                continue

            # если бар открылся под лимиткой на покупку -
            # выполняем лимитку по цене открытия бара
            if order.direction == Direction.BUY:
                if bar.open < order.price:
                    await cls.__executeOrder(order, bar.dt, bar.open)
                    continue

            # если бар открылся над лимиткой на продажу -
            # выполняем лимитку по цене открытия бара
            if order.direction == Direction.BUY:
                if bar.open > order.price:
                    await cls.__executeOrder(order, bar.dt, bar.open)
                    continue
            i += 1

    # }}}
    @classmethod  # __checkOrdersStop  # {{{
    async def __checkOrdersStop(cls, bar: Bar):
        logger.debug(f"{cls.__name__}.__checkOrdersStop()")

        i = 0
        while i < len(cls.__stop_orders):
            order = cls.__stop_orders[i]

            # TODO: пока не парюсь с exec_price
            # если exec_price=None - значит выполнение по рынку у stop loss
            # иначе exec_price=stop_price, не делаю тейки с разной ценой
            # активации и исполнения, понадобится - сделаю и логику их
            # выполнения, а пока чем проще тем лучше.
            if order.exec_price is not None:
                assert order.exec_price == order.stop_price
            price = order.stop_price
            if price in bar:
                await cls.__executeOrder(order, bar.dt, price)
                continue

            if order.type == Order.Type.STOP_LOSS:
                # Трейд в лонг.
                # Если цена открылась ниже стоп прайса, то стоп лосс
                # срабатывает по цене открытия бара
                if order.direction == Direction.SELL:
                    if bar.open < order.stop_price:
                        await cls.__executeOrder(order, bar.dt, bar.open)
                        continue

                # Трейд в шорт.
                # Если цена открылась выше стоп прайса, то стоп лосс
                # срабатывает по цене открытия бара
                if order.direction == Direction.BUY:
                    if bar.open > order.stop_price:
                        await cls.__executeOrder(order, bar.dt, bar.open)
                        continue

            if order.type == Order.Type.TAKE_PROFIT:
                # Трейд в лонг.
                # Если цена открылась выше стоп прайса, то тейк профит
                # срабатывает по цене открытия бара
                if order.direction == Direction.SELL:
                    if bar.open > order.stop_price:
                        await cls.__executeOrder(order, bar.dt, bar.open)
                        continue

                # Трейд в шорт.
                # Если цена открылась ниже стоп прайса, то тейк профит
                # срабатывает по цене открытия бара
                if order.direction == Direction.BUY:
                    if bar.open < order.stop_price:
                        await cls.__executeOrder(order, bar.dt, bar.open)
                        continue

            i += 1

    # }}}
    @classmethod  # __executeOrder  # {{{
    async def __executeOrder(cls, order, dt, price):
        logger.debug(f"{cls.__name__}.__executeOrder()")

        # # recognise execution price
        # match order.type:
        #     case Order.Type.MARKET:
        #         price = bar.open
        #     case Order.Type.LIMIT:
        #         price = order.price
        #     case Order.Type.STOP:
        #         price = order.stop_price
        #     case Order.Type.STOP_LOSS:
        #         price = order.stop_price
        #     case Order.Type.TAKE_PROFIT:
        #         price = order.stop_price

        # create transaction, then attach to order
        transaction = Transaction(
            order_id=order.order_id,
            dt=dt,
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
