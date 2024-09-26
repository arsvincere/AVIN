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
from decimal import Decimal
from typing import Any, AsyncIterable, ClassVar, Optional

import tinkoff.invest as ti
from grpc import StatusCode
from tinkoff.invest.utils import (
    decimal_to_quotation,
    money_to_decimal,
    quotation_to_decimal,
)

from avin.config import Usr
from avin.core import (
    Account,
    Asset,
    Bar,
    Broker,
    Id,
    LimitOrder,
    NewBarEvent,
    Operation,
    Order,
    StopLoss,
    StopOrder,
    TakeProfit,
    TimeFrame,
    TransactionEvent,
)
from avin.data import AssetType, Exchange, InstrumentId
from avin.exceptions import BrokerError
from avin.utils import AsyncSignal, Cmd, logger


class Tinkoff(Broker):
    name = "Tinkoff"
    TARGET = ti.constants.INVEST_GRPC_API
    TOKEN = Cmd.read(Usr.TINKOFF_TOKEN).strip()

    new_bar = AsyncSignal(NewBarEvent)
    new_transaction = AsyncSignal(TransactionEvent)

    __accounts: list[Account] = list()

    __connect_cycle: Optional[asyncio.Task] = None
    __connect_cycle_is_active = False
    __connect: Optional[ti.async_services.AsyncServices] = None

    __data_cycle: Optional[asyncio.Task] = None
    __data_cycle_is_active = False
    __data_stream: Optional[
        ti.async_services.AsyncMarketDataStreamManager
    ] = None
    __data_subscriptions: list[ti.CandleInstrument] = list()

    __transaction_cycle: Optional[asyncio.Task] = None
    __transaction_cycle_is_active = False
    __transaction_stream: Optional[AsyncIterable[ti.TradesStreamResponse]] = (
        None
    )

    @classmethod  # isConnect  # {{{
    def isConnect(cls) -> bool:
        logger.debug("Tinkoff.isConnect()")
        return cls.__connect_cycle_is_active

    # }}}
    @classmethod  # connect   # {{{
    async def connect(cls) -> bool:
        if cls.__connect_cycle_is_active:
            return True

        logger.info("  Tinkoff try to connect")
        cls.__connect_cycle = asyncio.create_task(cls.__connectionCycle())

        seconds_elapsed = 0
        while not cls.__connect_cycle_is_active:
            logger.info(f"  - waiting connection... ({seconds_elapsed} sec)")
            await asyncio.sleep(1)
            seconds_elapsed += 1
            if seconds_elapsed == 5:
                cls.__connect_cycle.cancel()
                logger.error("  - fail to connect Tinkoff :(")
                return False

        logger.info("  - successfully connected!")
        return True

    # }}}
    @classmethod  # disconnect  # {{{
    async def disconnect(cls) -> None:
        logger.debug("Tinkoff.disconnect()")

        await cls.stopDataStream()
        await cls.stopTransactionStream()

        if cls.__connect_cycle:
            cls.__connect_cycle.cancel()
            cls.__connect = None
            cls.__connect_cycle_is_active = False

            cls.__accounts.clear()

            logger.info(":: Tinkoff disconnected!")

    # }}}
    @classmethod  # isMarketOpen  # {{{
    async def isMarketOpen(cls) -> bool:
        logger.debug("Tinkoff.isMarketOpen()")
        assert cls.__connect is not None

        if not cls.__connect_cycle_is_active:
            logger.error(
                "Tinkoff not connected, impossible to check is market open."
            )
            return False

        sber = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "SBER")

        response = await cls.__connect.market_data.get_trading_status(
            figi=sber.figi
        )
        logger.debug(f"Tinkoff.isMarketOpen: Response='{response}'")

        return (
            response.market_order_available_flag
            and response.api_trade_available_flag
        )

    # }}}
    @classmethod  # getAccount  # {{{
    async def getAccount(cls, account_name: str) -> Account | None:
        # If you have never requested accounts, then request now
        if not cls.__accounts:
            await cls.getAllAccounts()

        # find 'account_name' & return it
        for account in cls.__accounts:
            if account.name == account_name:
                return account

        # return None if not found
        return None

    # }}}
    @classmethod  # getAllAccounts  # {{{
    async def getAllAccounts(cls) -> list[Account]:
        logger.debug("Tinkoff.getAllAccounts()")
        assert cls.__connect is not None

        if cls.__accounts:
            return cls.__accounts

        # request tinkoff accounts
        response = await cls.__connect.users.get_accounts()
        logger.debug(f"Tinkoff.getAllAccounts: Response='{response}'")

        # create list of avin.core.Account objects
        cls.__accounts = list()
        for tinkoff_account in response.accounts:
            acc = Account(tinkoff_account.name, cls, tinkoff_account)
            cls.__accounts.append(acc)

        return cls.__accounts

    # }}}
    @classmethod  # getMoney  # {{{
    async def getMoney(cls, account: Account) -> float:
        """Response example# {{{
        PositionsResponse(
            money=[
                MoneyValue(currency='rub', units=24473, nano=940000000)
                ],
            blocked=[],
            securities=[],
            limits_loading_in_progress=False,
            futures=[],
            options=[]
        )
        """  # }}}
        logger.debug(f"Tinkoff.getMoney({account.name})")
        assert cls.__connect is not None

        response: ti.PositionsResponse = (
            await cls.__connect.operations.get_positions(
                account_id=account.meta.id,
            )
        )
        logger.debug(f"Tinkoff.getMoney: Response='{response}'")

        # FIX: надо сделать свой класс Cash где нормально хранить
        # тоже currency, units, nano. И здесь
        # response.money[0]
        # работает только пока на счете из валют лежат только рубли
        money = float(money_to_decimal(response.money[0]))
        return money

    # }}}
    @classmethod  # getLimitOrders  # {{{
    async def getLimitOrders(cls, account: Account) -> list[LimitOrder]:
        """Response example# {{{
        GetOrdersResponse(
            orders=[
                OrderState(
                    order_id='51985347692',
                    execution_report_status=\
                        <OrderExecutionReportStatus.\
                        EXECUTION_REPORT_STATUS_NEW: 4>,
                    lots_requested=1,
                    lots_executed=0,
                    initial_order_price=MoneyValue(
                        currency='rub', units=91, nano=600000000
                    ),
                    executed_order_price=MoneyValue(
                        currency='rub', units=0, nano=0
                    ),
                    total_order_amount=MoneyValue(
                        currency='rub', units=91, nano=600000000
                    ),
                    average_position_price=MoneyValue(
                        currency='rub', units=0, nano=0
                    ),
                    initial_commission=MoneyValue(
                        currency='rub', units=0, nano=50000000),
                    executed_commission=MoneyValue(
                        currency='rub', units=0, nano=0
                    ),
                    figi='BBG004S68CP5',
                    direction=<OrderDirection.ORDER_DIRECTION_BUY: 1>,
                    initial_security_price=MoneyValue(
                        currency='rub', units=91, nano=599999999
                    ),
                    stages=[],
                    service_commission=MoneyValue(
                        currency='rub', units=0, nano=0
                    ),
                    currency='rub',
                    order_type=<OrderType.ORDER_TYPE_LIMIT: 1>,
                    order_date=datetime.datetime(
                        2024, 9, 9, 9, 28, 47, 379411,
                        tzinfo=datetime.timezone.utc
                    ),
                    instrument_uid='cf1c6158-a303-43ac-89eb-9b1db8f96043',
                    order_request_id='1725874127.0692253'
                )
            ]
        )
        """  # }}}
        logger.debug(f"Tinkoff.getLimitOrders({account.name})")
        assert cls.__connect is not None

        response: ti.GetOrdersResponse = (
            await cls.__connect.orders.get_orders(account_id=account.meta.id)
        )
        logger.debug(f"Tinkoff.getLimitOrders: Response='{response}'")

        orders = list()
        for i in response.orders:
            asset_id = await InstrumentId.byFigi(i.figi)
            await asset_id.cacheInfo()
            order = LimitOrder(
                account_name=account.name,
                direction=cls.__ti_to_av(i.direction),
                asset_id=asset_id,
                lots=i.lots_requested,
                quantity=i.lots_requested * asset_id.lot,
                price=cls.__ti_to_av(i.initial_order_price),
                status=cls.__ti_to_av(i.execution_report_status),
                order_id=Id.fromStr(i.order_request_id),
                trade_id=None,
                exec_lots=i.lots_executed,
                exec_quantity=i.lots_executed * asset_id.lot,
                meta=str(response),
                broker_id=i.order_id,
                transactions=list(),  # TODO: transactions
            )
            orders.append(order)
        return orders

    # }}}
    @classmethod  # getStopOrders  # {{{
    async def getStopOrders(cls, account: Account) -> list[StopOrder]:
        """Response example# {{{
        GetStopOrdersResponse(
            stop_orders=[
                StopOrder(
                    stop_order_id='5dfa66c8-090e-4594-9bac-5a3eef0a0873',
                    lots_requested=1,
                    figi='BBG004S68CP5',
                    direction=
                        <StopOrderDirection.STOP_ORDER_DIRECTION_BUY: 1>,
                    currency='rub',
                    order_type=<StopOrderType.STOP_ORDER_TYPE_TAKE_PROFIT: 1>,
                    create_date=datetime.datetime(
                        2024, 9, 9, 14, 46, 56, 6253,
                        tzinfo=datetime.timezone.utc
                    ),
                    activation_date_time=datetime.datetime(
                        1970, 1, 1, 0, 0,
                        tzinfo=datetime.timezone.utc
                    ),
                    expiration_time=datetime.datetime(
                        1970, 1, 1, 0, 0,
                        tzinfo=datetime.timezone.utc
                        ),
                    price=MoneyValue(
                        currency='rub', units=90, nano=400000000
                    ),
                    stop_price=MoneyValue(
                        currency='rub ', units=90, nano=400000000
                    ),
                    instrument_uid='cf1c6158-a303-43ac-89eb-9b1db8f96043',
                    take_profit_type=
                        <TakeProfitType.TAKE_PROFIT_TYPE_REGULAR: 1>,
                    trailing_data=StopOrderTrailingData(
                        indent=Quotation(units=0, nano=0),
                        indent_type=
                            <TrailingValueType.TRAILING_VALUE_UNSPECIFIED: 0>,
                        spread=Quotation(units=0, nano=0),
                        spread_type=
                            <TrailingValueType.TRAILING_VALUE_UNSPECIFIED: 0>,
                        status=
                            <TrailingStopStatus.TRAILING_STOP_UNSPECIFIED: 0>,
                    price=Quotation(units=0, nano=0),
                    extr=Quotation(units=0, nano=0)),
                    status=
                        <StopOrderStatusOption.STOP_ORDER_STATUS_ACTIVE: 2>,
                    exchange_order_type=
                        <ExchangeOrderType.EXCHANGE_ORDER_TYPE_LIMIT: 2>,
                    exchange_order_id=None
                )
            ]
        )
        """  # }}}
        logger.debug(f"Tinkoff.getStopOrders(account={account})")
        assert cls.__connect is not None

        try:
            response = await cls.__connect.stop_orders.get_stop_orders(
                account_id=account.meta.id
            )
            logger.debug(f"Tinkoff.getStopOrders: Response='{response}'")
        except ti.exceptions.InvestError as err:
            logger.error(f"Tinkoff.getStopOrders: Error={err}")
            return list()

        orders = list()
        for i in response.stop_orders:
            asset_id = await InstrumentId.byFigi(i.figi)
            await asset_id.cacheInfo()
            order = StopOrder(
                account_name=account.name,
                direction=cls.__ti_to_av(i.direction),
                asset_id=asset_id,
                lots=i.lots_requested,
                quantity=i.lots_requested * asset_id.lot,
                stop_price=cls.__ti_to_av(i.stop_price),
                exec_price=cls.__ti_to_av(i.price),
                status=cls.__ti_to_av(i.status),
                order_id=None,
                trade_id=None,
                exec_lots=0,  # XXX: у него не может быть исполненных лотов...
                exec_quantity=0,
                meta=str(i),
                broker_id=i.stop_order_id,
                transactions=list(),  # XXX: их тут тоже не может быть...
            )
            orders.append(order)

        return orders

    # }}}
    @classmethod  # getOperations  # {{{
    async def getOperations(
        cls, account: Account, from_: datetime, to: datetime
    ) -> list[Operation]:
        """Response example# {{{
        Operation(
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
                    2024, 7, 4, 12, 39, 26, 373816,
                    tzinfo=datetime.timezone.utc
                ),
                quantity=1,
                price=MoneyValue(currency='rub', units=160, nano=890000000))
            ],
            asset_uid='fe8d49a4-3321-449b-bd08-02efbac878fe',
            position_uid='17cf2c5b-2176-4851-85e2-a638225bef88',
            instrument_uid='cf1c6158-a303-43ac-89eb-9b1db8f96043'
        )
        """  # }}}
        logger.debug(f"Tinkoff.getOperations({account}, {from_}, {to})")
        assert cls.__connect is not None
        assert isinstance(from_, datetime)
        assert isinstance(to, datetime)

        # request operations
        response: ti.OperationsResponse = (
            await cls.__connect.operations.get_operations(
                account_id=account.meta.id,
                from_=from_,
                to=to,
            )
        )
        logger.debug(f"Tinkoff.getOperations: Response='{response}'")

        # convert response to list[avin.core.Operation]
        operations = list()
        for i in response.operations:
            # filter canceled operations
            if i.state != ti.OperationState.OPERATION_STATE_EXECUTED:
                continue

            # filter only operations with asset, without other operations
            # like input output money, broker services, dividents...
            if i.operation_type in (
                ti.OperationType.OPERATION_TYPE_BUY,
                ti.OperationType.OPERATION_TYPE_SELL,
            ):
                assert i.instrument_type == "share"
                asset_id = await InstrumentId.byUid(i.instrument_uid)
                assert asset_id is not None
                await asset_id.cacheInfo()

                op = Operation(
                    account_name=account.name,
                    dt=i.date,
                    direction=cls.__ti_to_av(i.operation_type),
                    asset_id=asset_id,
                    lots=int(i.quantity / asset_id.lot),
                    quantity=i.quantity,
                    price=cls.__ti_to_av(i.price),
                    amount=cls.__ti_to_av(i.price),
                    commission=None,
                    operation_id=None,
                    order_id=None,
                    trade_id=None,
                    meta=str(i),
                )
                operations.append(op)

        return operations

    # }}}
    @classmethod  # getPositions  # {{{
    async def getPositions(cls, account: Account) -> list[Postition]:
        logger.debug(f"Tinkoff.getPositions({account})")
        assert cls.__connect is not None

        response: ti.PositionsResponse = (
            await cls.__connect.operations.get_positions(
                account_id=account.meta.id
            )
        )
        logger.debug(f"Tinkoff.getPositions: Response='{response}'")
        return response

    # }}}
    @classmethod  # getPortfolio  # {{{
    async def getDetailedPortfolio(cls, account: Account) -> Portfolio:
        logger.debug(f"Tinkoff.getDetailedPortfolio({account})")
        assert cls.__connect is not None

        response: ti.PortfolioResponse = (
            await cls.__connect.operations.get_portfolio(
                account_id=account.meta.id
            )
        )
        logger.debug(f"Tinkoff.getDetailedPortfolio: Response='{response}'")
        return response

    # }}}
    @classmethod  # getWithdrawLimits  # {{{
    async def getWithdrawLimits(cls, account: Account):
        logger.debug(f"Tinkoff.getWithdrawLimits({account})")
        assert cls.__connect is not None

        response: ti.WithdrawLimitsResponse = (
            await cls.__connect.operations.get_withdraw_limits(
                account_id=account.meta.id
            )
        )
        logger.debug(f"Tinkoff.getWithdrawLimits: Response='{response}'")
        return response

    # }}}
    @classmethod  # getOrderOperation  # {{{
    async def getOrderOperation(
        cls, account: Account, order: Order
    ) -> Operation:
        logger.debug(f"Tinkoff.getOrderOperation({account}, {order})")

        response: ti.OrderState = await cls.__getOrderState(account, order)
        assert (
            response.execution_report_status
            == ti.OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL
        )

        operation = Operation(
            account_name=account.name,
            dt=response.order_date,
            direction=order.direction.toOperationDirection(),
            asset_id=order.asset_id,
            lots=order.lots,
            quantity=order.quantity,
            price=float(money_to_decimal(response.average_position_price)),
            amount=float(money_to_decimal(response.total_order_amount)),
            commission=float(money_to_decimal(response.executed_commission)),
            operation_id=None,
            order_id=order.order_id,
            trade_id=order.trade_id,
            meta=str(response),
        )

        return operation

    # }}}
    @classmethod  # getExecutedCommission  # {{{
    async def getExecutedCommission(
        cls, account: Account, order: Order
    ) -> Order.Status:
        logger.debug(f"Tinkoff.getExecutedCommission({account}, {order})")

        response: ti.OrderState = await cls.__getOrderState(account, order)
        assert (
            response.execution_report_status
            == ti.OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL
        )

        commission = cls.__ti_to_av(response.executed_commission)
        return commission

    # }}}
    @classmethod  # getHistoricalBars  # {{{
    async def getHistoricalBars(
        cls,
        asset: Asset,
        timeframe: TimeFrame,
        begin: datetime,
        end: datetime,
    ) -> list[Bar]:
        logger.debug(f"Tinkoff.getHistoricalBars({asset.ticker})")
        assert cls.__connect is not None

        new_bars = list()
        try:
            async for candle in cls.__connect.get_all_candles(
                figi=asset.figi,
                from_=begin,
                to=end,
                interval=cls.__av_to_ti(timeframe, ti.CandleInterval),
            ):
                if candle.is_complete:
                    bar = cls.__ti_to_av(candle)
                    new_bars.append(bar)
        except ti.exceptions.AioRequestError as err:
            logger.exception(err)

        return new_bars

    # }}}
    @classmethod  # getLastPrice  # {{{
    def getLastPrice(cls, asset_id: InstrumentId) -> float | None:
        logger.debug(f"Tinkoff.getLastPrice({asset_id})")

        with ti.Client(cls.TOKEN) as client:
            try:
                response = client.market_data.get_last_prices(
                    figi=[
                        asset_id.figi,
                    ]
                )
                last_price = cls.__ti_to_av(response.last_prices[0].price)
            except ti.exceptions.AioRequestError as err:
                logger.error(err)
                return None

            return last_price

    # }}}

    @classmethod  # syncOrder  # {{{
    async def syncOrder(cls, account: Account, order: Order) -> bool:
        """response example # {{{
        OrderState(
        order_id='R270663867',
        execution_report_status=
            <OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL: 1>,
        lots_requested=1,
        lots_executed=1,
        initial_order_price=MoneyValue(
            currency='rub', units=161, nano=400000000
            ),
        executed_order_price=MoneyValue(
            currency='rub', units=160, nano=890000000
            ),
        total_order_amount=MoneyValue(
            currency='rub', units=160, nano=890000000
            ),
        average_position_price=MoneyValue(
            currency='rub', units=160, nano=890000000
            ),
        initial_commission=MoneyValue(
            currency='rub', units=0, nano=90000000
            ),
        executed_commission=MoneyValue(
            currency='rub', units=0, nano=80000000
            ),
        figi='BBG004S68CP5',
        direction=<OrderDirection.ORDER_DIRECTION_BUY: 1>,
        initial_security_price=MoneyValue(
            currency='rub', units=161, nano=400000000
            ),
        stages=[
            OrderStage(
                price=MoneyValue(currency='rub', units=160, nano=890000000),
                quantity=1,
                trade_id='D134612622',
                execution_time=datetime.datetime(
                    2024, 7, 4, 12, 39, 26, 373816,
                    tzinfo=datetime.timezone.utc
                    )
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
        logger.debug(f"Tinkoff.syncOrder({account}, {order})")

        t = Order.Type
        if order.type in (t.MARKET, t.LIMIT):
            response: ti.OrderState = await cls.__getOrderState(
                account, order
            )
            order.exec_lots = response.lots_executed
            order.meta = str(response)
            status = cls.__ti_to_av(response.execution_report_status)
            await order.setStatus(status)
            return True

        if order.type in (t.STOP, t.STOP_LOSS, t.TAKE_PROFIT):
            stop_orders = await cls.getStopOrders(account)
            for i in stop_orders:
                if i.broker_id == order.broker_id:
                    order.meta = i.meta
                    await order.setStatus(i.status)
                    return True

        return False

    # }}}
    @classmethod  # postMarketOrder  # {{{
    async def postMarketOrder(cls, account: Account, order: Order) -> bool:
        """Response example# {{{
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
                    2024, 7, 4, 12, 39, 26, 693922,
                    tzinfo=datetime.timezone.utc
                )
            )
        )'
        """  # }}}
        logger.debug(f"Tinkoff.postMarketOrder({order})")
        assert cls.__connect is not None

        try:
            response: ti.PostOrderResponse = (
                await cls.__connect.orders.post_order(
                    account_id=account.meta.id,
                    order_type=cls.__av_to_ti(order, ti.OrderType),
                    direction=cls.__av_to_ti(order, ti.OrderDirection),
                    figi=order.asset_id.figi,
                    quantity=order.lots,
                    order_id=str(order.order_id),
                )
            )
            logger.debug(f"Tinkoff.postMarketOrder: Response='{response}'")
        except ti.exceptions.AioRequestError as err:
            logger.error(f"{err}")
            return False

        order.broker_id = response.order_id
        order.meta = str(response)
        return True

    # }}}
    @classmethod  # postLimitOrder  # {{{
    async def postLimitOrder(
        cls, account: Account, order: LimitOrder
    ) -> bool:
        """Response example# {{{
        PostOrderResponse(
            order_id='52004328245',
            execution_report_status=
                <OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_NEW: 4>,
            lots_requested=1,
            lots_executed=0,
            initial_order_price=MoneyValue(
                currency='rub', units=89, nano=400000000
            ),
            executed_order_price=MoneyValue(
                currency='', units=0, nano=0
            ),
            total_order_amount=MoneyValue(
                currency='rub', units=89, nano=400000000
            ),
            initial_commission=MoneyValue(
                currency='', units=0, nano=0
            ),
            executed_commission=MoneyValue(
                currency='', units=0, nano=0
            ),
            aci_value=MoneyValue(
                currency='', units=0, nano=0),
            figi='BBG004S68CP5',
            direction=<OrderDirection.ORDER_DIRECTION_BUY: 1>,
            initial_security_price=MoneyValue(
                currency='rub', units=89, nano=400000000
            ),
            order_type=<OrderType.ORDER_TYPE_LIMIT: 1>,
            message='',
            initial_order_price_pt=Quotation(units=0, nano=0),
            instrument_uid='cf1c6158-a303-43ac-89eb-9b1db8f96043',
            order_request_id='1725888227.1013482',
            response_metadata=ResponseMetadata(
                tracking_id='8616870e4bb1c42902197477b64fc542',
                server_time=datetime.datetime(
                    2024, 9, 9, 13, 23, 47, 398094,
                    tzinfo=datetime.timezone.utc
                )
            )
        )
        """  # }}}
        logger.debug(f"Tinkoff.postLimitOrder({order})")
        assert cls.__connect is not None

        try:
            response: ti.PostOrderResponse = (
                await cls.__connect.orders.post_order(
                    order_type=cls.__av_to_ti(order, ti.OrderType),
                    account_id=account.meta.id,
                    direction=cls.__av_to_ti(order, ti.OrderDirection),
                    figi=order.asset_id.figi,
                    quantity=order.lots,
                    price=Tinkoff.__av_to_ti(order.price, ti.Quotation),
                    order_id=str(order.order_id),
                )
            )
            logger.debug(f"Tinkoff.postLimitOrder: Response='{response}'")
        except ti.exceptions.AioRequestError as err:
            logger.error(f"{err}")
            return False

        order.broker_id = response.order_id
        order.meta = str(response)
        return True

    # }}}
    @classmethod  # postStopOrder  # {{{
    async def postStopOrder(cls, account: Account, order: StopOrder) -> bool:
        """Response example  # {{{
        PostStopOrderResponse(
            stop_order_id='f3f7e4e7-f076-4cc9-861d-d9995ed84b0f',
            order_request_id='',
            response_metadata=ResponseMetadata(
                tracking_id='87c7ed9d50034bb360a5f40edc3ba05c',
                server_time=datetime.datetime(
                    2024, 9, 9, 13, 32, 6, 690535,
                    tzinfo=datetime.timezone.utc
                )
            )
        )
        """  # }}}
        logger.debug(f"Tinkoff.postStopOrder({order})")
        assert cls.__connect is not None

        try:
            response = await cls.__connect.stop_orders.post_stop_order(
                stop_order_type=cls.__av_to_ti(order, ti.StopOrderType),
                account_id=account.meta.id,
                direction=cls.__av_to_ti(order, ti.StopOrderDirection),
                figi=order.asset_id.figi,
                quantity=order.lots,
                price=cls.__av_to_ti(order.exec_price, ti.Quotation),
                stop_price=cls.__av_to_ti(order.stop_price, ti.Quotation),
                # order_id=str(order.order_id),
                expiration_type=cls.__av_to_ti(
                    order, ti.StopOrderExpirationType
                ),
                # expire_date=
            )
            logger.debug(f"Tinkoff.postStopOrder: Response='{response}'")
        except ti.exceptions.AioRequestError as err:
            logger.error(f"{err}")
            return False

        order.broker_id = response.stop_order_id
        order.meta = str(response)
        return True

    # }}}
    @classmethod  # postStopLoss  # {{{
    async def postStopLoss(cls, account: Account, order: StopLoss) -> bool:
        logger.debug(f"Tinkoff.postStopLoss({account}, {order})")
        result = await cls.postStopOrder(account, order)
        return result

    # }}}
    @classmethod  # postTakeProfit:  # {{{
    async def postTakeProfit(
        cls, account: Account, order: TakeProfit
    ) -> bool:
        logger.debug(f"Tinkoff.postTakeProfit({account}, {order})")
        result = await cls.postStopOrder(account, order)
        return result

    # }}}
    @classmethod  # cancelLimitOrder  # {{{
    async def cancelLimitOrder(cls, account: Account, order: Order) -> bool:
        """Response example # {{{
        CancelOrderResponse(
            time=datetime.datetime(
                2024, 9, 9, 8, 53, 39, 312559,
                tzinfo=datetime.timezone.utc
            ),
            response_metadata=ResponseMetadata(
                tracking_id='d3e7296108394a9fd37e38357b3a3b05',
                server_time=datetime.datetime(
                    2024, 9, 9, 8, 53, 39, 314300,
                    tzinfo=datetime.timezone.utc
                )
            )
        )
        """  # }}}
        logger.debug(f"Tinkoff.cancelLimitOrder({account}, {order})")
        assert cls.__connect is not None

        try:
            response: ti.CancelOrderResponse = (
                await cls.__connect.orders.cancel_order(
                    account_id=account.meta.id,
                    order_id=order.broker_id,
                )
            )
            logger.debug(f"Tinkoff.cancelLimitOrder: Response='{response}'")
        except ti.exceptions.AioRequestError as err:
            logger.error(f"{err}")
            return False

        await order.setStatus(Order.Status.CANCELED)
        return True

    # }}}
    @classmethod  # cancelStopOrder  # {{{
    async def cancelStopOrder(cls, account: Account, order: Order) -> bool:
        """Response example# {{{
        CancelStopOrderResponse(
            time=datetime.datetime(
                2024, 9, 9, 15, 41, 4, 882931,
                tzinfo=datetime.timezone.utc)
            )

        Exception:
        raise AioRequestError(status_code, details, metadata) from e
        tinkoff.invest.exceptions.AioRequestError: (
            <StatusCode.NOT_FOUND: (5, 'not found')>,
            '50006',
            Metadata(
                tracking_id='8b0b16ada64beec08d131b751d51df85',
                ratelimit_limit='50, 50;w=60',
                ratelimit_remaining=48,
                ratelimit_reset=39,
                message='Stop-order notfound'
            )
        )
        """  # }}}
        logger.debug(f"Tinkoff.cancelStopOrder({account}, {order})")
        assert cls.__connect is not None

        try:
            response = await cls.__connect.stop_orders.cancel_stop_order(
                account_id=account.meta.id,
                stop_order_id=order.broker_id,
            )
            logger.debug(f"Tinkoff.cancelStopOrder: Response='{response}'")
        except ti.exceptions.AioRequestError as err:
            logger.error(err)
            if err.code == StatusCode.NOT_FOUND:
                raise BrokerError(
                    f"Tinkoff stop-order '{order.order_id}' - not found"
                ) from err
            return False

        await order.setStatus(Order.Status.CANCELED)
        return True

    # }}}

    @classmethod  # createBarStream  # {{{
    async def createBarStream(
        cls, asset: Asset, timeframe: TimeFrame
    ) -> None:
        logger.info(f"  - create bar stream {asset}-{timeframe}")
        assert cls.__connect is not None

        if not cls.__data_stream:
            cls.__data_stream = cls.__connect.create_market_data_stream()

        figi = asset.figi
        interval = cls.__av_to_ti(timeframe, ti.SubscriptionInterval)
        candle_subscription = ti.CandleInstrument(
            figi=figi, interval=interval
        )
        cls.__data_subscriptions.append(candle_subscription)
        cls.__data_stream.candles.waiting_close().subscribe(
            [candle_subscription]
        )

    # }}}
    @classmethod  # createTransactionStream  # {{{
    async def createTransactionStream(cls, account: Account) -> None:
        logger.info(f"  Tinkoff create transaction stream: account={account}")
        assert cls.__connect is not None

        cls.__transaction_stream = cls.__connect.orders_stream.trades_stream(
            accounts=[
                account.meta.id,
            ]
        )

    # }}}
    @classmethod  # createPositionSteam  # {{{
    async def createPositionSteam(cls, account: Account) -> None:
        """см Тинькофф АПИ, сервис операций, PositionsStream
        из него можно сделать поток обновляющегося портфеля.
        Он выдает позиции в портфеле, по группам деньги, акции, фьючерсы...
        Пока никак не использую
        Его поидее тоже надо сохранять в селф, и завести отдельный
        сигнал через который отправлять с него ответы.

        и там еще есть какой то PortfolioStream, там еще больше инфы
        по портфелю
        """
        assert False

        logger.debug("Tinkoff.createOrderStream()")
        stream = cls.__connect.operations_stream.positions_stream(
            accounts=[
                account.meta.id,
            ]
        )

    # }}}
    @classmethod  # startDataStream  # {{{
    async def startDataStream(cls) -> bool:
        logger.info("  Tinkoff try start data stream")
        cls.__data_cycle = asyncio.create_task(cls.__dataCycle())

        seconds_elapsed = 0
        while not cls.__data_cycle_is_active:
            logger.info(f"  - waiting data... ({seconds_elapsed} sec)")
            await asyncio.sleep(1)
            seconds_elapsed += 1
            if seconds_elapsed == 5:
                logger.error("  - fail to start data stream Tinkoff :(")
                return False

        logger.info("  - data stream started!")
        return True

    # }}}
    @classmethod  # stopDataStream  # {{{
    async def stopDataStream(cls):
        if cls.__data_cycle:
            cls.__data_cycle.cancel()
            cls.__data_cycle_is_active = False
            cls.__data_stream.unsubscribe(cls.__data_subscriptions)
            cls.__data_stream.stop()
            cls.__data_stream = None
            cls.__data_subscriptions.clear()
            logger.info("  Tinkoff data stream stopped")

    # }}}
    @classmethod  # startTransactionStream  # {{{
    async def startTransactionStream(cls):
        logger.info("  Tinkoff start transaction stream")
        cls.__transaction_cycle = asyncio.create_task(
            cls.__transactionCycle()
        )
        cls.__transaction_cycle_is_active = True
        return True

    # }}}
    @classmethod  # stopTransactionStream  # {{{
    async def stopTransactionStream(cls):
        if cls.__transaction_cycle:
            cls.__transaction_cycle.cancel()
            cls.__transaction_cycle_is_active = False
            cls.__transaction_stream = None
            logger.info("  Tinkoff stop transaction stream")

    # }}}

    @classmethod  # __getOrderState  # {{{
    async def __getOrderState(cls, account: Account, order: Order):
        """Response example # {{{
        OrderState(
        order_id='R270663867',
        execution_report_status=
            <OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL: 1>,
        lots_requested=1,
        lots_executed=1,
        initial_order_price=MoneyValue(
            currency='rub', units=161, nano=400000000
        ),
        executed_order_price=MoneyValue(
            currency='rub', units=160, nano=890000000
        ),
        total_order_amount=MoneyValue(
            currency='rub', units=160, nano=890000000
        ),
        average_position_price=MoneyValue(
            currency='rub', units=160, nano=890000000
        ),
        initial_commission=MoneyValue(
            currency='rub', units=0, nano=90000000
            ),
        executed_commission=MoneyValue(
            currency='rub', units=0, nano=80000000
            ),
        figi='BBG004S68CP5',
        direction=<OrderDirection.ORDER_DIRECTION_BUY: 1>,
        initial_security_price=MoneyValue(
            currency='rub', units=161, nano=400000000
        ),
        stages=[
            OrderStage(
                price=MoneyValue(currency='rub', units=160, nano=890000000),
                quantity=1,
                trade_id='D134612622',
                execution_time=datetime.datetime(
                    2024, 7, 4, 12, 39, 26, 373816,
                    tzinfo=datetime.timezone.utc
                )
            )
        ],
        service_commission=MoneyValue(
            currenc y='rub', units=290, nano=0
        ),
        currency='rub',
        order_type=<OrderType.ORDER_TYPE_MARKET: 2>,
        order_date=datetime.datetime(
            2024, 7, 4, 12, 39, 26, 372885,
            tzinfo=datetime.timezone.utc
        ),
        instrument_uid='cf1c6158-a303-43ac-89eb-9b1db8f96043',
        order_request_id='4defaa66-6545-4bcc-9f05-301adf32dfce'
        )
        """
        # }}}
        logger.debug(f"Tinkoff.__getOrderState({order})")
        assert cls.__connect is not None

        response: ti.OrderState = await cls.__connect.orders.get_order_state(
            account_id=account.meta.id,
            order_id=order.broker_id,
        )
        logger.debug(f"Tinkoff.__getOrderState: Response='{response}'")

        return response

    # }}}
    @classmethod  # __connectionCycle  # {{{
    async def __connectionCycle(cls):
        logger.debug("Tinkoff.__connectionCycle()")

        async with ti.AsyncClient(cls.TOKEN, target=cls.TARGET) as client:
            response = await client.users.get_accounts()
            if not response:
                return

            cls.__connect = client
            cls.__connect_cycle_is_active = True
            while cls.__connect_cycle_is_active:
                await asyncio.sleep(1)

        cls.__connect_cycle_is_active = False  # XXX: ???

    # }}}
    @classmethod  # __dataCycle  # {{{
    async def __dataCycle(cls):
        """Response example# {{{
        MarketDataResponse(
            subscribe_candles_response=None,
            subscribe_order_book_response=None,
            subscribe_trades_response=None,
            subscribe_info_response=None,
            subscribe_last_price_response=None,
            candle=Candle(
                figi='BBG004S68CP5',
                interval=
                  <SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE: 1>,
                open=Quotation(units=101, nano=700000000),
                high=Quotation(units=101, nano=900000000),
                low=Quotation(units=101, nano=700000000),
                close=Quotation(units=101, nano=900000000),
                volume=225,
                time=datetime.datetime(
                    2024, 9, 10, 11, 54,
                    tzinfo=datetime.timezone.utc
                ),
                last_trade_ts=datetime.datetime(
                    2024, 9, 10, 11, 54, 30, 770361,
                    tzinfo=datetime.timezone.utc),
                instrument_uid='cf1c6158-a303-43ac-89eb-9b1db8f96043'),
            trade=None,
            orderbook=None,
            trading_status=None,
            last_price=None
            ping=None,
            )
        """  # }}}
        logger.debug("async Tinkoff.__dataCycle()")

        async for response in cls.__data_stream:
            logger.debug(f"Tinkoff.__dataCycle: Response='{response}'")
            cls.__data_cycle_is_active = True
            if response.candle:
                figi = response.candle.figi
                timeframe = cls.__ti_to_av(response.candle.interval)
                bar = cls.__ti_to_av(response.candle)
                event = NewBarEvent(figi, timeframe, bar)
                await Tinkoff.new_bar.async_emit(event)

        # TODO: нет, здесь надо что то более глобальное
        # смена флага и че, про нее никто не узнает
        # можно сигнал завести - дата стрим упал типо
        # и тот кто ловит тот путь и реконетит. Пока так.
        # а может и самому брокеру внутри себя поддерживать
        # все соединения, опираясь на флаги...
        # вот стоит флаг коннектед - значит надо поддерживать соединение
        # стоит флаг дата стрим актив - значит надо поддерживать стрим
        # стоит флаг транзактион стрим - надо поддерживать его
        cls.__data_cycle_is_active = False  # XXX: ???

    # }}}
    @classmethod  # __transactionCycle  # {{{
    async def __transactionCycle(cls):
        """Response example# {{{
        TradesStreamResponse(
            order_trades=OrderTrades(
                order_id='RINV7SQH9BWBWN0ZX8J9',
                created_at=datetime.datetime(
                    2024, 9, 6, 7, 42, 38, 88683,
                    tzinfo=datetime.timezone.utc
                ),
                direction=<OrderDirection.ORDER_DIRECTION_BUY: 1>,
                figi='BBG004S68614',
                trades=[
                    OrderTrade(
                        date_time=datetime.datetime(
                            2024, 9, 6, 7, 42, 36, 77857,
                            tzinfo=datetime.timezone.utc
                        ),
                        price=Quotation(units=16, nano=41500000),
                        quantity=200,
                        trade_id='DINVAXQJXE2GH4F32AVQ'
                    )
                ],
                account_id='2193020159',
                instrument_uid='53b67587-96eb-4b41-8e0c-d2e3c0bdd234'
            ),
            ping=None,
            subscription=None
        )
        """  # }}}
        logger.debug("Tinkoff.__transactionCycle()")

        async for response in cls.__transaction_stream:
            logger.debug(f"Tinkoff.__transactionCycle: Response='{response}'")

            if response.order_trades:
                event: ti.OrderTrades = cls.__ti_to_av(response.order_trades)
                await Tinkoff.new_transaction.async_emit(event)

                # TODO: выглядит криво, эвент обращается к своему аккаунту
                # чтобы отправить в него себя же... бред, думай как лучше.
                await event.account.receiveTransaction(event)

            if response.ping:
                pass

        cls.__transaction_cycle_is_active = False  # XXX: ???

    # }}}

    @staticmethod  # __ti_to_av  # {{{
    def __ti_to_av(obj: Any):
        logger.debug(f"Tinkoff.__ti_to_av({obj})")

        class_name = obj.__class__.__name__
        match class_name:
            case "MoneyValue":
                return Tinkoff.__tiMoneyValue_to_avPrice(obj)
            case "Quotation":
                return Tinkoff.__tiQuotation_to_avPrice(obj)
            case "OrderType":
                return Tinkoff.__tiOrderType_to_avType(obj)
            case "StopOrderType":
                return Tinkoff.__tiStopOrderType_to_avType(obj)
            case "OrderDirection":
                return Tinkoff.__tiOrderDirection_to_avDirection(obj)
            case "StopOrderDirection":
                return Tinkoff.__tiStopOrderDirection_to_avDirection(obj)
            case "OrderExecutionReportStatus":
                return Tinkoff.__tiOrderExecutionReportStatus_to_avStatus(obj)
            case "StopOrderStatusOption":
                return Tinkoff.__tiStopOrderStatusOption_to_avStatus(obj)
            case "OperationType":
                return Tinkoff.__tiOperationType_to_avOperationDirection(obj)
            case "SubscriptionInterval":
                return Tinkoff.__tiSubscriptionInterval_to_avTimeFrame(obj)
            case "Candle":
                return Tinkoff.__tiCandle_to_avBar(obj)
            case "HistoricCandle":
                return Tinkoff.__tiCandle_to_avBar(obj)
            case "OrderTrades":
                return Tinkoff.__tiOrderTrades_to_avTransactionEvent(obj)
            case _:
                raise BrokerError(
                    f"Tinkoff fail convert: unknown object='{obj}', "
                    f"type='{type(obj)}'"
                )

    # }}}
    @staticmethod  # __tiMoneyValue_to_avPrice  # {{{
    def __tiMoneyValue_to_avPrice(ti_money_value):
        logger.debug(f"Tinkoff.__tiMoneyValue_to_avPrice({ti_money_value})")

        price = float(money_to_decimal(ti_money_value))
        return price

    # }}}
    @staticmethod  # __tiQuotation_to_avPrice  # {{{
    def __tiQuotation_to_avPrice(ti_quotation):
        logger.debug(f"Tinkoff.__tiQuotation_to_avPrice({ti_quotation})")

        price = float(quotation_to_decimal(ti_quotation))
        return price

    # }}}
    @staticmethod  # __tiOrderType_to_avType  # {{{
    def __tiOrderType_to_avType(tinkoff_order_type):
        logger.debug(
            f"Tinkoff.__tiOrderDirection_to_avType({tinkoff_order_type})"
        )

        types = {
            "ORDER_TYPE_UNSPECIFIED": Order.Type.UNDEFINE,
            "ORDER_TYPE_LIMIT": Order.Type.LIMIT,
            "ORDER_TYPE_MARKET": Order.Type.MARKET,
            "ORDER_TYPE_BESTPRICE": Order.Type.MARKET,
        }
        avin_order_type = types[tinkoff_order_type]

        return avin_order_type

    # }}}
    @staticmethod  # __tiStopOrderType_to_avType  # {{{
    def __tiStopOrderType_to_avType(tinkoff_order_type):
        logger.debug(
            f"Tinkoff.__tiOrderDirection_to_avType({tinkoff_order_type})"
        )

        types = {
            "STOP_ORDER_TYPE_UNSPECIFIED": Order.Type.UNDEFINE,
            "STOP_ORDER_TYPE_TAKE_PROFIT": Order.Type.TAKE_PROFIT,
            "STOP_ORDER_TYPE_STOP_LOSS": Order.Type.STOP_LOSS,
            "STOP_ORDER_TYPE_STOP_LIMIT": Order.Type.STOP,
        }
        avin_order_type = types[tinkoff_order_type]

        return avin_order_type

    # }}}
    @staticmethod  # __tiOrderDirection_to_avDirection  # {{{
    def __tiOrderDirection_to_avDirection(tinkoff_direction):
        logger.debug(
            "Tinkoff.__tiOrderDirection_to_avOrderDirection("
            f"{tinkoff_direction})"
        )

        directions = {
            "ORDER_DIRECTION_UNSPECIFIED": Order.Direction.UNDEFINE,
            "ORDER_DIRECTION_BUY": Order.Direction.BUY,
            "ORDER_DIRECTION_SELL": Order.Direction.SELL,
        }
        avin_direction = directions[tinkoff_direction.name]

        return avin_direction

    # }}}
    @staticmethod  # __tiStopOrderDirection_to_avDirection  # {{{
    def __tiStopOrderDirection_to_avDirection(tinkoff_direction):
        logger.debug(
            f"Tinkoff.__tiOrderDirection_to_avOrderDirection("
            f"{tinkoff_direction})"
        )

        t = ti.StopOrderDirection
        directions = {
            t.STOP_ORDER_DIRECTION_UNSPECIFIED: Order.Direction.UNDEFINE,
            t.STOP_ORDER_DIRECTION_BUY: Order.Direction.BUY,
            t.STOP_ORDER_DIRECTION_SELL: Order.Direction.SELL,
        }
        avin_direction = directions[tinkoff_direction]

        return avin_direction

    # }}}
    @staticmethod  # __tiOrderExecutionReportStatus_to_avStatus  # {{{
    def __tiOrderExecutionReportStatus_to_avStatus(tinkoff_status):
        logger.debug(
            f"Tinkoff.__tiOrderExecutionReportStatus_to_avOrderStatus"
            f"({tinkoff_status})"
        )

        # tinkoff limit order statuses
        t = ti.OrderExecutionReportStatus
        statuses = {
            t.EXECUTION_REPORT_STATUS_NEW: Order.Status.POSTED,
            t.EXECUTION_REPORT_STATUS_PARTIALLYFILL: Order.Status.PARTIAL,
            t.EXECUTION_REPORT_STATUS_FILL: Order.Status.FILLED,
            t.EXECUTION_REPORT_STATUS_REJECTED: Order.Status.REJECTED,
            t.EXECUTION_REPORT_STATUS_CANCELLED: Order.Status.CANCELED,
            t.EXECUTION_REPORT_STATUS_UNSPECIFIED: Order.Status.UNDEFINE,
        }
        avin_status = statuses[tinkoff_status]

        return avin_status

    # }}}
    @staticmethod  # __tiStopOrderStatusOption_to_avStatus  # {{{
    def __tiStopOrderStatusOption_to_avStatus(tinkoff_status):
        logger.debug(
            f"Tinkoff.__tiStopOrderStatusOption_to_avStatus({tinkoff_status})"
        )

        # tinkoff stop order statuses
        t = ti.StopOrderStatusOption
        statuses = {
            t.STOP_ORDER_STATUS_UNSPECIFIED: Order.Status.UNDEFINE,
            # XXX: что это?
            t.STOP_ORDER_STATUS_ALL: Order.Status.UNDEFINE,
            # XXX: rename ACTIVE?
            t.STOP_ORDER_STATUS_ACTIVE: Order.Status.PENDING,
            t.STOP_ORDER_STATUS_EXECUTED: Order.Status.EXECUTED,  # TEST:
            t.STOP_ORDER_STATUS_CANCELED: Order.Status.CANCELED,
            t.STOP_ORDER_STATUS_EXPIRED: Order.Status.EXPIRED,
        }
        avin_status = statuses[tinkoff_status]

        # TEST: надо посмотреть поподробнее, какой статус становится
        # у ордера когда он срабатывает, возможно у тинькова executed
        # это тоже что у меня triggered... кстати... тогда можно
        # этот ордер не считать вообще... блять сложно короче пиздец
        # надо смотреть как меняется статус ордера у тинька
        return avin_status

    # }}}
    @staticmethod  # __tiOperationType_to_avOperationDirection  # {{{
    def __tiOperationType_to_avOperationDirection(ti_operation_type):
        logger.debug(
            f"Tinkoff.__tiOperationType_to_avOperationDirection"
            f"({ti_operation_type})"
        )

        t = ti.OperationType
        types = {
            t.OPERATION_TYPE_BUY: Operation.Direction.BUY,
            t.OPERATION_TYPE_SELL: Operation.Direction.SELL,
        }
        av_direction = types[ti_operation_type]

        return av_direction

    # }}}
    @staticmethod  # __tiSubscriptionInterval_to_avTimeFrame  # {{{
    def __tiSubscriptionInterval_to_avTimeFrame(ti_interval):
        logger.debug(
            f"Tinkoff.__tiSubscriptionInterval_to_avTimeFrame"
            f"({ti_interval})"
        )

        t = ti.SubscriptionInterval
        intervals = {
            t.SUBSCRIPTION_INTERVAL_ONE_MINUTE: TimeFrame("1M"),
            t.SUBSCRIPTION_INTERVAL_FIVE_MINUTES: TimeFrame("5M"),
            t.SUBSCRIPTION_INTERVAL_10_MIN: TimeFrame("10M"),
            t.SUBSCRIPTION_INTERVAL_ONE_HOUR: TimeFrame("1H"),
            t.SUBSCRIPTION_INTERVAL_ONE_DAY: TimeFrame("D"),
        }
        av_timeframe = intervals[ti_interval]

        return av_timeframe

    # }}}
    @staticmethod  # __tiCandle_to_avBar  # {{{
    def __tiCandle_to_avBar(candle):
        logger.debug(f"Tinkoff.__tiCandle_to_avBar({candle})")

        open = float(quotation_to_decimal(candle.open))
        close = float(quotation_to_decimal(candle.close))
        high = float(quotation_to_decimal(candle.high))
        low = float(quotation_to_decimal(candle.low))
        vol = candle.volume
        dt = candle.time

        bar = Bar(dt, open, high, low, close, vol)
        return bar

    # }}}
    @staticmethod  # __tiOrderTrades_to_avTransactionEvent  # {{{
    def __tiOrderTrades_to_avTransactionEvent(order_trades):
        """Response example# {{{
        order_trades=OrderTrades(
            order_id='RINV7SQH9BWBWN0ZX8J9',
            created_at=datetime.datetime(
                2024, 9, 6, 7, 42, 38, 88683,
                tzinfo=datetime.timezone.utc
            ),
            direction=<OrderDirection.ORDER_DIRECTION_BUY: 1>,
            figi='BBG004S68614',
            trades=[
                OrderTrade(
                    date_time=datetime.datetime(
                        2024, 9, 6, 7, 42, 36, 77857,
                        tzinfo=datetime.timezone.utc
                    ),
                    price=Quotation(units=16, nano=41500000),
                    quantity=200,
                    trade_id='DINVAXQJXE2GH4F32AVQ'
                )
            ],
            account_id='2193020159',
            instrument_uid='53b67587-96eb-4b41-8e0c-d2e3c0bdd234'
        ),
        ping=None,
        subscription=None
        )
        """  # }}}
        logger.debug(
            f"Tinkoff.__tiOrderTrades_to_avTransactionEvent"
            f"({order_trades})"
        )

        # find account
        account_id = order_trades.account_id  # -> name
        for i in Tinkoff.__accounts:
            if i.meta.id == account_id:
                account = i
                break

        # extract args
        figi = order_trades.figi
        direction = Tinkoff.__ti_to_av(order_trades.direction)
        order_broker_id = order_trades.order_id
        transactions = order_trades.trades  # TODO: convert

        # create TransactionEvent
        transaction_event = TransactionEvent(
            account=account,
            figi=figi,
            direction=direction,
            order_broker_id=order_broker_id,
            transactions=transactions,
        )
        return transaction_event

    # }}}
    @staticmethod  # __av_to_ti  # {{{
    def __av_to_ti(av_obj: Any, ti_class: ClassVar):
        logger.debug(f"Tinkoff.__av_to_ti({av_obj}, {ti_class})")

        class_name = ti_class.__name__
        match class_name:
            case "Quotation":
                return Tinkoff.__avPrice_to_tiQuotation(av_obj)
            case "OrderType":
                return Tinkoff.__avOrder_to_tiOrderType(av_obj)
            case "StopOrderType":
                return Tinkoff.__avOrder_to_tiStopOrderType(av_obj)
            case "OrderDirection":
                return Tinkoff.__avOrder_to_tiOrderDirection(av_obj)
            case "StopOrderDirection":
                return Tinkoff.__avOrder_to_tiStopOrderDirection(av_obj)
            case "StopOrderExpirationType":
                return Tinkoff.__avOrder_to_tiStopOrderExpirationType(av_obj)
            case "SubscriptionInterval":
                return Tinkoff.__avTimeFrame_to_tiSubscriptionInterval(av_obj)
            case "CandleInterval":
                return Tinkoff.__avTimeFrame_to_tiCandleInterval(av_obj)
            case _:
                raise BrokerError(
                    f"Tinkoff fail extract: ti_class='{ti_class}', "
                    f"av_obj='{av_obj}'"
                )

    # }}}
    @staticmethod  # __avPrice_to_tiQuotation()  # {{{
    def __avPrice_to_tiQuotation(price):
        logger.debug(f"Tinkoff.__avPrice_to_tiQuotation({price})")

        if price is None:
            return None
        else:
            quotation = decimal_to_quotation(Decimal(price))
            return quotation

    # }}}
    @staticmethod  # __avOrder_to_tiOrderType  # {{{
    def __avOrder_to_tiOrderType(order: Order):
        logger.debug(f"Tinkoff.__avOrder_to_tiOrderType({order})")

        t = ti.OrderType

        if order.type == Order.Type.MARKET:
            return t.ORDER_TYPE_MARKET

        if order.type == Order.Type.LIMIT:
            return t.ORDER_TYPE_LIMIT

    # }}}
    @staticmethod  # __avOrder_to_tiStopOrderType  # {{{
    def __avOrder_to_tiStopOrderType(order):
        logger.debug(f"Tinkoff.__avOrder_to_tiStopOrderType({order})")

        t = ti.StopOrderType

        if order.type == Order.Type.STOP_LOSS:
            return t.STOP_ORDER_TYPE_STOP_LOSS

        if order.type == Order.Type.TAKE_PROFIT:
            return t.STOP_ORDER_TYPE_TAKE_PROFIT

        if order.type == Order.Type.STOP:
            current_price = Tinkoff.getLastPrice(order.asset_id)
            if order.direction == Order.Direction.BUY:
                if current_price >= order.stop_price:
                    return t.STOP_ORDER_TYPE_TAKE_PROFIT
                if current_price < order.stop_price:
                    return t.STOP_ORDER_TYPE_STOP_LIMIT
            elif order.direction == Order.Direction.SELL:
                if current_price <= order.stop_price:
                    return t.STOP_ORDER_TYPE_TAKE_PROFIT
                if current_price > order.stop_price:
                    return t.STOP_ORDER_TYPE_STOP_LIMIT

    # }}}
    @staticmethod  # __avOrder_to_tiOrderDirection  # {{{
    def __avOrder_to_tiOrderDirection(order: Order):
        logger.debug(f"Tinkoff.__avOrder_to_tiOrderDirection({order})")

        assert order.type in (Order.Type.MARKET, Order.Type.LIMIT)

        if order.direction == Order.Direction.BUY:
            return ti.OrderDirection.ORDER_DIRECTION_BUY

        if order.direction == Order.Direction.SELL:
            return ti.OrderDirection.ORDER_DIRECTION_SELL

        return ti.OrderDirection.ORDER_DIRECTION_UNSPECIFIED

    # }}}
    @staticmethod  # __avOrder_to_tiStopOrderDirection  # {{{
    def __avOrder_to_tiStopOrderDirection(order: Order):
        logger.debug(f"Tinkoff.__avOrder_to_tiStopOrderDirection({order})")

        assert order.type in (
            Order.Type.STOP,
            Order.Type.STOP_LOSS,
            Order.Type.TAKE_PROFIT,
        )

        t = ti.StopOrderDirection
        if order.direction == Order.Direction.BUY:
            return t.STOP_ORDER_DIRECTION_BUY
        if order.direction == Order.Direction.SELL:
            return t.STOP_ORDER_DIRECTION_SELL

        return t.STOP_ORDER_DIRECTION_UNSPECIFIED

    # }}}
    @staticmethod  # __avOrder_to_tiStopOrderExpirationType  # {{{
    def __avOrder_to_tiStopOrderExpirationType(order: Order):
        logger.debug(
            f"Tinkoff.__avOrder_to_tiStopOrderExpirationType({order})"
        )

        t = ti.StopOrderExpirationType
        if order.type == Order.Type.STOP:
            return t.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL
        if order.type == Order.Type.STOP_LOSS:
            return t.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL
        if order.type == Order.Type.TAKE_PROFIT:
            return t.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL

    # }}}
    @staticmethod  # __avTimeFrame_to_tiSubscriptionInterval  # {{{
    def __avTimeFrame_to_tiSubscriptionInterval(av_timeframe):
        logger.debug(
            f"Tinkoff.__avTimeFrame_to_tiSubscriptionInterval({av_timeframe})"
        )

        t = ti.SubscriptionInterval
        intervals = {
            "1M": t.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
            "5M": t.SUBSCRIPTION_INTERVAL_FIVE_MINUTES,
            "10M": t.SUBSCRIPTION_INTERVAL_10_MIN,
            "1H": t.SUBSCRIPTION_INTERVAL_ONE_HOUR,
            "D": t.SUBSCRIPTION_INTERVAL_ONE_DAY,
            "W": t.SUBSCRIPTION_INTERVAL_WEEK,
            "M": t.SUBSCRIPTION_INTERVAL_MONTH,
        }
        ti_interval = intervals[str(av_timeframe)]
        return ti_interval

    # }}}
    @staticmethod  # __avTimeFrame_to_tiCandleInterval  # {{{
    def __avTimeFrame_to_tiCandleInterval(av_timeframe):
        logger.debug(
            f"Tinkoff.__avTimeFrame_to_tiCandleInterval({av_timeframe})"
        )

        t = ti.CandleInterval
        intervals = {
            "1M": t.CANDLE_INTERVAL_1_MIN,
            "5M": t.CANDLE_INTERVAL_5_MIN,
            "10M": t.CANDLE_INTERVAL_10_MIN,
            "1H": t.CANDLE_INTERVAL_HOUR,
            "D": t.CANDLE_INTERVAL_DAY,
            "W": t.CANDLE_INTERVAL_WEEK,
            "M": t.CANDLE_INTERVAL_MONTH,
        }
        ti_interval = intervals[str(av_timeframe)]
        return ti_interval

    # }}}
