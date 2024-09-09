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
from decimal import Decimal
from typing import Any

import tinkoff.invest as ti
from grpc import StatusCode
from tinkoff.invest.utils import (
    decimal_to_quotation,
    money_to_decimal,
    quotation_to_decimal,
)

from avin.config import Usr
from avin.core import Account, Asset, Broker, Id, LimitOrder, Order, StopOrder
from avin.data import AssetType, Exchange, InstrumentId
from avin.exceptions import BrokerError
from avin.utils import Cmd, logger

# TODO: округление прайсов упростить.
# или пилить свой класс работающий с currency, units, nano
# или что то типо такого
# round_price(155.56484668, min_price_step)


# TODO: сделай единообразным поведение методов getLimitOrders, getStopOrders,
# если уж перехватываешь исключение то везде

# TODO: проверить возвращаемые значения, сделать нормальные bool везде


class Tinkoff(Broker):
    name = "Tinkoff"
    TARGET = ti.constants.INVEST_GRPC_API
    TOKEN = Cmd.read(Usr.TINKOFF_TOKEN).strip()

    def __init__(self):  # {{{
        logger.debug("Tinkoff.__init__()")
        Broker.__init__(self)

        self.__connect_task = None
        self.__client = None
        self.__connected = False
        self.__accounts = list()

    # }}}
    def isConnect(self) -> bool:  # {{{
        logger.debug("Tinkoff.isConnect()")
        return self.__connected

    # }}}
    async def connect(self) -> None:  # {{{
        if self.__connected:
            return

        logger.info(":: Tinkoff try to connect")
        self.__connect_task = asyncio.create_task(self.__runConnectionCycle())

        seconds_elapsed = 0
        while not self.__connected:
            logger.info(f"  - waiting connection... ({seconds_elapsed} sec)")
            await asyncio.sleep(1)
            seconds_elapsed += 1
            if seconds_elapsed == 5:
                self.__connect_task.cancel()
                logger.error("  - fail to connect Tinkoff :(")
                return

        logger.info("  - successfully connected!")

    # }}}
    async def disconnect(self):  # {{{
        logger.debug("Tinkoff.disconnect()")

        self.__connect_task.cancel()
        self.__client = None
        self.__connected = False
        self.__accounts = list()

        logger.info(":: Tinkoff disconnected!")

    # }}}
    async def isMarketOpen(self) -> bool:  # {{{
        logger.debug("Tinkoff.isMarketOpen()")

        if not self.__connected:
            logger.error(
                "Tinkoff not connected, impossible to check is market open."
            )
            return False

        sber = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "SBER")

        response = await self.__client.market_data.get_trading_status(
            figi=sber.figi
        )
        logger.debug(f"Tinkoff.isMarketOpen: Response='{response}'")

        return (
            response.market_order_available_flag
            and response.api_trade_available_flag
        )

    # }}}
    async def getAccount(self, account_name: str) -> Account | None:  # {{{
        # If you have never requested accounts, then request now
        if not self.__accounts:
            await self.getAllAccounts()

        # find 'account_name' & return it
        for account in self.__accounts:
            if account.name == account_name:
                return account

        # return None if not found
        return None

    # }}}
    async def getAllAccounts(self) -> list[Account]:  # {{{
        logger.debug("Tinkoff.getAllAccounts()")
        if self.__accounts:
            return self.__accounts

        response = await self.__client.users.get_accounts()
        logger.debug(f"Tinkoff.getAllAccounts: Response='{response}'")

        self.__accounts = list()
        for tinkoff_account in response.accounts:
            acc = Account(
                name=tinkoff_account.name, broker=self, meta=tinkoff_account
            )
            self.__accounts.append(acc)
        return self.__accounts

    # }}}
    async def getMoney(self, account: Account) -> float:  # {{{
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

        response: ti.PositionsResponse = (
            await self.__client.operations.get_positions(
                account_id=account.meta.id,
            )
        )
        logger.debug(f"Tinkoff.getMoney: Response='{response}'")

        # FIX: надо сделать свой класс Cash где нормально хранить
        # тоже currency, units, nano. И здесь
        # response.money[0]
        # работает только пока на счете из валют лежат только рубли
        money = float(quotation_to_decimal(response.money[0]))
        return money

    # }}}
    async def getLimitOrders(self, account: Account) -> list[Order]:  # {{{
        """Response example# {{{
        GetOrdersResponse(
            orders=[
                OrderState(
                    order_id='51985347692',
                    execution_report_status=
                        <OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_NEW: 4>,
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

        response: ti.GetOrdersResponse = (
            await self.__client.orders.get_orders(account_id=account.meta.id)
        )
        logger.debug(f"Tinkoff.getLimitOrders: Response='{response}'")

        orders = list()
        for i in response.orders:
            asset_id = await InstrumentId.byFigi(i.figi)
            await asset_id.cacheInfo()
            order = LimitOrder(
                account_name=account.name,
                direction=self.__ti_to_av(i.direction),
                asset_id=asset_id,
                lots=i.lots_requested,
                quantity=i.lots_requested * asset_id.lot,
                price=self.__ti_to_av(i.initial_order_price),
                status=self.__ti_to_av(i.execution_report_status),
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
    async def getStopOrders(self, account: Account) -> list[Order]:  # {{{
        """Response example# {{{
        GetStopOrdersResponse(
            stop_orders=[
                StopOrder(
                    stop_order_id='5dfa66c8-090e-4594-9bac-5a3eef0a0873',
                    lots_requested=1,
                    figi='BBG004S68CP5',
                    direction=<StopOrderDirection.STOP_ORDER_DIRECTION_BUY: 1>,
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
                    take_profit_type=<TakeProfitType.TAKE_PROFIT_TYPE_REGULAR: 1>,
                    trailing_data=StopOrderTrailingData(
                        indent=Quotation(units=0, nano=0),
                        indent_type=
                            <TrailingValueType.TRAILING_VALUE_UNSPECIFIED: 0>,
                        spread=Quotation(units=0, nano=0),
                        spread_type=
                            <TrailingValueType.TRAILING_VALUE_UNSPECIFIED: 0>,
                        status=<TrailingStopStatus.TRAILING_STOP_UNSPECIFIED: 0>,
                    price=Quotation(units=0, nano=0),
                    extr=Quotation(units=0, nano=0)),
                    status=<StopOrderStatusOption.STOP_ORDER_STATUS_ACTIVE: 2>,
                    exchange_order_type=
                        <ExchangeOrderType.EXCHANGE_ORDER_TYPE_LIMIT: 2>,
                    exchange_order_id=None
                )
            ]
        )
        """  # }}}
        logger.debug(f"Tinkoff.getStopOrders(account={account})")

        try:
            response = await self.__client.stop_orders.get_stop_orders(
                account_id=account.meta.id
            )
            logger.debug(f"Tinkoff.getStopOrders: Response='{response}'")
        except ti.exceptions.InvestError:
            logger.error("Tinkoff.getStopOrders: Error={err}")
            return None

        orders = list()
        for i in response.stop_orders:
            asset_id = await InstrumentId.byFigi(i.figi)
            await asset_id.cacheInfo()
            order = StopOrder(
                account_name=account.name,
                direction=self.__ti_to_av(i.direction),
                asset_id=asset_id,
                lots=i.lots_requested,
                quantity=i.lots_requested * asset_id.lot,
                stop_price=self.__ti_to_av(i.stop_price),
                exec_price=self.__ti_to_av(i.price),
                status=self.__ti_to_av(i.status),
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
    async def getOperations(self, account: Account) -> list[Operation]: ...
    async def getPositions(self, account: Account) -> list[Postition]: ...
    async def getDetailedPortfolio(self, account: Account) -> Portfolio: ...
    async def getWithdrawLimits(self, account: Account): ...
    async def getOrderOperation(self, order: Order) -> Order.Status: ...

    async def syncOrder(self, order: Order, account: Account):  # {{{
        """response example # {{{
        OrderState(
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
        response: ti.OrderState = await self.__getOrderState(order, account)

        order.broker_id = response.order_id
        order.meta = str(response)
        order.exec_lots = response.lots_executed
        status = self.__ti_to_av(response.execution_report_status)
        await order.setStatus(status)

    # }}}
    async def postMarketOrder(self, order: Order, account: Account):  # {{{
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
                    2024, 7, 4, 12, 39, 26, 693922, tzinfo=datetime.timezone.utc
                )
            )
        )'
        """  # }}}
        logger.debug(f"Tinkoff.postMarketOrder({order})")

        response: ti.PostOrderResponse = (
            await self.__client.orders.post_order(
                account_id=account.meta.id,
                order_type=self.__av_to_ti(order, ti.OrderType),
                direction=self.__av_to_ti(order, ti.OrderDirection),
                figi=order.asset_id.figi,
                quantity=order.lots,
                order_id=str(order.order_id),
            )
        )
        logger.debug(f"Tinkoff.postMarketOrder: Response='{response}'")

        # save broker_id, save 'response' in order.meta and
        # setStatus -> side effect: update in db and emit signals
        order.broker_id = response.order_id
        order.meta = str(response)
        status = self.__ti_to_av(response.execution_report_status)
        await order.setStatus(status)

        return True

    # }}}
    async def postLimitOrder(self, order: Order, account: Account):  # {{{
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

        response: ti.PostOrderResponse = (
            await self.__client.orders.post_order(
                order_type=self.__av_to_ti(order, ti.OrderType),
                account_id=account.meta.id,
                direction=self.__av_to_ti(order, ti.OrderDirection),
                figi=order.asset_id.figi,
                quantity=order.lots,
                price=Tinkoff.__av_to_ti(order.price, ti.Quotation),
                order_id=str(order.order_id),
            )
        )
        logger.debug(f"Tinkoff.postLimitOrder: Response='{response}'")

        # save broker_id, save 'response' in order.meta and
        # setStatus -> side effect: update in db and emit signals
        order.broker_id = response.order_id
        order.meta = str(response)
        status = self.__ti_to_av(response.execution_report_status)
        await order.setStatus(status)

        return True

    # }}}
    async def postStopOrder(self, order: StopOrder, account: Account):  # {{{
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
        try:
            response = await self.__client.stop_orders.post_stop_order(
                stop_order_type=self.__av_to_ti(order, ti.StopOrderType),
                account_id=account.meta.id,
                direction=self.__av_to_ti(order, ti.StopOrderDirection),
                figi=order.asset_id.figi,
                quantity=order.lots,
                price=self.__av_to_ti(order.exec_price, ti.Quotation),
                stop_price=self.__av_to_ti(order.stop_price, ti.Quotation),
                # order_id=str(order.order_id),
                expiration_type=self.__av_to_ti(
                    order, ti.StopOrderExpirationType
                ),
                # expire_date=
            )
            logger.debug(f"Tinkoff.postStopOrder: Response='{response}'")
        except ti.exceptions.RequestError as err:
            logger.error(f"{err}")
            return False

        order.broker_id = response.stop_order_id
        order.meta = str(response)
        await order.setStatus(Order.Status.PENDING)

        return True

    # }}}
    async def postStopLoss(self, order: Order, account: Account): ...
    async def postTakeProfit(self, order: Order, account: Account): ...
    async def cancelLimitOrder(  # {{{
        self, order: Order, account: Account
    ) -> bool:
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

        response: ti.CancelOrderResponse = (
            await self.__client.orders.cancel_order(
                account_id=account.meta.id,
                order_id=order.broker_id,
            )
        )
        logger.debug(f"Tinkoff.cancelLimitOrder: Response='{response}'")

        await self.syncOrder(order, account)
        return order.status == Order.Status.CANCELED

    # }}}
    async def cancelStopOrder(self, order: Order, account: Account):  # {{{
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

        try:
            response = await self.__client.stop_orders.cancel_stop_order(
                account_id=account.meta.id,
                stop_order_id=order.broker_id,
            )
            logger.debug(f"Tinkoff.cancelStopOrder: Response='{response}'")
        except ti.exceptions.AioRequestError as err:
            logger.error(err)
            if err.code == StatusCode.NOT_FOUND:
                # TODO: подумать как лучше всего тут действовать
                raise BrokerError(
                    f"Tinkoff stop-order '{order.order_id}' - not found"
                )
                return False  # ???

        await order.setStatus(Order.Status.CANCELED)
        return True

    # }}}
    async def createBarStream(self, account: Account) -> bool: ...
    async def createTransactionStream(self, account: Account) -> bool: ...
    async def createOperationStream(self, account: Account) -> bool: ...
    async def createPositionStream(self, account: Account) -> bool: ...
    async def subscribe(self, asset: Asset, data_type: DataType) -> bool: ...

    @classmethod  # getLastPrice  # {{{
    def getLastPrice(
        cls,
        asset_id: InstrumentId,
    ) -> float | None:
        with ti.Client(cls.TOKEN) as client:
            try:
                response = client.market_data.get_last_prices(
                    figi=[
                        asset_id.figi,
                    ]
                )
                last_price = response.last_prices[0].price
                last_price = float(quotation_to_decimal(last_price))
            except ti.exceptions.AioRequestError as err:
                logger.error(err)
                return None

            return last_price

    # }}}
    async def getHistoricalBars(  # {{{
        self,
        asset: Asset,
        timeframe: TimeFrame,
        begin: datetime,
        end: datetime,
    ) -> list[Bar]:
        pass
        ...

    # }}}

    async def __runConnectionCycle(self):  # {{{
        logger.debug("Tinkoff.__runConnectionCycle()")

        async with ti.AsyncClient(self.TOKEN, target=self.TARGET) as client:
            response = await client.users.get_accounts()
            if not response:
                return

            self.__client = client
            self.__connected = True
            while self.__connected:
                await asyncio.sleep(1)

    # }}}
    async def __getOrderState(self, order, account):  # {{{
        """response example # {{{
        OrderState(
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
        logger.debug(f"Tinkoff.__getOrderState({order})")

        response: ti.OrderState = await self.__client.orders.get_order_state(
            account_id=account.meta.id,
            order_id=order.broker_id,
        )
        logger.debug(f"Tinkoff.__getOrderState: Response='{response}'")

        return response

    # }}}

    @staticmethod  # __ti_to_av  # {{{
    def __ti_to_av(obj: Any):
        logger.debug(f"Tinkoff.__ti_to_av({obj})")

        class_name = obj.__class__.__name__
        match class_name:
            case "MoneyValue":
                return Tinkoff.__tiMoneyValue_to_avPrice(obj)
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
            case _:
                raise BrokerError(
                    f"Tinkoff fail convert: unknown object='{obj}', "
                    f"type='{type(obj)}'"
                )

    # }}}
    @staticmethod  # __tiMoneyValue_to_avPrice{{{
    def __tiMoneyValue_to_avPrice(ti_money_value):
        price = float(money_to_decimal(ti_money_value))
        return price

    # }}}
    @staticmethod  # __tiOrderType_to_avType  # {{{
    def __tiOrderType_to_avType(tinkoff_order_type):
        logger.debug("Tinkoff.__tiOrderDirection_to_avType()")

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
        logger.debug("Tinkoff.__tiOrderDirection_to_avType()")

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
        logger.debug("Tinkoff.__tiOrderDirection_to_avOrderDirection()")

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
        logger.debug("Tinkoff.__tiOrderDirection_to_avOrderDirection()")

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
            "Tinkoff.__tiOrderExecutionReportStatus_to_avOrderStatus()"
        )

        # tinkoff limit order statuses
        t = ti.OrderExecutionReportStatus
        statuses = {
            t.EXECUTION_REPORT_STATUS_UNSPECIFIED: Order.Status.UNDEFINE,
            t.EXECUTION_REPORT_STATUS_FILL: Order.Status.FILLED,
            t.EXECUTION_REPORT_STATUS_REJECTED: Order.Status.REJECTED,
            t.EXECUTION_REPORT_STATUS_CANCELLED: Order.Status.CANCELED,
            t.EXECUTION_REPORT_STATUS_NEW: Order.Status.POSTED,
            t.EXECUTION_REPORT_STATUS_PARTIALLYFILL: Order.Status.PARTIAL,
        }
        avin_status = statuses[tinkoff_status]

        return avin_status

    # }}}
    @staticmethod  # __tiStopOrderStatusOption_to_avStatus  # {{{
    def __tiStopOrderStatusOption_to_avStatus(tinkoff_status):
        logger.debug("Tinkoff.__tiStopOrderStatusOption_to_avStatus()")

        # tinkoff stop order statuses
        t = ti.StopOrderStatusOption
        statuses = {
            t.STOP_ORDER_STATUS_UNSPECIFIED: Order.Status.UNDEFINE,
            t.STOP_ORDER_STATUS_ALL: Order.Status.UNDEFINE,  # XXX: что это?
            t.STOP_ORDER_STATUS_ACTIVE: Order.Status.PENDING,  # XXX: rename ACTIVE?
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
    @staticmethod  # __av_to_ti  # {{{
    def __av_to_ti(av_obj: Any, ti_class: ClassVar):
        logger.debug(f"Tinkoff.__av_to_ti({ti_class}, {av_obj})")

        class_name = ti_class.__name__
        match class_name:
            case "Quotation":
                return Tinkoff.__avPrice_to_tiQuotation(av_obj)
            case "OrderType":
                return Tinkoff.__avOrder_to_OrderType(av_obj)
            case "StopOrderType":
                return Tinkoff.__avOrder_to_StopOrderType(av_obj)
            case "OrderDirection":
                return Tinkoff.__avOrder_to_OrderDirection(av_obj)
            case "StopOrderDirection":
                return Tinkoff.__avOrder_to_StopOrderDirection(av_obj)
            case "StopOrderExpirationType":
                return Tinkoff.__avOrder_to_StopOrderExpirationType(av_obj)
            case _:
                raise BrokerError(
                    f"Tinkoff fail extract: ti_class='{ti_class}', "
                    f"av_obj='{av_obj}'"
                )

    # }}}
    @staticmethod  # __avPrice_to_tiQuotation()  # {{{
    def __avPrice_to_tiQuotation(price):
        if price is None:
            return None
        else:
            quotation = decimal_to_quotation(Decimal(price))
            return quotation

    # }}}
    @staticmethod  # __avOrder_to_OrderType  # {{{
    def __avOrder_to_OrderType(order: Order):
        t = ti.OrderType

        if order.type == Order.Type.MARKET:
            return t.ORDER_TYPE_MARKET

        if order.type == Order.Type.LIMIT:
            return t.ORDER_TYPE_LIMIT

    # }}}
    @staticmethod  # __avOrder_to_StopOrderType  # {{{
    def __avOrder_to_StopOrderType(order: Order):
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
    @staticmethod  # __avOrder_to_OrderDirection  # {{{
    def __avOrder_to_OrderDirection(order: Order):
        assert order.type in (Order.Type.MARKET, Order.Type.LIMIT)

        if order.direction == Order.Direction.BUY:
            return ti.OrderDirection.ORDER_DIRECTION_BUY

        if order.direction == Order.Direction.SELL:
            return ti.OrderDirection.ORDER_DIRECTION_SELL

        return ti.OrderDirection.ORDER_DIRECTION_UNSPECIFIED

    # }}}
    @staticmethod  # __avOrder_to_StopOrderDirection  # {{{
    def __avOrder_to_StopOrderDirection(order: Order):
        assert order.type in (
            Order.Type.STOP,
            Order.Type.WAIT,
            Order.Type.STOP_LOSS,
            Order.Type.TAKE_PROFIT,
        )

        if order.direction == Order.Direction.BUY:
            return ti.StopOrderDirection.STOP_ORDER_DIRECTION_BUY

        if order.direction == Order.Direction.SELL:
            return ti.StopOrderDirection.STOP_ORDER_DIRECTION_SELL

        return StopOrderDirection.STOP_ORDER_DIRECTION_UNSPECIFIED

    # }}}
    @staticmethod  # __avOrder_to_StopOrderExpirationType  # {{{
    def __avOrder_to_StopOrderExpirationType(order: Order):
        t = ti.StopOrderExpirationType

        if order.type == Order.Type.STOP:
            return t.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL
        if order.type == Order.Type.STOP_LOSS:
            return t.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL
        if order.type == Order.Type.TAKE_PROFIT:
            return t.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL

    # }}}
