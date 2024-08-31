#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from datetime import UTC, datetime

import pytest

from avin import *


def test_Range():  # {{{
    r = Range(5, 10)

    assert r.min == 5
    assert r.max == 10
    assert r.type == Range.Type.UNDEFINE
    assert r.bar is None

    assert r.percent() == 50.0
    assert r.abs() == 5.0
    assert r.mid() == 7.5

    assert 6 in r
    assert 6 in r.half(1)
    assert 6 in r.third(1)
    assert 6 in r.quarter(1)
    assert 8 in r[50:100]
    assert 11 not in r

    bar = Bar(now(), 10, 12, 9, 11, 1000)
    body = bar.body
    assert isinstance(body, Range)
    assert body.bar == bar
    assert body.type == Range.Type.BODY
    assert 11.0 in bar.body
    assert 11.1 not in bar.body

    assert 10.9 not in bar.body.quarter(1)
    assert 10.9 not in bar.body.quarter(2)
    assert 10.9 not in bar.body.quarter(3)
    assert 10.9 in bar.body.quarter(4)

    assert 11.9 not in bar.upper.third(1)
    assert 11.9 not in bar.upper.third(2)
    assert 11.9 in bar.upper.third(3)

    assert 9.9 not in bar.lower.half(1)
    assert 9.9 in bar.lower.half(2)


# }}}
def test_Bar():  # {{{
    bar = Bar("2023-01-01", 10, 12, 9, 11, 1000, chart=None)
    assert bar.dt == datetime.fromisoformat("2023-01-01")
    assert bar.open == 10
    assert bar.high == 12
    assert bar.low == 9
    assert bar.close == 11
    assert bar.vol == 1000

    assert isinstance(bar.range, Range)
    assert isinstance(bar.body, Range)
    assert isinstance(bar.upper, Range)
    assert isinstance(bar.lower, Range)

    assert 12.01 not in bar
    assert 11.99 in bar
    assert 9.01 in bar
    assert 8.99 not in bar

    assert 11.9 in bar.upper
    assert 10.9 not in bar.upper

    assert 9.0 in bar.lower
    assert 8.9 not in bar.lower

    assert 10.5 in bar.body
    assert 11.5 not in bar.body

    assert bar.isBull()
    assert not bar.isBear()

    bar.addFlag(Bar.Type.INSIDE)
    assert bar.isInside()
    assert not bar.isOutside()
    assert not bar.isOverflow()
    assert not bar.isExtremum()

    bar.removeFlag(Bar.Type.INSIDE)
    assert not bar.isInside()
    assert not bar.isOutside()
    assert not bar.isOverflow()
    assert not bar.isExtremum()

    bar.addFlag(Bar.Type.OVERFLOW)
    bar.addFlag(Bar.Type.EXTREMUM)
    assert not bar.isInside()
    assert not bar.isOutside()
    assert bar.isOverflow()
    assert bar.isExtremum()


# }}}
def test_TimeFrame():  # {{{
    D = TimeFrame("D")
    h1 = TimeFrame("1H")
    m5 = TimeFrame("5M")

    assert m5 < D
    assert m5 * 12 == h1
    assert h1 < "D"
    assert m5 > "1M"
    assert h1.minutes() == 60
    assert m5.minutes() == 5

    assert repr(h1) == "TimeFrame('1H')"
    assert str(h1) == "1H"

    assert m5.toDataType() == DataType.BAR_5M
    assert h1.toDataType() == DataType.BAR_1H
    assert D.toDataType() == DataType.BAR_D

    assert m5.toTimeDelta() == FIVE_MINUTE
    assert h1.toTimeDelta() == ONE_HOUR
    assert D.toTimeDelta() == ONE_DAY


# }}}


