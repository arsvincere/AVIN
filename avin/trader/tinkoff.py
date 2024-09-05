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
from datetime import datetime

import tinkoff.invest as ti
from tinkoff.invest import (
    CandleInterval,
    Client,
    MoneyValue,
    OrderDirection,
    OrderExecutionReportStatus,
    OrderType,
    PostOrderResponse,
    StopOrderDirection,
    StopOrderType,
    SubscriptionInterval,
)
from tinkoff.invest.async_services import AsyncMarketDataStreamManager
from tinkoff.invest.schemas import (
    CandleInstrument,
)
from tinkoff.invest.utils import (
    decimal_to_quotation,
    money_to_decimal,
    quotation_to_decimal,
)

from avin.core import Asset, Bar, Event, Operation, Order, TimeFrame
from avin.data import *
from avin.logger import logger
from avin.trader.abstract_broker import Broker
from avin.trader.account import Account
from avin.utils import Cmd


class Tinkoff(Broker):  # {{{
    """const"""  # {{{

    name = "Tinkoff"
    TARGET = ti.constants.INVEST_GRPC_API
    TOKEN = Cmd.read("/home/alex/AVIN/usr/connect/tinkoff/token.txt").strip()

    # }}}
    def __init__(self, trader=None):  # {{{
        logger.debug("Tinkoff.__init__()")
        Broker.__init__(self)
        self.__trader = trader
        self.__client = None
        self.__connect = False

    # }}}
    @property  # _client# {{{
    def _client(self):
        return self.__client

    # }}}
    @property  # trader# {{{
    def trader(self):
        return self.__trader

    # }}}
    async def connect(self) -> None:  # {{{
        logger.info(":: Tinkoff try to connect")

        # create task - run connection cycle
        task = asyncio.create_task(self.__runConnectionCycle())

        # wait 5 second, check flag 'self.__connect' every 1 second,
        # if connected return
        for n in range(1, 6):
            if self.__connect:
                logger.info("  - successfully connected!")
                return
            else:
                logger.info(f"  - waiting connection... ({n})")
                await asyncio.sleep(1)

        # fail to connect, cancel task and log error
        task.cancel()
        logger.error("Fail to connect Tinkoff!")
        return

    # }}}
    def disconnect(self):  # {{{
        logger.debug("Tinkoff.disconnect()")
        self.__connect = False

    # }}}
    def isConnect(self):  # {{{
        logger.debug("Tinkoff.isConnect()")
        return self.__connect

    # }}}
    async def isMarketOpen(self):  # {{{
        logger.debug("Tinkoff.isMarketOpen()")
        if not self.__connect:
            logger.error(
                "Tinkoff not connected, impossible to check is market open."
            )

        sber = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "SBER")
        status = self.__client.market_data.get_trading_status(figi=sber.figi)
        is_open = (
            status.market_order_available_flag
            and status.api_trade_available_flag
        )
        return is_open

    # }}}
    def getAllAccounts(self):  # {{{
        logger.debug("Tinkoff.getAllAccounts()")
        response = self.__client.users.get_accounts()
        logger.debug(f"Tinkoff.getAllAccounts: Response='{response}'")
        user_accounts = list()
        for tinkoff_account in response.accounts:
            acc = Account(
                name=tinkoff_account.name, broker=self, meta=tinkoff_account
            )
            user_accounts.append(acc)
        return user_accounts

    # }}}
    def getMoney(self, account: Account):  # {{{
        logger.debug(f"Tinkoff.getMoney({account.name})")
        response = self.__client.operations.get_positions(
            account_id=account.meta.id,
        )
        money = float(quotation_to_decimal(response.money[0]))
        logger.debug(f"Tinkoff.getMoney: Response='{response}'")
        logger.debug(f"Tinkoff.getMoney: UserValue='{money}'")
        return money

    # }}}
    def getLimitOrders(self, account):  # {{{
        logger.debug(f"Tinkoff.getLimitOrders({account.name})")
        response = self.__client.orders.get_orders(account_id=account.ID)
        logger.debug(f"Tinkoff.getLimitOrders: Response='{response}'")
        orders = Tinkoff._getLimitOrders(response)
        return orders

    # }}}
    def getStopOrders(self, acc):  # {{{
        logger.debug(f"Tinkoff.getStopOrders(acc={acc})")
        try:
            response = self.__client.stop_orders.get_stop_orders(
                account_id=acc.id
            )
        except tinkoff.invest.exceptions.InvestError:
            logger.error("Tinkoff.getStopOrders: Error={err}")
            return None
        logger.debug(f"Tinkoff.getStopOrders: Response='{response}'")
        orders = Tinkoff._getStopOrders(response)
        return orders

    # }}}
    def getOperations(self, acc, from_, to):  # {{{
        """Operation(
        id='R270663867',
        parent_operation_id='',
        currency='rub',
        payment=MoneyValue(currency='rub', units=-160, nano=-890000000),
        price=MoneyValue(currency='rub', units=160, nano=890000000),
        state=<OperationState.OPERATION_STATE_EXECUTED: 1>,
        quantity=1,
        quantity_rest=0,
        figi='BBG004S68CP5',
        instrument_type='share',
        date=datetime.datetime(
            2024, 7, 4, 12, 3 9, 26, 368788, tzinfo=datetime.timezone.utc
            ),
        type='Покупка ценных бумаг',
        operation_type=<OperationType.OPERATION_TYPE_BUY: 15>,
        trades=[
            OperationTrade(
            trade_id='134612622',
            date_time=datetime.datetime(
                2024, 7, 4, 12, 39, 26, 373816, tzinfo=datetime.timezone.utc
                ),
            quantity=1,
            price=MoneyValue(currency='rub', units=160, nano=890000000))
            ],
        asset_uid='fe8d49a4-3321-449b-bd08-02efbac878fe',
        position_uid='17cf2c5b-2176-4851-85e2-a638225bef88',
        instrument_uid='cf1c6158-a303-43ac-89eb-9b1db8f96043')
        """

        logger.debug(
            f"Tinkoff.getOperations(acc={acc}), from_={from_}, to={to}"
        )
        assert isinstance(from_, datetime)
        assert isinstance(to, datetime)
        response = self.__client.operations.get_operations(
            account_id=acc.id,
            from_=from_,
            to=to,
        )
        logger.debug(f"Tinkoff.getOperations: Response='{response}'")
        operations = Tinkoff._getOperations(response)
        return operations

    # }}}
    def getPositions(self, acc):  # {{{
        logger.debug(f"Tinkoff.getPositions(acc={acc})")
        response = self.__client.operations.get_positions(account_id=acc.id)
        return

        logger.debug(f"Tinkoff.getPositions: Response='{response}'")
        money = Tinkoff._getMoney(response)
        shares = Tinkoff._getShares(response)
        bounds = Tinkoff._getBounds(response)
        futures = Tinkoff._getFutures(response)
        options = Tinkoff._getOptions(response)
        portfolio = Portfolio(money, shares, bounds, futures, options)
        return portfolio

    # }}}
    def getDetailedPortfolio(self, acc):  # {{{
        logger.debug(f"Tinkoff.getDetailedPortfolio(acc={acc})")
        # короче это более подрбная версия get_positions()
        # см документацию
        response = self.__client.operations.get_portfolio(account_id=acc.id)
        logger.debug(f"Tinkoff.getDetailedPortfolio: Response='{response}'")
        return response

    # }}}
    def getWithdrawLimits(self, acc):  # {{{
        logger.debug(f"Tinkoff.getWithdrawLimits(acc={acc})")
        response = self.__client.operations.get_withdraw_limits(
            account_id=acc.id
        )
        logger.debug(f"Tinkoff.getWithdrawLimits: Response='{response}'")
        return limits

    # }}}
    def getOrderState(self, acc, order):  # {{{
        """OrderState(# {{{
        order_id='R270663867',
        execution_report_status=
            <OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL: 1>,
        lots_requested=1,
        lots_executed=1,
        initial_order_price=MoneyValue(currency='rub', units=161, nano=400000000),
        executed_order_price=MoneyValue(currency='rub', units=160, nano=890000000),
        total_order_amount=MoneyValue(currency='rub', units=160, nano=890000000),
        average_position_price=MoneyValue(currency='rub', units=160, nano=890000000),
        initial_commission=MoneyValue(currency='rub', units=0, nano=90000000),
        executed_commission=MoneyValue(currency='rub', units=0, nano=80000000),
        figi='BBG004S68CP5',
        direction=<OrderDirection.ORDER_DIRECTION_BUY: 1>,
        initial_security_price=MoneyValue(currency='rub', units=161, nano=400000000),
        stages=[
            OrderStage(
                price=MoneyValue(currency='rub', units=160, nano=890000000),
                quantity=1,
                trade_id='D134612622',
                execution_time=datetime.datetime(
                    2024, 7, 4, 12, 39, 26, 373816, tzinfo=datetime.timezone.utc)
                )
            ],
        service_commission=MoneyValue(currenc y='rub', units=290, nano=0),
        currency='rub',
        order_type=<OrderType.ORDER_TYPE_MARKET: 2>,
        order_date=datetime.datetime(
            2024, 7, 4, 12, 39, 26, 372885, tzinfo=datetime.timezone.utc),
        instrument_uid='cf1c6158-a303-43ac-89eb-9b1db8f96043',
        order_request_id='4defaa66-6545-4bcc-9f05-301adf32dfce'
        )
        """
        # }}}
        response: ti.OrderState = self.__client.orders.get_order_state(
            account_id=acc.id,
            order_id=order.broker_id,
        )
        return response

    # }}}
    def getOrderOperation(self, acc, order) -> Operation:
        response = self.getOrderState(acc, order)
        assert (
            response.execution_report_status
            == OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL
        )

        direction = (
            Operation.Direction.BUY
            if order.direction == Order.Direction.BUY
            else Operation.Direction.SELL
        )

        operation = Operation(
            account_name=acc.name,
            dt=response.order_date,
            direction=direction,
            asset_id=order.asset_id,
            lots=response.lots_executed,
            quantity=order.quantity,  # FIX: так не пойдет, надо считать
            price=float(money_to_decimal(response.average_position_price)),
            amount=float(money_to_decimal(response.total_order_amount)),
            commission=float(money_to_decimal(response.executed_commission)),
            operation_id=None,  # constructor will create new id
            order_id=order.order_id,
            trade_id=order.trade_id,
            meta=None,
        )
        print(response)

        return operation

    async def postMarketOrder(  # {{{
        self, order: Order.Market, account: Account
    ):
        # TODO: разобраться с этими ключами индемпотентности
        # ключи работают, не дают выставить ордер с тем же ключом (ид)
        # tinkoff.invest.exceptions.RequestError: (<StatusCode.INVALID_ARGUMENT: (3, 'invalid argument')>, '30057', Metadata(tracking_id='aedb2dee10e321c76f06198946b7cbf6', ratelimit_limit='300, 300;w=60', ratelimit_rema ining=299, ratelimit_reset=55, message='The order is a duplicate, but the order report was not found'))
        # но ИД нужен текст а не флоат как у меня сейчас...
        # надо будет мне свои ИДшники переделать на строки

        """Post order response example# {{{
        Response='PostOrderResponse(
            order_id='R270663867',
            execution_report_status=<OrderExecutionReportStatus.
                EXECUTION_REPORT_STATUS_FILL: 1>,
            lots_requested=1, lots _executed=1,
            initial_order_price=MoneyValue(
                currency='rub', units=161, nano=400000000
                ),
            executed_order_price=MoneyValue(
                currency='rub', units=160, nano=890000000
                ),
            total_order_amount=MoneyValue(
                currency='rub', units=160, nano=890000000
                ),
            initial_commission=MoneyValue(
                currency='rub', units=290, nano=90000000
                ),
            executed_commission=MoneyValue(
                currency='rub', units=290, nano=0
                ),
            aci_value=MoneyValue(
                currency='', units=0, nano=0
                ),
            figi='BBG004S68CP5',
            direction=<OrderDirection.ORDER_DIRECTION_BUY: 1>,
            initial_security_price=MoneyValue(
                currency='rub', units=161, nano=400000000
                ),
            order_type=<OrderType.ORDER_TYPE_MARKET: 2>,
            message='',
            initial_order_price_pt=Quotation(units=0, nano=0),
            instrument_uid='cf1c6158-a303-43ac-89eb-9b1db8f96043',
            order_request_id='',
            response_metadata=ResponseMetadata(
                tracking_id='2431d8eeb71bf472 300d096a1ea7b43e',
                server_time=datetime.datetime(
                    2024, 7, 4, 12, 39, 26, 693922, tzinfo=datetime.timezone.utc
                )
            )
        )'
        """  # }}}
        logger.debug(f"Tinkoff.postMarketOrder({order})")
        response: ti.PostOrderResponse = self.__client.orders.post_order(
            account_id=account.id,
            order_type=Tinkoff._OrderTypeFrom(order),
            direction=Tinkoff._OrderDirectionFrom(order),
            figi=order.asset_id.figi,
            quantity=order.lots,
            # order_id=order.order_id,
        )

        order.broker_id = response.order_id
        order.meta = str(response)

        oers = OrderExecutionReportStatus
        tinkoff_status = response.execution_report_status
        if tinkoff_status == oers.EXECUTION_REPORT_STATUS_FILL:
            status = Order.Status.FILLED
        elif tinkoff_status == oers.EXECUTION_REPORT_STATUS_NEW:
            status = Order.Status.POSTED
        elif tinkoff_status == oers.EXECUTION_REPORT_STATUS_REJECTED:
            status = Order.Status.REJECTED
        elif tinkoff_status == oers.EXECUTION_REPORT_STATUS_CANCELLED:
            status = Order.Status.CANCELED
        elif tinkoff_status == oers.EXECUTION_REPORT_STATUS_PARTIALLYFILL:
            status = Order.Status.PARTIAL

        # TODO: здесь неявная хуйня с генерацией
        # сигналов и обновлением в БД, нужно сделать более явно как то...
        # а то вверху присваиваю broker_id и meta напрямую полям,
        # а тут через интерфейс ордера, и подразумевая что он заодно
        # сохранится в базе, нужно более прозрачно сделать.
        result = await order.setStatus(status)

        logger.debug(f"Tinkoff.postMarketOrder: Response='{response}'")
        return order

    # }}}
    def postLimitOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.postLimitOrder({order})")
        response: PortfoliostOrderResponse = self.__client.orders.post_order(
            account_id=acc.id,
            order_type=Tinkoff._OrderTypeFrom(order),
            direction=Tinkoff._OrderDirectionFrom(order),
            instrument_id=order.asset.uid,
            quantity=order.lots,
            price=Tinkoff._QuotationFrom(order.price),
            # order_id = order.ID,  # в песочнице с ним не работает
        )
        logger.debug(f"Tinkoff.postLimitOrder: Response='{response}'")
        order.ID = response.order_id
        return response

    # }}}
    def postStopOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.postStopOrder({order})")
        try:
            response = self.__client.stop_orders.post_stop_order(
                price=Tinkoff._QuotationFrom(order.exec_price),
                quantity=order.lots,
                direction=Tinkoff._OrderDirectionFrom(order),
                account_id=acc.id,
                stop_price=Tinkoff._QuotationFrom(order.stop_price),
                # expire_date=
                instrument_id=order.asset.uid,
                expiration_type=Tinkoff._expirationTypeFrom(order),
                stop_order_type=Tinkoff._OrderTypeFrom(order),
                # order_id = order.ID,  # в песочнице с ним не работает
            )
        except tinkoff.invest.exceptions.RequestError as err:
            logger.error(f"{err}")
            return False
        order.ID = response.stop_order_id
        logger.debug(f"Tinkoff.postStopOrder: Response='{response}'")
        return response

    # }}}
    def cancelLimitOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.cancelLimitOrder(acc={acc}, order={order})")
        response = self.__client.orders.cancel_order(
            account_id=acc.id,
            order_id=order.ID,
        )
        logger.debug(f"Tinkoff.cancelLimitOrder: Response='{response}'")
        return response

    # }}}
    def cancelStopOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.cancelStopOrder(acc={acc}, order={order})")
        response = self.__client.stop_orders.cancel_stop_order(
            account_id=acc.id,
            stop_order_id=order.ID,
        )
        logger.debug(f"Tinkoff.cancelStopOrder: Response='{response}'")
        return response

    # }}}
    def createDataStream(self):  # {{{
        logger.debug("Tinkoff.createDataStream()")
        stream = self.__client.create_market_data_stream()
        return stream

    # }}}
    def addSubscription(self, stream, asset, timeframe):  # {{{
        logger.debug("Tinkoff.createSubscription()")
        figi = asset.figi
        interval = Tinkoff._SubscriptionIntervalFrom(timeframe)
        candle_subscription = CandleInstrument(figi=figi, interval=interval)
        stream.candles.waiting_close().subscribe([candle_subscription])

    # }}}
    def checkStream(self, stream: AsyncMarketDataStreamManager):  # {{{
        logger.debug("async Tinkoff.checkStream()")
        it = iter(stream)
        response = next(stream)
        logger.debug(f"  - async Tinkoff.checkStream: Response='{response}'")

    # }}}
    def waitEvent(self, stream: AsyncMarketDataStreamManager):  # {{{
        logger.debug("async Tinkoff.waitEvent()")
        response = next(stream)
        logger.debug(f"  Tinkoff.waitEvent: Response='{response}'")
        if response.candle:
            figi = response.candle.figi
            timeframe = Tinkoff._toTimeFrame(response.candle.interval)
            bar = Tinkoff._toBar(response.candle, Bar)
            event = Event.NewBar(figi, timeframe, bar)
            return event
        else:
            return None

    # }}}

    def createOrderStream(self, account: Account):  # {{{
        logger.debug("Tinkoff.createOrderStream()")
        stream = self.__client.orders_stream.trades_stream(
            accounts=[
                account.meta.id,
            ]
        )
        return stream

    """
    TradesStreamResponse(
        order_trades=None,
        ping=Ping(
            time=datetime.datetime(
                2024, 7, 6, 7, 10, 37, 722397, tzinfo=datetime.timezone.utc
                ),
            stream_id=''
            )
        )

    TradesStreamResponse(
        order_trades=OrderTrades(
            order_id='REX01J23E4ER3JF63SBD',
            created_at=datetime.datetime(
                2024, 7, 6, 7, 11, 33, 268625, tzinfo=datetime.timezone.utc
                ),
            direction=<OrderDirection.ORDER_DIRECTION_SELL: 2>,
            figi='BBG004730N88',
            trades=[
                OrderTrade(
                    date_time=datetime.datetime(
                        2024, 7, 6, 7, 11, 31, 663280, tzinfo=datetime.timezone.utc
                        ),
                    price=Quotation(units=325, nano=50000000),
                    quantity=10,
                    trade_id='DEX01J23E4ESXAKQ5AQA')],
                    account_id='2000566238',
                    instrument_uid='e6123145-9665-43e0-8413-cd61b8aa9b13'
                    ),
        ping=None
        )
    """

    # }}}
    def createPositionSteam(self, account: Account):  # {{{
        logger.debug("Tinkoff.createOrderStream()")
        stream = self.__client.operations_stream.positions_stream(
            accounts=[
                account.meta.id,
            ]
        )
        return stream

    """ PositionsStreamResponse(
    subscriptions=PositionsSubscriptionResult(
        accounts=[PositionsSubscriptionStatus(
        account_id='2000566238',
        subscription_status=
            <PositionsAccountSubscriptionStatus.POSITIONS_SUBSCRIPTION_STATUS_SUCCESS: 1>
        )]),
        position=None,
        ping=None
        )
    PositionsStreamResponse(subscriptions=None, position=PositionData(account_id='2000566238',
    money=[PositionsMoney(available_value=MoneyValue(currency='rub', units=640, nano=680000000)
    , blocked_value=MoneyValue(currency='rub', units=158, nano=480000000))], securities=[], fut
    ures=[], options=[], date=datetime.datetime(2024, 7, 6, 7, 3, 21, 929869, tzinfo=datetime.t
    imezone.utc)), ping=None)

    PositionsStreamResponse(subscriptions=None, position=PositionData(account_id='2000566238',
    money=[PositionsMoney(available_value=MoneyValue(currency='rub', units=641, nano=180000000)
    , blocked_value=MoneyValue(currency='rub', units=0, nano=80000000))], securities=[Positions
    Securities(figi='BBG004S68CP5', blocked=0, balance=1, position_uid='17cf2c5b-2176-4851-85e2
    -a638225bef88', instrument_uid='cf1c6158-a303-43ac-89eb-9b1db8f96043', exchange_blocked=Fal
    se, instrument_type='share')], futures=[], options=[], date=datetime.datetime(2024, 7, 6, 7
    , 3, 22, 114877, tzinfo=datetime.timezone.utc)), ping=None)

    PositionsStreamResponse(subscriptions=None, position=PositionData(account_id='2000566238',
    money=[PositionsMoney(available_value=MoneyValue(currency='rub', units=641, nano=260000000)
    , blocked_value=MoneyValue(currency='rub', units=0, nano=0))], securities=[], futures=[], o
    ptions=[], date=datetime.datetime(2024, 7, 6, 7, 3, 22, 364311, tzinfo=datetime.timezone.ut
    c)), ping=None)

    PositionsStreamResponse(subscriptions=None, position=PositionData(account_id='2000566238',
    money=[PositionsMoney(available_value=MoneyValue(currency='rub', units=641, nano=180000000)
    , blocked_value=MoneyValue(currency='rub', units=0, nano=0))], securities=[], futures=[], o
    ptions=[], date=datetime.datetime(2024, 7, 6, 7, 3, 22, 373359, tzinfo=datetime.timezone.ut
    c)), ping=None)
    """
    # }}}

    async def __runConnectionCycle(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.connect()")
        with Client(self.TOKEN, target=self.TARGET) as client:
            response = client.users.get_accounts()
            if response:
                self.__client = client
                self.__connect = True
                while self.__connect:
                    await asyncio.sleep(1)

        self.__client = None
        self.__connect = False
        logger.info("Tinkoff disconnected")

    # }}}
    @staticmethod  # _CandleIntervalFrom# {{{
    def _CandleIntervalFrom(
        timeframe: TimeFrame,
    ) -> tinkoff.invest.CandleInterval:
        intervals = {
            "1M": CandleInterval.CANDLE_INTERVAL_1_MIN,
            "5M": CandleInterval.CANDLE_INTERVAL_5_MIN,
            "1H": CandleInterval.CANDLE_INTERVAL_HOUR,
            "D": CandleInterval.CANDLE_INTERVAL_DAY,
            "W": CandleInterval.CANDLE_INTERVAL_WEEK,
            "M": CandleInterval.CANDLE_INTERVAL_MONTH,
        }
        return intervals[str(timeframe)]

    # }}}
    @staticmethod  # _SubscriptionIntervalFrom# {{{
    def _SubscriptionIntervalFrom(
        timeframe: TimeFrame,
    ) -> tinkoff.invest.SubscriptionInterval:
        intervals = {
            "1M": SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
            "5M": SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIVE_MINUTES,
            "1H": SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_HOUR,
            "D": SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_DAY,
            "W": SubscriptionInterval.SUBSCRIPTION_INTERVAL_WEEK,
            "M": SubscriptionInterval.SUBSCRIPTION_INTERVAL_MONTH,
        }
        return intervals[str(timeframe)]

    # }}}
    @staticmethod  # _OrderTypeFrom# {{{
    def _OrderTypeFrom(order: Order):
        ot = ti.OrderType
        sot = ti.StopOrderType

        if order.type == Order.Type.MARKET:
            return ot.ORDER_TYPE_MARKET
        if order.type == Order.Type.LIMIT:
            return ot.ORDER_TYPE_LIMIT
        if order.type == Order.Type.STOP_LOSS:
            return sot.STOP_ORDER_TYPE_STOP_LOSS
        if order.type == Order.Type.TAKE_PROFIT:
            return sot.STOP_ORDER_TYPE_TAKE_PROFIT

        if order.type == Order.Type.STOP:
            current_price = Tinkoff.getLastPrice(order.asset)
            if order.direction == Order.Direction.BUY:
                if current_price >= order.price:
                    return sot.STOP_ORDER_TYPE_TAKE_PROFIT
                if current_price < order.price:
                    return sot.STOP_ORDER_TYPE_STOP_LOSS
            elif order.direction == Order.Direction.SELL:
                if current_price <= order.price:
                    return sot.STOP_ORDER_TYPE_TAKE_PROFIT
                if current_price > order.price:
                    return sot.STOP_ORDER_TYPE_STOP_LOSS

    # }}}
    @staticmethod  # _OrderDirectionFrom# {{{
    def _OrderDirectionFrom(order: Order):
        if order.type in (Order.Type.MARKET, Order.Type.LIMIT):
            if order.direction == Order.Direction.BUY:
                return ti.OrderDirection.ORDER_DIRECTION_BUY
            if order.direction == Order.Direction.SELL:
                return ti.OrderDirection.ORDER_DIRECTION_SELL
            return ti.OrderDirection.ORDER_DIRECTION_UNSPECIFIED

        if order.type in (
            Order.Type.STOP_LOSS,
            Order.Type.TAKE_PROFIT,
            Order.Type.STOP,
            Order.Type.WAIT,
        ):
            if order.direction == Order.Direction.BUY:
                return ti.StopOrderDirection.STOP_ORDER_DIRECTION_BUY
            if order.direction == Order.Direction.SELL:
                return ti.StopOrderDirection.STOP_ORDER_DIRECTION_SELL
            return StopOrderDirection.STOP_ORDER_DIRECTION_UNSPECIFIED

    # }}}
    @staticmethod  # _QuotationFrom# {{{
    def _QuotationFrom(price: float):
        if price is None:
            return None
        else:
            quotation = decimal_to_quotation(Decimal(price))
            return quotation

    # }}}
    @staticmethod  # _expirationTypeFrom# {{{
    def _expirationTypeFrom(order: Order):
        if order.type == Order.Type.MARKET:
            return None
        if order.type == Order.Type.LIMIT:
            return None
        if order.type == Order.Type.STOP:
            return ti.StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL
        if order.type == Order.Type.TAKE:
            return ti.StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL

    # }}}
    @staticmethod  # _toTimeFrame# {{{
    def _toTimeFrame(tinkoff_interval) -> TimeFrame:
        si = SubscriptionInterval
        ci = CandleInterval
        if isinstance(tinkoff_interval, SubscriptionInterval):
            intervals = {
                si.SUBSCRIPTION_INTERVAL_ONE_MINUTE: "1M",
                si.SUBSCRIPTION_INTERVAL_FIVE_MINUTES: "5M",
                si.SUBSCRIPTION_INTERVAL_ONE_HOUR: "1H",
                si.SUBSCRIPTION_INTERVAL_ONE_DAY: "D",
                si.SUBSCRIPTION_INTERVAL_WEEK: "W",
                si.SUBSCRIPTION_INTERVAL_MONTH: "M",
            }
            string = intervals[tinkoff_interval]
        elif isinstance(tinkoff_interval, CandleInterval):
            intervals = {
                ci.CANDLE_INTERVAL_1_MIN: "1M",
                ci.CANDLE_INTERVAL_5_MIN: "5M",
                ci.CANDLE_INTERVAL_HOUR: "1H",
                ci.CANDLE_INTERVAL_DAY: "D",
                ci.CANDLE_INTERVAL_WEEK: "W",
                ci.CANDLE_INTERVAL_MONTH: "M",
            }
            string = intervals[tinkoff_interval]
        else:
            assert False, "unknow interval type '{type(tinkoff_interval)}'"
        return TimeFrame(string)

    # }}}
    @staticmethod  # _toBar# {{{
    def _toBar(candle, constructor) -> Bar:
        opn = float(quotation_to_decimal(candle.open))
        cls = float(quotation_to_decimal(candle.close))
        hgh = float(quotation_to_decimal(candle.high))
        low = float(quotation_to_decimal(candle.low))
        vol = candle.volume
        dt = candle.time
        bar = constructor(dt, opn, hgh, low, cls, vol)
        return bar

    # }}}
    @staticmethod  # _getOperationAsset# {{{
    def _getOperationAsset(tinkoff_operation: ti.Operation):
        typ = tinkoff_operation.instrument_type
        if typ == "share":
            asset = Asset.byUid(
                exchange=Exchange.MOEX,
                asset_type=AssetType.Share,
                uid=tinkoff_operation.instrument_uid,
            )
            return asset

        assert False, "Тестировались только акции, не '{typ}'"

    # }}}
    @staticmethod  # _getOperationDirection# {{{
    def _getOperationDirection(tinkoff_operation: ti.Operation):
        if (
            tinkoff_operation.operation_type
            == ti.OperationType.OPERATION_TYPE_BUY
        ):
            return Operation.Direction.BUY
        if (
            tinkoff_operation.operation_type
            == ti.OperationType.OPERATION_TYPE_SELL
        ):
            return Operation.Direction.SELL

    # }}}
    @staticmethod  # _getOperations# {{{
    def _getOperations(response: ti.OperationsResponse):
        operations = list()
        for i in response.operations:
            if i.operation_type in (
                ti.OperationType.OPERATION_TYPE_BUY,
                ti.OperationType.OPERATION_TYPE_SELL,
            ):
                asset = Tinkoff._getOperationAsset(i)
                op = Operation(
                    dt=i.date,
                    direction=Tinkoff._getOperationDirection(i),
                    asset=asset,
                    lots=int(i.quantity / asset.lot),
                    quantity=i.quantity,
                    price=float(money_to_decimal(i.price)),
                    amount=abs(float(money_to_decimal(i.payment))),
                    commission=0,
                    meta=i,
                )
                operations.append(op)
        return operations

    # }}}
    @staticmethod  # _getMoney# {{{
    def _getMoney(response: ti.PositionsResponse):
        money = list()
        for i in response.money:
            currency = i.currency
            val = float(money_to_decimal(i))
            block = None
            cash = Portfolio.Cash(currency, val, block)
            money.append(cash)
        return money

    # }}}
    @staticmethod  # _getShares# {{{
    def _getShares(response: ti.PositionsResponse):
        shares = list()
        for i in response.securities:
            if i.instrument_type != "share":
                continue
            figi = i.figi
            asset = Asset.assetByFigi(figi)
            balance = i.balance
            block = i.blocked
            ID = i.position_uid
            s = Portfolio.Share(asset, balance, block, ID, i)
            shares.append(s)
        return shares

    # }}}
    @staticmethod  # _getBounds# {{{
    def _getBounds(response: ti.PositionsResponse):
        return list()

    # }}}
    @staticmethod  # _getFutures# {{{
    def _getFutures(response: ti.PositionsResponse):
        return list()

    # }}}
    @staticmethod  # _getOptions# {{{
    def _getOptions(response: ti.PositionsResponse):
        return list()

    # }}}
    @staticmethod  # _getOrderAsset# {{{
    def _getOrderAsset(response: ti.OrderState):
        figi = response.figi
        asset = TinkoffId.assetByFigi(figi)
        return asset

    # }}}
    @staticmethod  # _getOrderType# {{{
    def _getOrderType(response: ti.OrderState):
        ot = OrderType
        sot = StopOrderType
        types = {
            "ORDER_TYPE_UNSPECIFIED": Order.Type.UNDEFINE,
            "ORDER_TYPE_LIMIT": Order.Type.LIMIT,
            "ORDER_TYPE_MARKET": Order.Type.MARKET,
            "ORDER_TYPE_BESTPRICE": Order.Type.MARKET,
            "STOP_ORDER_TYPE_UNSPECIFIED": Order.Type.UNDEFINE,
            "STOP_ORDER_TYPE_TAKE_PROFIT": Order.Type.TAKE_PROFIT,
            "STOP_ORDER_TYPE_STOP_LOSS": Order.Type.STOP_LOSS,
            "STOP_ORDER_TYPE_STOP_LIMIT": Order.Type.STOP,
        }
        tinkoff_order_type = response.order_type.name
        avin_type = types[tinkoff_order_type]
        return avin_type

    # }}}
    @staticmethod  # _getOrderDirection# {{{
    def _getOrderDirection(response: ti.OrderState):
        od = OrderDirection
        sod = StopOrderDirection
        directions = {
            "ORDER_DIRECTION_UNSPECIFIED": Order.Direction.UNDEFINE,
            "ORDER_DIRECTION_BUY": Order.Direction.BUY,
            "ORDER_DIRECTION_SELL": Order.Direction.SELL,
            "STOP_ORDER_DIRECTION_UNSPECIFIED": Order.Direction.UNDEFINE,
            "STOP_ORDER_DIRECTION_BUY": Order.Direction.BUY,
            "STOP_ORDER_DIRECTION_SELL": Order.Direction.SELL,
        }
        tinkoff_order_direction = response.direction.name
        avin_direction = directions[tinkoff_order_direction]
        return avin_direction

    # }}}
    @staticmethod  # _getLimitOrderStatus# {{{
    def _getLimitOrderStatus(response: ti.OrderState):
        oers = OrderExecutionReportStatus
        statuses = {
            oers.EXECUTION_REPORT_STATUS_UNSPECIFIED: Order.Status.UNDEFINE,
            oers.EXECUTION_REPORT_STATUS_FILL: Order.Status.FILL,
            oers.EXECUTION_REPORT_STATUS_REJECTED: Order.Status.REJECT,
            oers.EXECUTION_REPORT_STATUS_CANCELLED: Order.Status.CANCEL,
            oers.EXECUTION_REPORT_STATUS_NEW: Order.Status.POST,
            oers.EXECUTION_REPORT_STATUS_PARTIALLYFILL: Order.Status.PARTIAL,
        }
        tinkoff_status = response.execution_report_status
        avin_status = statuses[tinkoff_status]
        return avin_status

    # }}}
    @staticmethod  # _getLimitOrderPrice# {{{
    def _getLimitOrderPrice(response: ti.OrderState):
        money_value = response.initial_security_price
        price = float(money_to_decimal(money_value))
        return price

    # }}}
    @staticmethod  # _getStopOrderActivationPrice# {{{
    def _getStopOrderActivationPrice(response: ti.StopOrder):
        money_value = response.stop_price
        price = float(money_to_decimal(money_value))
        return price

    # }}}
    @staticmethod  # _getOrderAsset# {{{
    def _getOrderCommission(response: ti.OrderState):
        money_value = response.initial_commission
        commission = float(money_to_decimal(money_value))
        return commission

    # }}}
    @staticmethod  # _getOrderExecPrice# {{{
    def _getOrderExecPrice(response: ti.OrderState):
        money_value = response.executed_order_price
        price = float(money_to_decimal(money_value))
        if price:
            return price
        else:
            return None

    # }}}
    @staticmethod  # _getLimitOrders# {{{
    def _getLimitOrders(response: ti.GetOrdersResponse):
        orders = list()
        for i in response.orders:
            order = Order(
                signal=None,
                type=Tinkoff._getOrderType(i),
                direction=Tinkoff._getOrderDirection(i),
                asset=Tinkoff._getOrderAsset(i),
                lots=i.lots_requested,
                price=Tinkoff._getLimitOrderPrice(i),
                exec_price=Tinkoff._getOrderExecPrice(i),
                timeout=None,
                status=Tinkoff._getLimitOrderStatus(i),
                ID=i.order_id,
                commission=Tinkoff._getOrderCommission(i),
            )
            orders.append(order)
        return orders

    # }}}
    @staticmethod  # _getStopOrders# {{{
    def _getStopOrders(response: ti.GetOrdersResponse):
        orders = list()
        for i in response.stop_orders:
            order = Order(
                signal=None,
                type=Tinkoff._getOrderType(i),
                direction=Tinkoff._getOrderDirection(i),
                asset=Tinkoff._getOrderAsset(i),
                lots=i.lots_requested,
                price=Tinkoff._getStopOrderActivationPrice(i),
                exec_price="unspecified",
                timeout=None,
                status=Order.Status.POST,
                ID=i.stop_order_id,
                commission="unspecified",
            )
            orders.append(order)
        return orders

    # }}}
    @staticmethod  # getHistoricalBars# {{{
    def getHistoricalBars(asset, timeframe, begin, end) -> list[Bar]:
        logger.debug(f"Tinkoff.getHistoricalBars({asset.ticker})")
        new_bars = list()
        with Client(Tinkoff.TOKEN_FULL) as client:
            try:
                candles = client.get_all_candles(
                    figi=asset.figi,
                    from_=begin,
                    to=end,
                    interval=Tinkoff._CandleIntervalFrom(timeframe),
                )
                for candle in candles:
                    if candle.is_complete:
                        bar = Tinkoff._toBar(candle)
                        new_bars.append(bar)
            except ti.exceptions.RequestError as err:
                tracking_id = err.metadata.tracking_id if err.metadata else ""
                logger.error(
                    f"Tracking_id={tracking_id}, "
                    f"code={err.code}"
                    f"RequestError={err}"
                )
                return None
            return new_bars

    # }}}
    @staticmethod  # getLastPrice# {{{
    def getLastPrice(asset) -> float:
        with Client(Tinkoff.TOKEN_FULL) as client:
            try:
                response = client.market_data.get_last_prices(
                    figi=[
                        asset.figi,
                    ]
                )
                last_price = response.last_prices[0].price
                last_price = float(quotation_to_decimal(last_price))
            except ti.exceptions.RequestError as err:
                tracking_id = err.metadata.tracking_id if err.metadata else ""
                logger.error(
                    f"Tracking_id={tracking_id}, "
                    f"code={err.code}, "
                    f"RequestError={errcode}"
                )
                return None
            return last_price

    # }}}


# }}}
class Sandbox(Tinkoff):  # {{{
    """const"""  # {{{

    TARGET = ti.constants.INVEST_GRPC_API_SANDBOX
    TOKEN = Cmd.read("/home/alex/AVIN/usr/connect/tinkoff/token.txt").strip()

    # }}}
    def __init__(self, trader=None):  # {{{
        Tinkoff.__init__(self, trader)
        # }}}

    async def connect(self, token):  # {{{
        logger.debug("Tinkoff.activate()")
        with Client(token, target=INVEST_GRPC_API_SANDBOX) as client:
            self._client = client
            self._connect = True
            while self._connect:
                await asyncio.sleep(1)
            # after close connection
            print("after close connection!")
            ...

    # }}}
    def openAccount(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.openAccount()")
        sandbox_account = self._client.sandbox.open_sandbox_account()
        logger.info("Sandbox add new account 'sandbox_account'")
        return sandbox_account

    # }}}
    def closeAccount(self, acc):  # {{{
        logger.info(f"Sandbox: close account id={acc.id}")
        self._client.sandbox.close_sandbox_account(account_id=acc.id)

    # }}}
    def closeAllSandboxAccounts(self):  # {{{
        logger.info("Sandbox: close all accounts")
        for acc in self.sandbox_accounts.accounts:
            self._client.sandbox.close_sandbox_account(account_id=acc.id)

    # }}}
    def addMoney(self, acc, money, currency="rub"):  # {{{
        logger.info(f"Sandbox: add money '{money} {currency}'")
        money = decimal_to_quotation(Decimal(money))
        amount = MoneyValue(
            units=money.units, nano=money.nano, currency=currency
        )
        self._client.sandbox.sandbox_pay_in(
            account_id=acc.id,
            amount=amount,
        )

    # }}}
    def postMarketOrder(self, order, acc):  # {{{
        logger.debug(f"Sandbox.postMarketOrder({order})")
        d = Tinkoff._OrderDirectionFrom(order)
        response: PostOrderResponse = self._client.orders.post_order(
            account_id=acc.id,
            order_type=Tinkoff._OrderTypeFrom(order),
            direction=Tinkoff._OrderDirectionFrom(order),
            instrument_id=order.asset.uid,
            quantity=order.lots,
            # price =  # для market не указываем
            # order_id = order.uid,  # в песочнице с ним не работает
        )
        logger.debug(f"Sandbox.postMarketOrder: Response='{response}'")
        return response

    # }}}
    def postLimitOrder(self, order, acc):  # {{{
        logger.debug(f"Sandbox.postLimitOrder({order})")
        response: PortfoliostOrderResponse = self._client.orders.post_order(
            account_id=acc.id,
            order_type=Tinkoff._OrderTypeFrom(order),
            direction=Tinkoff._OrderDirectionFrom(order),
            instrument_id=order.asset.uid,
            quantity=order.lots,
            price=Tinkoff._QuotationFrom(order.price),
            # order_id = order.uid,  # в песочнице с ним не работает
        )
        logger.debug(f"Sandbox.postLimitOrder: Response='{response}'")
        return response

    # }}}
    def postStopOrder(self, order, acc):  # {{{
        logger.debug(f"Sandbox.postStopOrder({order})")
        response = self._client.stop_orders.post_stop_order(
            # price = Tinkoff._QuotationFrom(order.exec_price),
            quantity=order.lots,
            direction=Tinkoff._OrderDirectionFrom(order),
            account_id=acc.id,
            stop_price=Tinkoff._QuotationFrom(order.price),
            # expire_date =
            instrument_id=order.asset.uid,
            expiration_type=Tinkoff._expirationTypeFrom(order),
            stop_order_type=Tinkoff._OrderTypeFrom(order),
        )
        logger.debug(f"Sandbox.postStopOrder: Response='{response}'")
        return response

    # }}}


# }}}
