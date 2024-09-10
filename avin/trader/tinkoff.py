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
from typing import Any

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
    StopOrder,
    TimeFrame,
    TransactionEvent,
)
from avin.data import AssetType, Exchange, InstrumentId
from avin.exceptions import BrokerError
from avin.utils import AsyncSignal, Cmd, logger

# TODO: сделай единообразным поведение методов getLimitOrders, getStopOrders,
# если уж перехватываешь исключение то везде

# TODO: проверить возвращаемые значения, сделать нормальные bool везде
# где надо. А где надо?


class Tinkoff(Broker):
    name = "Tinkoff"
    TARGET = ti.constants.INVEST_GRPC_API
    TOKEN = Cmd.read(Usr.TINKOFF_TOKEN).strip()

    new_bar = AsyncSignal(NewBarEvent)
    new_transaction = AsyncSignal(TransactionEvent)
    # order_filled = AsyncSignal(OrderEvent)  # XXX: ?????

    def __init__(self):  # {{{
        logger.debug("Tinkoff.__init__()")
        Broker.__init__(self)
        self.__accounts = list()

        self.__connect_task = None
        self.__client = None
        self.__connected = False

        self.__wait_data_task = None
        self.__data_subscriptions = list()
        self.__data_stream = None
        self.__data_stream_is_active = False

        self.__transaction_task = None
        self.__transaction_stream = None
        self.__transaction_stream_is_active = False

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

        await self.stopDataStream()
        await self.stopTransactionStream()

        # XXX: а может быть startConnect & stopConnect ???
        self.__connect_task.cancel()
        self.__client = None
        self.__connected = False

        self.__accounts.clear()

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
    async def getOperations(  # {{{
        self, account: Account, from_: datetime, to: datetime
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
        assert isinstance(from_, datetime)
        assert isinstance(to, datetime)

        # request operations
        response: ti.OperationsResponse = (
            await self.__client.operations.get_operations(
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
                await asset_id.cacheInfo()

                op = Operation(
                    account_name=account.name,
                    dt=i.date,
                    direction=self.__ti_to_av(i.operation_type),
                    asset_id=asset_id,
                    lots=int(i.quantity / asset_id.lot),
                    quantity=i.quantity,
                    price=self.__ti_to_av(i.price),
                    amount=self.__ti_to_av(i.price),
                    commission=None,
                    operation_id=None,
                    order_id=None,
                    trade_id=None,
                    meta=str(i),
                )
                operations.append(op)

        return operations

    # }}}
    async def getPositions(self, account: Account) -> list[Postition]:  # {{{
        logger.debug(f"Tinkoff.getPositions({account})")
        response: ti.PositionsResponse = (
            await self.__client.operations.get_positions(
                account_id=account.meta.id
            )
        )
        logger.debug(f"Tinkoff.getPositions: Response='{response}'")
        return response

    # }}}
    async def getDetailedPortfolio(  # {{{
        self, account: Account
    ) -> Portfolio:
        logger.debug(f"Tinkoff.getDetailedPortfolio({account})")
        response: ti.PortfolioResponse = (
            await self.__client.operations.get_portfolio(
                account_id=account.meta.id
            )
        )
        logger.debug(f"Tinkoff.getDetailedPortfolio: Response='{response}'")
        return response

    # }}}
    async def getWithdrawLimits(self, account: Account):  # {{{
        logger.debug(f"Tinkoff.getWithdrawLimits({account})")
        response: ti.WithdrawLimitsResponse = (
            await self.__client.operations.get_withdraw_limits(
                account_id=account.meta.id
            )
        )
        logger.debug(f"Tinkoff.getWithdrawLimits: Response='{response}'")
        return response

    # }}}
    async def getOrderOperation(  # {{{
        self, account: Account, order: Order
    ) -> Order.Status:
        response: ti.OrderState = await self.__getOrderState(account, order)
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

    async def syncOrder(self, account: Account, order: Order):  # {{{
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
        response: ti.OrderState = await self.__getOrderState(account, order)

        order.broker_id = response.order_id
        order.exec_lots = response.lots_executed
        order.meta = str(response)
        status = self.__ti_to_av(response.execution_report_status)
        await order.setStatus(status)

    # }}}
    async def postMarketOrder(self, account: Account, order: Order):  # {{{
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
    async def postLimitOrder(self, account: Account, order: Order):  # {{{
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
    async def postStopOrder(self, account: Account, order: Order):  # {{{
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
    async def postStopLoss(self, account: Account, order: Order):  # {{{
        return self.postStopOrder(account, order)

    # }}}
    async def postTakeProfit(self, account: Account, order: Order):  # {{{
        return self.postStopOrder(account, order)

    # }}}
    async def cancelLimitOrder(  # {{{
        self, account: Account, order: Order
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

        await self.syncOrder(account, order)
        return order.status == Order.Status.CANCELED

    # }}}
    async def cancelStopOrder(self, account: Account, order: Order):  # {{{
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

    async def createDataStream(  # {{{
        self, asset: Asset, data_type: DataType
    ):
        logger.info(f"  - Tinkoff.subscribe({asset}, {data_type})")

        if not self.__data_stream:
            await self.__createMarketDataStream()

        figi = asset.figi
        interval = self.__av_to_ti(data_type, ti.SubscriptionInterval)
        candle_subscription = ti.CandleInstrument(
            figi=figi, interval=interval
        )
        self.__data_subscriptions.append(candle_subscription)
        self.__data_stream.candles.waiting_close().subscribe(
            [candle_subscription]
        )

    # }}}
    async def createTransactionStream(self, account: Account) -> None:  # {{{
        logger.info(
            f":: Tinkoff create transaction stream (account='{account}')"
        )

        self.__transaction_stream = self.__client.orders_stream.trades_stream(
            accounts=[
                account.meta.id,
            ]
        )

    # }}}
    async def createPositionSteam(self, account: Account):  # {{{
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
        stream = self.__client.operations_stream.positions_stream(
            accounts=[
                account.meta.id,
            ]
        )
        return stream

    # }}}

    async def startDataStream(self) -> bool:
        logger.info(":: Tinkoff try start data stream")
        self.__wait_data_task = asyncio.create_task(self.__waitData())

        seconds_elapsed = 0
        while not self.__data_stream_is_active:
            logger.info(f"  - waiting data... ({seconds_elapsed} sec)")
            await asyncio.sleep(1)
            seconds_elapsed += 1
            if seconds_elapsed == 5:
                logger.error("  - fail to start data stream Tinkoff :(")
                return False

        logger.info("  - data stream started!")
        return True

    async def stopDataStream(self):
        self.__wait_data_task.cancel()
        self.__data_stream.unsubscribe(self.__data_subscriptions)

        self.__data_stream.stop()
        self.__data_stream = None
        self.__data_subscriptions.clear()
        self.__data_stream_is_active = False
        logger.info(":: Tinkoff data stream stopped")

    async def startTransactionStream(self):
        logger.info(":: Tinkoff try start transaction stream")
        self.__transaction_task = asyncio.create_task(
            self.__waitTransaction()
        )
        self.__transaction_stream_is_active = True

    async def stopTransactionStream(self):
        self.__transaction_task.cancel()
        self.__transaction_stream = None
        self.__transaction_stream_is_active = False
        logger.info(":: Tinkoff try start transaction stream")

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
    async def __getOrderState(self, account: Account, order: Order):  # {{{
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
        initial_commission=MoneyValue(currency='rub', units=0, nano=90000000),
        executed_commission=MoneyValue(currency='rub', units=0, nano=80000000),
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

        response: ti.OrderState = await self.__client.orders.get_order_state(
            account_id=account.meta.id,
            order_id=order.broker_id,
        )
        logger.debug(f"Tinkoff.__getOrderState: Response='{response}'")

        return response

    # }}}
    async def __createMarketDataStream(self) -> bool:  # {{{
        logger.debug("Tinkoff.__createMarketDataStream()")
        self.__data_stream: ti.async_services.AsyncMarketDataStreamManager = (
            self.__client.create_market_data_stream()
        )
        logger.debug(
            f"Tinkoff.__createMarketDataStream() -> {market_data_stream} "
        )

    # }}}
    async def __waitData(self):  # {{{
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
        logger.debug("async Tinkoff.__waitData()")
        async for response in self.__data_stream:
            logger.debug(f"  Tinkoff.__waitData: Response='{response}'")
            self.__data_stream_is_active = True
            if response.candle:
                figi = response.candle.figi
                timeframe = self.__ti_to_av(response.candle.interval)
                bar = self.__ti_to_av(response.candle)
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
        self.__data_stream_is_active = False  # XXX: ???

    # }}}
    async def __waitTransaction(self):  # {{{
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
        logger.debug("async Tinkoff.__waitTransaction()")

        async for response in self.__transaction_stream:
            logger.debug(
                f"  Tinkoff.__waitTransaction: Response='{response}'"
            )

            event: TransactionEvent = self.__ti_to_av(response)
            await Tinkoff.new_transaction.async_emit(event)

            # TODO: логика
            # получили транзакцию.  известен ордер ид и транзакции
            # можно эту транзакцию отправить сигналом.
            # принявшему хорошо бы эту транзакцию в базу записать
            # далее аккаунт например ловит этот сигнал
            # по брокер ИД ордера, находит мой ордер
            # запрашивает ордер статус...
            # если ордер статус выполнен
            #   запрашивает операцию по трейду
            #   делает сигнал ордер исполнен
            # если ордер не выполнен
            #   ставим статус ордер партиали
            #   обновляем ордер в базе
            #   спим дальше

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
            case "OperationType":
                return Tinkoff.__tiOperationType_to_avOperationDirection(obj)
            case "SubscriptionInterval":
                return Tinkoff.__tiSubscriptionInterval_to_avTimeFrame(obj)
            case "Candle":
                return Tinkoff.__tiCandle_to_avBar(obj)
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
    @staticmethod  # __tiOperationType_to_avOperationDirection  # {{{
    def __tiOperationType_to_avOperationDirection(ti_operation_type):
        logger.debug("Tinkoff.__tiOperationType_to_avOperationDirection()")

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
        logger.debug("Tinkoff.__tiSubscriptionInterval_to_avTimeFrame()")

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
        logger.debug("Tinkoff.__tiCandle_to_avBar()")
        open = float(quotation_to_decimal(candle.open))
        close = float(quotation_to_decimal(candle.close))
        high = float(quotation_to_decimal(candle.high))
        low = float(quotation_to_decimal(candle.low))
        vol = candle.volume
        dt = candle.time

        bar = Bar(dt, open, high, low, close, vol)
        return bar

    # }}}
    @staticmethod  # __tiTradesStreamResponse_to_avTransactionEvent
    def __tiTradesStreamResponse_to_avTransactionEvent(stream_response):
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
        # FIX: AFK получить имя аккаунта по его ИД, поиск в self.__accounts
        # преобразовать direction
        # преобразовать transactions
        account_id = stream_response.order_trades.account_id  # -> name
        order_broker_id = stream_response.order_trades.order_id
        direction = stream_response.order_trades.direction  # ->
        figi = stream_response.order_trades.figi
        transactions = stream_response.order_trades.trades

        event = TransactionEvent(
            account_id, order_broker_id, direction, figi, transactions
        )
        return event

    @staticmethod  # __av_to_ti  # {{{
    def __av_to_ti(av_obj: Any, ti_class: ClassVar):
        logger.debug(f"Tinkoff.__av_to_ti({ti_class}, {av_obj})")

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
                return Tinkoff.__avDataType_to_tiSubscriptionInterval(av_obj)
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
    @staticmethod  # __avOrder_to_tiOrderType  # {{{
    def __avOrder_to_tiOrderType(order: Order):
        t = ti.OrderType

        if order.type == Order.Type.MARKET:
            return t.ORDER_TYPE_MARKET

        if order.type == Order.Type.LIMIT:
            return t.ORDER_TYPE_LIMIT

    # }}}
    @staticmethod  # __avOrder_to_tiStopOrderType  # {{{
    def __avOrder_to_tiStopOrderType(order: Order):
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
        assert order.type in (Order.Type.MARKET, Order.Type.LIMIT)

        if order.direction == Order.Direction.BUY:
            return ti.OrderDirection.ORDER_DIRECTION_BUY

        if order.direction == Order.Direction.SELL:
            return ti.OrderDirection.ORDER_DIRECTION_SELL

        return ti.OrderDirection.ORDER_DIRECTION_UNSPECIFIED

    # }}}
    @staticmethod  # __avOrder_to_tiStopOrderDirection  # {{{
    def __avOrder_to_tiStopOrderDirection(order: Order):
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
    @staticmethod  # __avOrder_to_tiStopOrderExpirationType  # {{{
    def __avOrder_to_tiStopOrderExpirationType(order: Order):
        t = ti.StopOrderExpirationType

        if order.type == Order.Type.STOP:
            return t.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL
        if order.type == Order.Type.STOP_LOSS:
            return t.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL
        if order.type == Order.Type.TAKE_PROFIT:
            return t.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL

    # }}}
    @staticmethod  # __avDataType_to_tiSubscriptionInterval  # {{{
    def __avDataType_to_tiSubscriptionInterval(av_data_type):
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
        ti_interval = intervals[str(av_data_type)]
        return ti_interval

    # }}}