@pytest.mark.asyncio  # test_Chart  # {{{
async def test_Chart(event_loop):
    sber = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "SBER")
    tf = TimeFrame("1M")
    begin = datetime(2023, 8, 1, 0, 0, tzinfo=UTC)
    end = datetime(2023, 9, 1, 0, 0, tzinfo=UTC)
    bars = await Keeper.get(Bar, ID=sber, timeframe=tf, begin=begin, end=end)

    # create chart
    chart = Chart(sber.ID, tf, bars)
    assert chart.ID == sber.ID
    assert chart.ID.ticker == "SBER"
    assert chart.timeframe == tf

    assert chart.first.dt == datetime(2023, 8, 1, 6, 59, tzinfo=UTC)
    assert chart.last.dt == datetime(2023, 8, 31, 20, 49, tzinfo=UTC)

    assert chart[1].dt == datetime(2023, 8, 31, 20, 49, tzinfo=UTC)
    assert chart.now is None
    assert chart[0] is None

    # manipulation with head
    chart.setHeadIndex(15)
    assert chart.getHeadIndex() == 15
    assert chart.now.dt == datetime(2023, 8, 1, 7, 14, tzinfo=UTC)

    chart.setHeadDatetime(datetime(2023, 8, 3, 10, 0, tzinfo=UTC))
    assert chart.now.dt == datetime(2023, 8, 3, 10, 0, tzinfo=UTC)
    assert chart.last.dt == datetime(2023, 8, 3, 9, 59, tzinfo=UTC)

    bars = chart.getTodayBars()
    assert bars[0].dt == datetime(2023, 8, 3, 6, 59, tzinfo=UTC)
    assert bars[-1].dt == datetime(2023, 8, 3, 9, 59, tzinfo=UTC)
    assert len(bars) == 181

    chart.nextHead()
    assert chart.now.dt == datetime(2023, 8, 3, 10, 1, tzinfo=UTC)
    assert chart.last.dt == datetime(2023, 8, 3, 10, 0, tzinfo=UTC)

    chart.resetHead()
    assert chart.first.dt == datetime(2023, 8, 1, 6, 59, tzinfo=UTC)
    assert chart.last.dt == datetime(2023, 8, 31, 20, 49, tzinfo=UTC)
    assert chart.now is None
    assert chart[0] is None
    assert chart[1].dt == datetime(2023, 8, 31, 20, 49, tzinfo=UTC)
    assert chart.getHeadIndex() == len(chart.getBars())

    # add new bars in chart
    bar = Bar(now(), 1, 1, 1, 1, 5000)
    chart.update([bar, bar])
    bars = chart.getBars()
    assert bars[-1] == bar
    assert bars[-2] == bar
    assert bars[-2].vol == 5000


# }}}
@pytest.mark.asyncio  # test_Asset  # {{{
async def test_Asset(event_loop):
    exchange = Exchange.MOEX
    asset_type = AssetType.SHARE
    ticker = "SBER"
    figi = "BBG004730N88"
    name = "Сбер Банк"
    ID = InstrumentId(asset_type, exchange, ticker, figi, name)

    asset = Asset.byId(ID)
    assert asset.exchange == exchange
    assert asset.type == asset_type
    assert asset.ticker == ticker
    assert asset.figi == figi
    assert asset.name == name

    asset = await Asset.byFigi(figi)
    assert asset.exchange == exchange
    assert asset.type == asset_type
    assert asset.ticker == ticker
    assert asset.figi == figi
    assert asset.name == name

    asset = await Asset.byTicker(asset_type, exchange, ticker)
    assert asset.exchange == exchange
    assert asset.type == asset_type
    assert asset.ticker == ticker
    assert asset.figi == figi
    assert asset.name == name

    assert asset.parent() is None


# }}}
@pytest.mark.asyncio  # test_Share  # {{{
async def test_Share(event_loop):
    exchange = Exchange.MOEX
    asset_type = AssetType.SHARE
    id_list = await Data.find(asset_type, exchange, "SBER")
    assert len(id_list) == 1
    sber = Share(id_list[0])

    assert sber.exchange == exchange
    assert sber.type == asset_type
    assert sber.ticker == "SBER"
    assert sber.name == "Сбер Банк"
    assert sber.figi == "BBG004730N88"

    # info
    # assert sber.info is None  # logger - error
    await sber.loadInfo()
    assert sber.info
    assert sber.uid == "e6123145-9665-43e0-8413-cd61b8aa9b13"
    assert sber.min_price_step == 0.01
    assert sber.lot == 10

    await sber.cacheChart("D")
    assert sber.chart("D").timeframe == TimeFrame("D")
    assert sber.chart("1H") is None

    await sber.cacheChart("1H")
    assert sber.chart("1H").timeframe == TimeFrame("1H")

    sber.clearCache()
    assert sber.chart("1H") is None
    assert sber.chart("D") is None

    chart = await sber.loadChart("1M")
    assert sber.chart("1M") is None  # loading not caching
    assert chart.timeframe == TimeFrame("1M")


