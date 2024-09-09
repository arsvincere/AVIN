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
    broker = Tinkoff()
    await broker.connect()
    assert broker.isConnect()

    accounts = await broker.getAllAccounts()
    assert len(accounts) == 4

    account = await broker.getAccount("Alex")
    assert account.name == "Alex"
    assert account.broker.__class__.__name__ == "Tinkoff"
    assert account.meta is not None

    # get money
    money = await broker.getMoney(account)
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
    await broker.postMarketOrder(order, account)
    assert order.status in (Order.Status.POSTED, Order.Status.FILLED)
    order.order_id = Id.newId()
    order.direction = Order.Direction.SELL
    await broker.postMarketOrder(order, account)
    assert order.status in (Order.Status.POSTED, Order.Status.FILLED)

    # post LimitOrder then cancel
    last_price = await broker.getLastPrice(mvid)
    order_id = Id.newId()
    limit_order = LimitOrder(
        account_name=account.name,
        direction=Order.Direction.BUY,
        asset_id=mvid.ID,
        lots=1,
        quantity=1 * mvid.lot,
        price=last_price - 10,
        status=Order.Status.NEW,
        order_id=order_id,
    )
    await broker.postLimitOrder(limit_order, account)
    assert limit_order.status == Order.Status.POSTED
    successful = await broker.cancelLimitOrder(limit_order, account)
    assert successful

    # disconnect
    await broker.disconnect()
    assert not broker.isConnect()
