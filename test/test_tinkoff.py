#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


import pytest

from avin import *


@pytest.mark.asyncio
async def test_Tinkoff(event_loop):
    await Tinkoff.connect()
    assert Tinkoff.isConnect()

    accounts = await Tinkoff.getAllAccounts()
    assert len(accounts) == 4

    account = await Tinkoff.getAccount("Alex")
    assert account.name == "Alex"
    assert account.broker.name == "Tinkoff"
    assert account.meta is not None

    # get money
    money = await Tinkoff.getMoney(account)
    assert isinstance(money, float)
    assert money > 0

    # post MarketOrder buy then sell
    mvid = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "MVID")
    await mvid.cacheInfo()
    order_id = Id.newId()
    order = MarketOrder(
        account_name=account.name,
        direction=Order.Direction.BUY,
        asset_id=mvid.ID,
        lots=1,
        quantity=1 * mvid.lot,
        status=Order.Status.NEW,
        order_id=order_id,
    )
    await Tinkoff.postMarketOrder(account, order)
    assert order.status in (Order.Status.POSTED, Order.Status.FILLED)
    order.order_id = Id.newId()
    order.direction = Order.Direction.SELL
    await Tinkoff.postMarketOrder(account, order)
    assert order.status in (Order.Status.POSTED, Order.Status.FILLED)

    # get order operation
    operation = await Tinkoff.getOrderOperation(account, order)
    assert operation.asset_id == order.asset_id
    assert operation.lots == order.lots

    # post LimitOrder buy
    last_price = Tinkoff.getLastPrice(mvid)
    order_id = Id.newId()
    limit_order = LimitOrder(
        account_name=account.name,
        direction=Order.Direction.BUY,
        asset_id=mvid.ID,
        lots=1,
        quantity=1 * mvid.lot,
        price=round_price(last_price - 10, mvid.min_price_step),
        status=Order.Status.NEW,
        order_id=order_id,
    )
    await Tinkoff.postLimitOrder(account, limit_order)
    assert limit_order.status == Order.Status.POSTED

    # get it limit order
    received_order = await Tinkoff.getLimitOrders(account)
    received_order = received_order[0]
    assert received_order.type == limit_order.type
    assert received_order.account_name == limit_order.account_name
    assert received_order.direction == limit_order.direction
    assert received_order.asset_id == limit_order.asset_id
    assert received_order.lots == limit_order.lots
    assert received_order.quantity == limit_order.quantity
    # assert received_order.price == limit_order.price  # TODO: correct round
    assert received_order.order_id == limit_order.order_id
    assert received_order.broker_id == limit_order.broker_id

    # cancel limit order buy
    successful = await Tinkoff.cancelLimitOrder(account, limit_order)
    assert successful

    # post LimitOrder sell
    last_price = Tinkoff.getLastPrice(mvid)
    order_id = Id.newId()
    limit_order = LimitOrder(
        account_name=account.name,
        direction=Order.Direction.SELL,
        asset_id=mvid.ID,
        lots=1,
        quantity=1 * mvid.lot,
        price=round_price(last_price + 10, mvid.min_price_step),
        status=Order.Status.NEW,
        order_id=order_id,
    )
    await Tinkoff.postLimitOrder(account, limit_order)
    assert limit_order.status == Order.Status.POSTED

    # get it limit order
    received_order = await Tinkoff.getLimitOrders(account)
    received_order = received_order[0]
    assert received_order.type == limit_order.type
    assert received_order.account_name == limit_order.account_name
    assert received_order.direction == limit_order.direction
    assert received_order.asset_id == limit_order.asset_id
    assert received_order.lots == limit_order.lots
    assert received_order.quantity == limit_order.quantity
    # assert received_order.price == limit_order.price # TODO: correct round
    assert received_order.order_id == limit_order.order_id
    assert received_order.broker_id == limit_order.broker_id

    # cancel limit order sell
    successful = await Tinkoff.cancelLimitOrder(account, limit_order)
    assert successful

    # post stop order buy
    last_price = Tinkoff.getLastPrice(mvid)
    price = round_price(last_price - 10, mvid.min_price_step)
    order_id = Id.newId()
    stop_order = StopOrder(
        account_name=account.name,
        direction=Order.Direction.BUY,
        asset_id=mvid.ID,
        lots=1,
        quantity=1 * mvid.lot,
        stop_price=price,
        exec_price=price,
        status=Order.Status.NEW,
        order_id=order_id,
    )

    await Tinkoff.postStopOrder(account, stop_order)
    assert stop_order.status == Order.Status.PENDING

    received_order = await Tinkoff.getStopOrders(account)
    received_order = received_order[0]

    assert received_order.type == stop_order.type
    assert received_order.account_name == stop_order.account_name
    assert received_order.direction == stop_order.direction
    assert received_order.asset_id == stop_order.asset_id
    assert received_order.lots == stop_order.lots
    assert received_order.quantity == stop_order.quantity
    # assert received_order.stop_price == stop_order.stop_price # TODO: correct round
    # assert received_order.exec_price == stop_order.exec_price # TODO: correct round
    assert received_order.broker_id == stop_order.broker_id
    assert received_order.order_id is None

    await Tinkoff.cancelStopOrder(account, stop_order)
    assert stop_order.status == Order.Status.CANCELED

    # post stop order sell
    last_price = Tinkoff.getLastPrice(mvid)
    price = round_price(last_price + 10, mvid.min_price_step)

    order_id = Id.newId()
    stop_order = StopOrder(
        account_name=account.name,
        direction=Order.Direction.SELL,
        asset_id=mvid.ID,
        lots=1,
        quantity=1 * mvid.lot,
        stop_price=price,
        exec_price=price,
        status=Order.Status.NEW,
        order_id=order_id,
    )

    await Tinkoff.postStopOrder(account, stop_order)
    assert stop_order.status == Order.Status.PENDING

    await Tinkoff.cancelStopOrder(account, stop_order)
    assert stop_order.status == Order.Status.CANCELED

    # get operations, last 2 operation - buy/sell MVID
    from_ = now() - ONE_MINUTE
    to = now()
    operations = await Tinkoff.getOperations(account, from_, to)
    assert operations[0].asset_id == mvid.ID
    assert operations[1].asset_id == mvid.ID

    # disconnect
    await Tinkoff.disconnect()
    assert not Tinkoff.isConnect()