# }}}
@pytest.mark.asyncio  # test_AssetList  # {{{
async def test_AssetList(event_loop):
    alist = AssetList(name="_unittest")
    assert alist.name == "_unittest"
    assert alist.assets == []
    assert alist.count == 0

    afks = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "AFKS")
    sber = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "SBER")

    # add
    alist.add(afks)
    assert alist.count == 1

    # no duplicating items
    alist.add(sber)
    # alist.add(sber)  # logger - warning
    # alist.add(sber)  # logger - warning
    assert alist.count == 2

    # getitem
    assert alist[0].ticker == "AFKS"
    assert alist[1].ticker == "SBER"

    # iter
    for i in alist:
        assert isinstance(i, Asset)

    # contain
    assert afks in alist
    assert sber in alist

    # remove
    alist.remove(sber)
    assert sber not in alist
    assert alist.count == 1

    # find by ID
    result = alist.find(afks.ID)
    assert result == afks
    result = alist.find(sber.ID)
    assert result is None

    # save
    await AssetList.save(alist)

    # load
    loaded = await AssetList.load("_unittest")
    assert alist.name == loaded.name
    assert alist.count == loaded.count
    assert alist[0].ticker == loaded[0].ticker

    # copy
    await AssetList.copy(alist, "_unittest_copy")
    alist_copy = await AssetList.load("_unittest_copy")
    assert alist_copy.name != alist.name
    assert alist_copy.name == "_unittest_copy"

    # rename runtime object
    alist_copy.name = "_unittest_copy_rename"  # rename just object, not in db
    assert alist_copy.name == "_unittest_copy_rename"
    loaded = await AssetList.load("_unittest_copy")
    assert loaded.name == "_unittest_copy"
    loaded = await AssetList.load("_unittest_copy_rename")  # this not in db
    assert loaded == []
    alist_copy.name = "_unittest_copy"  # revert rename object

    # rename runtime object and record in db
    await AssetList.rename(alist_copy, "_unittest_copy_rename_2")
    assert alist_copy.name == "_unittest_copy_rename_2"
    loaded = await AssetList.load("_unittest_copy_rename_2")
    assert loaded.name == alist_copy.name
    assert loaded.count == alist_copy.count

    # delete
    await AssetList.delete(alist)  # delete only from db, not current object
    await AssetList.delete(alist_copy)  # delete only from db...
    loaded = await AssetList.load("_unittest")
    assert loaded == []
    loaded = await AssetList.load("_unittest_copy")
    assert loaded == []
    loaded = await AssetList.load("_unittest_copy_rename_2")
    assert loaded == []

    # clear list
    alist.clear()
    assert alist.name == "_unittest"
    assert alist.assets == []
    assert alist.count == 0


# }}}
@pytest.mark.asyncio  # test_Order  # {{{
async def test_Order(event_loop):
    sber_id = await InstrumentId.byTicker(
        AssetType.SHARE, Exchange.MOEX, "SBER"
    )
    o = Order.Market(
        "_unittest", Order.Direction.SELL, sber_id, lots=15, quantity=150
    )
    assert o.account_name == "_unittest"
    assert o.direction == Order.Direction.SELL
    assert o.asset_id == sber_id
    assert o.lots == 15
    assert o.quantity == 150
    assert o.order_id is not None
    assert o.trade_id is None
    assert o.exec_lots == 0
    assert o.exec_quantity == 0
    assert o.status == Order.Status.NEW

    await Order.save(o)

    # setStatus change both: object & record in db
    await o.setStatus(Order.Status.POST)
    assert o.status == Order.Status.POST
    loaded = await Order.load(o.order_id)
    assert loaded.status == o.status

    # change exec_lots
    o.exec_lots = 5
    o.exec_quantity = 50

    # update db record
    await Order.update(o)
    loaded = await Order.load(o.order_id)
    assert loaded.exec_lots == o.exec_lots
    assert loaded.exec_quantity == o.exec_quantity

    # delete from db
    await Order.delete(o)

    # Limit order
    o_limit = Order.Limit(
        "_unittest",
        Order.Direction.BUY,
        sber_id,
        lots=15,
        quantity=150,
        price=300,
    )
    assert o_limit.account_name == "_unittest"
    assert o_limit.direction == Order.Direction.BUY
    assert o_limit.asset_id == sber_id
    assert o_limit.lots == 15
    assert o_limit.quantity == 150
    assert o_limit.price == 300
    assert o_limit.order_id is not None
    assert o_limit.trade_id is None
    assert o_limit.exec_lots == 0
    assert o_limit.exec_quantity == 0
    assert o_limit.status == Order.Status.NEW

    # Stop order
    o_stop = Order.Stop(
        "_unittest",
        Order.Direction.BUY,
        sber_id,
        lots=15,
        quantity=150,
        stop_price=301,
        exec_price=302,
    )
    assert o_stop.account_name == "_unittest"
    assert o_stop.direction == Order.Direction.BUY
    assert o_stop.asset_id == sber_id
    assert o_stop.lots == 15
    assert o_stop.quantity == 150
    assert o_stop.stop_price == 301
    assert o_stop.exec_price == 302
    assert o_stop.order_id is not None
    assert o_stop.trade_id is None
    assert o_stop.exec_lots == 0
    assert o_stop.exec_quantity == 0
    assert o_stop.status == Order.Status.NEW


