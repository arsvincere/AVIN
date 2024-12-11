#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

import pytest
from avin import *


@pytest.mark.asyncio  # test_Strategy  # {{{
async def test_Strategy():
    # don't test in holidays
    if WeekDays.isHoliday(now().weekday()):
        return

    await Tinkoff.connect()
    if not Tinkoff.isConnect():
        assert False, "Fail to connect"

    # create asset, account, trade list with active trades
    asset = await Asset.fromTicker(
        Exchange.MOEX, Instrument.Type.SHARE, "MVID"
    )
    account = await Tinkoff.getAccount("Alex")
    tlist = TradeList("_unittest")
    await TradeList.save(tlist)
    active_trades = tlist.selectStrategy("Every", "minute")

    strategy = await Strategy.load("Every", "minute")
    strategy.setAccount(account)
    strategy.setTradeList(active_trades)

    await Tinkoff.createTransactionStream(account)
    await Tinkoff.startTransactionStream()

    assert strategy.name == "Every"
    assert strategy.version == "minute"
    assert strategy.account == account
    assert strategy.config is not None
    assert strategy.timeframe_list is not None
    assert strategy.active_trades is not None
    assert Strategy.path(strategy) == Cmd.path(
        Usr.STRATEGY, "Every", "minute.py"
    )
    assert Strategy.dirPath(strategy.name) == Cmd.path(Usr.STRATEGY, "Every")

    # создаем трейд
    trade = await strategy.createTrade(
        now(),
        Trade.Type.LONG,
        asset,
    )

    # создаем ордер
    order = await strategy.createMarketOrder(
        direction=Direction.BUY,
        instrument=asset,
        lots=1,
    )

    # связываем этот ордер с трейдом
    await trade.attachOrder(order)

    # постим этот ордер
    await strategy.postOrder(order)
    await asyncio.sleep(5)

    # ордер исполняется...
    assert order.status == Order.Status.EXECUTED

    # создаем и постим стоп лосс на 0.3%
    stop_loss = await strategy.createStopLoss(trade, stop_percent=0.3)
    await strategy.postOrder(stop_loss)
    await asyncio.sleep(2)

    # создаем и постим стоп лосс на 0.9%
    take_profit = await strategy.createTakeProfit(trade, take_percent=0.9)
    await strategy.postOrder(take_profit)
    await asyncio.sleep(2)

    await asyncio.sleep(5)
    await strategy.closeTrade(trade)

    # delete all
    await TradeList.delete(tlist)


# }}}
@pytest.mark.asyncio  # test_StrategyList  # {{{
async def test_StrategyList():
    s1 = await Strategy.load("Every", "minute")
    s2 = await Strategy.load("Every", "five")

    strategy_list = StrategyList("slist")
    assert strategy_list.name == "slist"

    # add
    strategy_list.add(s1)
    assert len(strategy_list) == 1
    strategy_list.add(s2)
    assert len(strategy_list) == 2
    assert strategy_list.strategys == [s1, s2]

    # remove
    strategy_list.remove(s1)
    assert len(strategy_list) == 1

    # clear
    strategy_list.clear()
    assert len(strategy_list) == 0

    # property setter name
    strategy_list.name = "new_name"
    assert strategy_list.name == "new_name"

    # property setter strategys
    strategy_list.strategys = [s2, s1]
    assert strategy_list.strategys == [s2, s1]

    # iter
    for i in strategy_list:
        assert isinstance(i, Strategy)

    # in
    assert s1 in strategy_list
    assert s2 in strategy_list
    strategy_list.clear()
    assert s1 not in strategy_list
    assert s2 not in strategy_list


# }}}
@pytest.mark.asyncio  # test_StrategySetNode  # {{{
async def test_StrategySetNode():
    item = StrategySetNode(
        "Every", "minute", "BBG004730N88", long=True, short=True
    )
    assert item.strategy == "Every"
    assert item.version == "minute"
    assert item.figi == "BBG004730N88"
    assert item.long
    assert item.short


# }}}
@pytest.mark.asyncio  # test_StrategySet  # {{{
async def test_StrategySet():
    afks = await Asset.fromTicker(Exchange.MOEX, Asset.Type.SHARE, "AFKS")
    aflt = await Asset.fromTicker(Exchange.MOEX, Asset.Type.SHARE, "AFLT")
    alrs = await Asset.fromTicker(Exchange.MOEX, Asset.Type.SHARE, "ALRS")
    sber = await Asset.fromTicker(Exchange.MOEX, Asset.Type.SHARE, "SBER")

    # create items
    item1 = StrategySetNode(
        "Every", "minute", "BBG004S68614", long=True, short=False
    )
    item2 = StrategySetNode(
        "Every", "minute", "BBG004S683W7", long=False, short=True
    )
    item3 = StrategySetNode(
        "Every", "five", "BBG004S68B31", long=True, short=True
    )
    item4 = StrategySetNode(
        "Every", "five", "BBG004730N88", long=True, short=True
    )

    # create strategy set
    s_set = StrategySet(name="blablabla")
    assert s_set.name == "blablabla"

    # add items
    assert len(s_set) == 0
    s_set.add(item1)
    assert len(s_set) == 1
    s_set.add(item2)
    s_set.add(item3)
    s_set.add(item4)
    assert len(s_set) == 4

    # create asset list
    asset_list = await s_set.createAssetList()
    assert len(asset_list) == 4
    assert afks in asset_list
    assert aflt in asset_list
    assert alrs in asset_list
    assert sber in asset_list

    # create strategy list
    strategy_list = await s_set.createStrategyList()
    assert len(strategy_list) == 2
    assert strategy_list.find("Every", "minute")
    assert strategy_list.find("Every", "five")
    assert not strategy_list.find("Bugaga", "v5")

    # save
    await StrategySet.save(s_set)

    # load
    loaded = await StrategySet.load("blablabla")
    assert loaded.name == s_set.name
    assert len(loaded) == len(s_set)

    # delete
    await StrategySet.delete(s_set)


# }}}