# }}}
@pytest.mark.asyncio  # test_Operation  # {{{
async def test_Operation():
    ID = await InstrumentId.byTicker(AssetType.SHARE, Exchange.MOEX, "SBER")
    share = Share(ID)
    dt = datetime(2024, 8, 27, 15, 12, tzinfo=UTC)

    op = Operation(
        account_name="_unittest",
        dt=dt,
        direction=Operation.Direction.SELL,
        asset_id=share.ID,
        lots=1,
        quantity=50,
        price=100,
        amount=100 * 50,
        commission=10,
        trade_id=None,
        meta=None,
    )

    assert op.dt == dt
    assert op.direction == Operation.Direction.SELL
    assert op.asset_id == ID
    assert op.price == 100
    assert op.lots == 1
    assert op.quantity == 50
    assert op.amount == 5000
    assert op.commission == 10
    assert op.meta is None

    assert str(op) == "2024-08-27 18:12 SELL SBER 50 * 100 = 5000 + 10"


# }}}
@pytest.mark.asyncio  # test_Trade  # {{{
async def test_Trade():
    # create strategy and trade
    dt = datetime(2024, 8, 27, 16, 33, tzinfo=UTC)
    strategy = Strategy("_unittest", "v1")
    trade_type = Trade.Type.LONG
    asset = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "SBER")
    trade_id = 1111
    trade = Trade(
        dt=dt,
        strategy=strategy.name,
        version=strategy.version,
        trade_type=trade_type,
        asset_id=asset.ID,
        trade_id=trade_id,
    )
    assert trade.trade_id == trade_id
    assert trade.dt == dt
    assert trade.status == Trade.Status.INITIAL
    assert trade.strategy == strategy.name
    assert trade.version == strategy.version
    assert trade.type == trade_type
    assert trade.asset_id == asset.ID
    assert trade.orders == []
    assert trade.operations == []

    await Keeper.add(strategy)
    await Trade.save(trade)

    # create order
    order_id = 2222
    order = Order.Limit(
        account_name="_unittest",
        direction=Order.Direction.BUY,
        asset_id=asset.ID,
        lots=1,
        quantity=10,
        price=100,
        order_id=order_id,
    )
    await trade.addOrder(order)  # signals of order connect automaticaly
    assert order.trade_id == trade.trade_id  # and parent trade_id was seted

    await order.posted.async_emit(order)
    assert trade.status == Trade.Status.POSTED  # side effect - status changed

    # create operation
    operation_id = 3333
    operation = Operation(
        account_name="_unittest",
        dt=dt,
        direction=Operation.Direction.BUY,
        asset_id=asset.ID,
        price=100,
        lots=1,
        quantity=10,
        amount=100 * 10,
        commission=5,
        operation_id=operation_id,
        order_id=order_id,
        meta=None,
    )

    await order.fulfilled.async_emit(
        order,
        [
            operation,
        ],
    )
    assert trade.status == Trade.Status.OPEN  # side effect - status changed

    # other property availible for opened trade
    assert trade.isLong()
    assert not trade.isShort()
    assert trade.lots() == 1
    assert trade.quantity() == 10
    assert trade.buyQuantity() == 10
    assert trade.sellQuantity() == 0
    assert trade.amount() == 1000
    assert trade.buyAmount() == 1000
    assert trade.sellAmount() == 0
    assert trade.commission() == 5
    assert trade.buyCommission() == 5
    assert trade.sellCommission() == 0
    assert trade.average() == 100
    assert trade.buyAverage() == 100
    assert trade.sellAverage() == 0
    assert trade.openPrice() == 100
    assert trade.openDatetime() == dt

    # Add second order and operation
    dt2 = dt + ONE_DAY
    order_id_2 = 2223
    order_2 = Order.Limit(
        account_name="_unittest",
        direction=Order.Direction.SELL,
        asset_id=asset.ID,
        lots=1,
        quantity=10,
        price=110,
        order_id=order_id_2,
    )
    operation_2 = Operation(
        account_name="_unittest",
        dt=dt2,
        direction=Operation.Direction.SELL,
        asset_id=asset.ID,
        price=110,
        lots=1,
        quantity=10,
        amount=110 * 10,
        commission=5,
        order_id=order_id_2,
        meta=None,
    )
    await trade.addOrder(order_2)  # signals of order connect automaticaly
    await order_2.posted.async_emit(order_2)
    await order_2.fulfilled.async_emit(
        order_2,
        [
            operation_2,
        ],
    )

    assert trade.status == Trade.Status.CLOSE
    assert trade.isLong()
    assert not trade.isShort()
    assert trade.lots() == 0
    assert trade.quantity() == 0
    assert trade.buyQuantity() == 10
    assert trade.sellQuantity() == 10
    assert trade.amount() == 0
    assert trade.buyAmount() == 1000
    assert trade.sellAmount() == 1100
    assert trade.commission() == 10
    assert trade.buyCommission() == 5
    assert trade.sellCommission() == 5
    assert trade.average() == 0
    assert trade.buyAverage() == 100
    assert trade.sellAverage() == 110
    assert trade.openDatetime() == dt
    assert trade.openPrice() == 100
    assert trade.closeDatetime() == dt2
    assert trade.closePrice() == 110

    # members availible for closed trade
    assert trade.result() == 1100 - 1000 - 10  # sell - buy - commission
    assert trade.holdingDays() == 2
    assert trade.percent() == 9.0
    assert trade.percentPerDay() == 4.5

    # clear all
    await Keeper.delete(operation)
    await Keeper.delete(operation_2)
    await Keeper.delete(order)
    await Keeper.delete(order_2)
    await Keeper.delete(trade)
    await Keeper.delete(strategy)

    chart = await trade.chart(TimeFrame("D"))
    assert chart.last.dt.date() == dt.date()

    chart = await trade.chart(TimeFrame("1M"))
    assert chart.last.dt == dt - ONE_MINUTE


# }}}
@pytest.mark.asyncio  # test_TradeList  # {{{
async def test_TradeList():
    # create trade list
    tlist_name = "_name"
    tlist = TradeList(tlist_name)

    # create trades
    strategy = Strategy("_unittest", "v1")
    dt = datetime(2024, 8, 27, 16, 33, tzinfo=UTC)
    trade_type = Trade.Type.LONG
    asset = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "SBER")
    trade_id_1 = 1111
    trade_1 = Trade(
        dt=dt,
        strategy=strategy.name,
        version=strategy.version,
        trade_type=trade_type,
        asset_id=asset.ID,
        trade_id=trade_id_1,
    )
    trade_id_2 = 1112
    trade_2 = Trade(
        dt=dt,
        strategy=strategy.name,
        version=strategy.version,
        trade_type=trade_type,
        asset_id=asset.ID,
        trade_id=trade_id_2,
    )
    tlist.add(trade_1)
    tlist.add(trade_2)

    assert tlist.name == "_name"
    assert tlist.count == 2

    # save
    await TradeList.save(tlist)

    # load
    loaded = await TradeList.load(tlist_name)
    assert loaded.name == tlist.name
    assert loaded.count == tlist.count

    # clear
    tlist.clear()

    # update
    await TradeList.update(tlist)
    loaded = await TradeList.load(tlist_name)
    assert loaded.count == 0

    # delete
    await TradeList.delete(tlist)


# }}}


# def test_Position():  # {{{
# TODO:
# позиция это чисто позиция в портфолио, как от брокера приходит
#     ID = Data.find(Exchange.MOEX, AssetType.SHARE, "SBER")
#     share = Share(ID)
#     dt = now()
#     op = Operation(
#         dt=dt,
#         direction=Operation.Direction.BUY,
#         asset=share,
#         price=100,
#         lots=1,
#         quantity=50,
#         amount=100 * 50,
#         commission=10,
#         meta=None,
#     )
#
#     pos = Position(operations=[op], meta=None)
#     assert pos.status == Position.Status.OPEN
#     assert pos.operations[0] == op
#     assert pos.openPrice() == 100
#     assert pos.lots() == 1
#     assert pos.openDatetime() == dt
#     assert pos.quantity() == 50
#     assert pos.buyQuantity() == 50
#     assert pos.sellQuantity() == 0
#     assert pos.amount() == 5000
#     assert pos.buyAmount() == 5000
#     assert pos.sellAmount() == 0
#     assert pos.commission() == 10
#     assert pos.buyCommission() == 10
#     assert pos.sellCommission() == 0
#     assert pos.average() == 100
#     assert pos.averageBuy() == 100
#     assert pos.averageSell() == 0


# }}}
# def test_Cash():  # {{{
#     rub = Cash(Cash.Type.RUB, 1_000_000)
#     assert rub.type == Cash.Type.RUB
#     assert rub.value == 1_000_000
#
#
# # }}}
# def test_Portfolio():  # {{{
#     portfolio = Portfolio()
#
#     # input cash
#     rub = Cash(Cash.Type.RUB, 1_000_000)
#     portfolio.inputCash(rub)
#     cash_in_p = portfolio.cash(Cash.Type.RUB)
#     assert cash_in_p.value == rub.value
#     assert cash_in_p.type == rub.type
#
#     # output cash
#     rub = Cash(Cash.Type.RUB, 100_000)
#     portfolio.outputCash(rub)
#     cash_in_p = portfolio.cash(Cash.Type.RUB)
#     assert cash_in_p.value == 900_000
#
#     # add/get position
#     ID = Data.find(Exchange.MOEX, AssetType.SHARE, "SBER")
#     share = Share(ID)
#     dt = now()
#     op = Operation(
#         account_name="_unittest",
#         dt=dt,
#         direction=Operation.Direction.BUY,
#         asset=share,
#         price=100,
#         lots=1,
#         quantity=50,
#         amount=100 * 50,
#         commission=10,
#         meta=None,
#     )
#     pos = Position(operations=[op], meta=None)
#
#     portfolio = Portfolio(
#         [
#             rub,
#         ],
#         [
#             pos,
#         ],
#     )
#     shares_pos = portfolio.get(AssetType.SHARE)
#     assert shares_pos[0] == pos
#
#     # TODO: после рефакторинга сигнала это проедалать
#     # remove position (availible only if position closed)
#     # op = Operation(
#     #     dt=         dt,
#     #     direction=  Operation.Direction.SELL,
#     #     asset=      share,
#     #     price=      100,
#     #     lots=       1,
#     #     quantity=   50,
#     #     amount=     100*50,
#     #     commission= 10,
#     #     meta=       None
#     #     )
#     # pos.add(op)
#     # assert pos.status == Position.Status.CLOSE
#     # portfolio.remove(pos)
#     # shares_pos = portfolio.get(AssetType.SHARE)
#     # assert len(shares_pos) == 0
#     #
#
#
# # }}}
# def test_Filter():  # {{{
#     code = """
# def condition(x):
#     return x * 5
#     """
#     f = Filter("example", code)
#     assert f.check(4) == 20
#     assert f.name == "example"
#     assert f.code == code
#     Filter.save(f)
#
#     loaded = Filter.load(f.path)
#     assert Cmd.isExist(loaded.path)
#     assert loaded.check(4) == 20
#     assert loaded.name == "example"
#
#     Filter.rename(loaded, "blablabla")
#     assert Cmd.isExist(loaded.path)
#     Filter.delete(loaded)
#
#
# # }}}
