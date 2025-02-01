#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import pytest
from avin import *


def test_Id():  # {{{
    id_ = Id.newId()
    string = str(id_)

    from_str = Id.fromStr(string)
    assert id_ == from_str


# }}}
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
def test_Size():  # {{{
    b = Size.BIG
    n = Size.NORMAL
    s = Size.SMALL

    assert s < b
    assert n <= b
    assert b > s
    assert b >= n
    assert n == Size.NORMAL


# }}}
def test_Bar():  # {{{
    dt = DateTime.fromisoformat("2023-01-01")
    bar = Bar(dt, 10, 12, 9, 11, 1000, chart=None)
    assert bar.dt == dt
    assert bar.open == 10
    assert bar.high == 12
    assert bar.low == 9
    assert bar.close == 11
    assert bar.vol == 1000

    assert isinstance(bar.full, Range)
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

    bar.delFlag(Bar.Type.INSIDE)
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
def test_TimeFrameList():  # {{{
    tfl = TimeFrameList()
    assert str(tfl) == "[]"
    assert len(tfl) == 0
    assert TimeFrame("1M") not in tfl

    tfl.add(TimeFrame("1M"))
    assert str(tfl) == "[1M]"
    assert len(tfl) == 1
    assert TimeFrame("1M") in tfl

    tfl.add(TimeFrame("5M"))
    tfl.add(TimeFrame("1H"))
    assert str(tfl) == "[1M, 5M, 1H]"
    assert len(tfl) == 3
    assert TimeFrame("1M") in tfl
    assert TimeFrame("5M") in tfl
    assert TimeFrame("1H") in tfl
    assert TimeFrame("D") not in tfl

    # no duplicates
    tfl.add(TimeFrame("5M"))
    assert len(tfl) == 3

    # remove
    tfl.remove(TimeFrame("5M"))
    # tfl.remove(TimeFrame("5M"))  # logger warning
    assert str(tfl) == "[1M, 1H]"
    assert len(tfl) == 2

    # operator += to join without duplicates
    tfl2 = TimeFrameList(
        [
            TimeFrame("1M"),
            TimeFrame("D"),
            TimeFrame("W"),
        ]
    )
    tfl += tfl2
    assert len(tfl) == 4
    assert str(tfl) == "[1M, 1H, D, W]"

    # find
    finded = tfl.find("D")
    assert finded == TimeFrame("D")

    # clear
    tfl.clear()
    assert len(tfl) == 0
    assert str(tfl) == "[]"


# }}}
def test_BarChangedEvent():  # {{{
    figi = "BBG004730N88"
    timeframe = TimeFrame("1M")
    bar = Bar("2023-01-01", 10, 12, 9, 11, 1000, chart=None)

    event = BarChangedEvent(figi, timeframe, bar)
    assert event.figi == figi
    assert event.timeframe == timeframe
    assert event.bar == bar
    assert event.type == Event.Type.BAR_CHANGED


# }}}
def test_NewHistoricalBarEvent():  # {{{
    figi = "BBG004730N88"
    timeframe = TimeFrame("1M")
    bar = Bar("2023-01-01", 10, 12, 9, 11, 1000, chart=None)

    event = NewHistoricalBarEvent(figi, timeframe, bar)
    assert event.figi == figi
    assert event.timeframe == timeframe
    assert event.bar == bar
    assert event.type == Event.Type.NEW_HISTORICAL_BAR


# }}}
def test_Transaction():  # {{{
    t1 = Transaction(
        order_id="111",
        dt=DateTime(2023, 8, 1),
        quantity=5,
        price=10.0,
        broker_id="1111",
    )
    assert t1.order_id == "111"
    assert t1.dt == DateTime(2023, 8, 1)
    assert t1.quantity == 5
    assert t1.price == 10.0
    assert t1.broker_id == "1111"

    # TODO: save, load, delete from db


# }}}
def test_TransactionList():  # {{{
    t1 = Transaction(
        order_id="111",
        dt=now(),
        quantity=5,
        price=10.0,
        broker_id="1111",
    )
    t2 = Transaction(
        order_id="222",
        dt=now(),
        quantity=6,
        price=10.0,
        broker_id="2222",
    )

    transaction_list = TransactionList()
    assert len(transaction_list) == 0
    assert str(transaction_list) == "TransactionList=[]"
    assert t1 not in transaction_list
    assert t2 not in transaction_list

    transaction_list.add(t1)
    transaction_list.add(t2)
    assert len(transaction_list) == 2
    assert t1 in transaction_list
    assert t2 in transaction_list
    assert transaction_list.first == t1
    assert transaction_list.last == t2

    assert transaction_list.quantity() == 5 + 6
    assert transaction_list.amount() == 110.0
    assert transaction_list.average() == 10.0

    transaction_list.remove(t1)
    assert len(transaction_list) == 1
    assert t1 not in transaction_list
    assert t2 in transaction_list

    transaction_list.clear()
    assert len(transaction_list) == 0
    assert str(transaction_list) == "TransactionList=[]"
    assert t1 not in transaction_list
    assert t2 not in transaction_list


# }}}
def test_Risk():  # {{{
    deposit = 100_000
    r_trade = 1000
    open_price = 100
    stop_price = 90
    take_price = 150
    lotX = 10

    max_lots = Risk.maxLotsByRisk(r_trade, open_price, stop_price, lotX)
    assert max_lots == 10

    max_lots = Risk.maxLotsByDeposit(deposit, open_price, lotX)
    assert max_lots == 100

    pr = Risk.pr(open_price, stop_price, take_price)
    assert pr == 5.0


# }}}


@pytest.mark.asyncio  # test_Chart  # {{{
async def test_Chart(event_loop):
    sber = await Asset.fromTicker(
        Exchange.MOEX, Instrument.Type.SHARE, "SBER"
    )
    tf = TimeFrame("1M")
    begin = DateTime(2023, 8, 1, 0, 0, tzinfo=UTC)
    end = DateTime(2023, 9, 1, 0, 0, tzinfo=UTC)
    bars = await Keeper.get(
        Bar, instrument=sber, timeframe=tf, begin=begin, end=end
    )

    # create chart
    chart = Chart(sber, tf, bars)
    assert chart.instrument == sber
    assert chart.instrument.ticker == "SBER"
    assert chart.timeframe == tf

    assert chart.first.dt == DateTime(2023, 8, 1, 6, 59, tzinfo=UTC)
    assert chart.last.dt == DateTime(2023, 8, 31, 20, 49, tzinfo=UTC)

    assert chart[1].dt == DateTime(2023, 8, 31, 20, 49, tzinfo=UTC)
    assert chart.now is None
    assert chart[0] is None

    # manipulation with head
    chart.setHeadIndex(15)
    assert chart.getHeadIndex() == 15
    assert chart.now.dt == DateTime(2023, 8, 1, 7, 14, tzinfo=UTC)

    chart.setHeadDatetime(DateTime(2023, 8, 3, 10, 0, tzinfo=UTC))
    assert chart.now.dt == DateTime(2023, 8, 3, 10, 0, tzinfo=UTC)
    assert chart.last.dt == DateTime(2023, 8, 3, 9, 59, tzinfo=UTC)

    bars = chart.getTodayBars()
    assert bars[0].dt == DateTime(2023, 8, 3, 6, 59, tzinfo=UTC)
    assert bars[-1].dt == DateTime(2023, 8, 3, 9, 59, tzinfo=UTC)
    assert len(bars) == 181

    chart.nextHead()
    assert chart.now.dt == DateTime(2023, 8, 3, 10, 1, tzinfo=UTC)
    assert chart.last.dt == DateTime(2023, 8, 3, 10, 0, tzinfo=UTC)

    chart.prevHead()
    assert chart.now.dt == DateTime(2023, 8, 3, 10, 0, tzinfo=UTC)
    assert chart.last.dt == DateTime(2023, 8, 3, 9, 59, tzinfo=UTC)

    chart.resetHead()
    assert chart.first.dt == DateTime(2023, 8, 1, 6, 59, tzinfo=UTC)
    assert chart.last.dt == DateTime(2023, 8, 31, 20, 49, tzinfo=UTC)
    assert chart.now is None
    assert chart[0] is None
    assert chart[1].dt == DateTime(2023, 8, 31, 20, 49, tzinfo=UTC)
    assert chart.getHeadIndex() == len(chart.getBars())

    # add new bars in chart
    bar = Bar(now(), 1, 1, 1, 1, 5000)
    chart.addHistoricalBar(bar)
    bars = chart.getBars()
    assert bars[-1] == bar
    assert bars[-1].vol == 5000


# }}}
@pytest.mark.asyncio  # test_Asset  # {{{
async def test_Asset(event_loop):
    info = {
        "exchange": "MOEX",
        "type": "SHARE",
        "ticker": "SBER",
        "figi": "BBG004730N88",
        "name": "Сбер Банк",
        "lot": "10",
        "min_price_step": "0.01",
    }
    instrument = Instrument(info)

    asset = Asset.fromInstrument(instrument)
    assert asset.exchange == Exchange.MOEX
    assert asset.type == Asset.Type.SHARE
    assert asset.ticker == "SBER"
    assert asset.figi == "BBG004730N88"
    assert asset.name == "Сбер Банк"
    assert asset.lot == 10
    assert asset.min_price_step == 0.01
    assert isinstance(asset, Share)

    asset = await Asset.fromFigi("BBG004730N88")
    assert asset.exchange == Exchange.MOEX
    assert asset.type == Asset.Type.SHARE
    assert asset.ticker == "SBER"
    assert asset.figi == "BBG004730N88"
    assert asset.name == "Сбер Банк"
    assert asset.lot == 10
    assert asset.min_price_step == 0.01
    assert isinstance(asset, Share)

    asset = await Asset.fromTicker(Exchange.MOEX, Asset.Type.SHARE, "SBER")
    assert asset.exchange == Exchange.MOEX
    assert asset.type == Asset.Type.SHARE
    assert asset.ticker == "SBER"
    assert asset.figi == "BBG004730N88"
    assert asset.name == "Сбер Банк"
    assert asset.lot == 10
    assert asset.min_price_step == 0.01
    assert isinstance(asset, Share)

    # load bars data as DataFrame
    sber = await Asset.fromTicker(
        Exchange.MOEX, Instrument.Type.SHARE, "SBER"
    )
    begin = DateTime(2023, 1, 1, tzinfo=UTC)
    end = DateTime(2023, 2, 1, tzinfo=UTC)
    dataframe = await sber.loadData(TimeFrame("D"), begin, end)
    assert dataframe["volume"][0] == 21098550  # volume 2023-01-03 SBER


# }}}
@pytest.mark.asyncio  # test_Share  # {{{
async def test_Share(event_loop):
    exchange = Exchange.MOEX
    asset_type = Asset.Type.SHARE
    instr_list = await Data.find(exchange, asset_type, "SBER")
    assert len(instr_list) == 1
    instrument = instr_list[0]
    sber = Share(instrument.info)

    assert instrument == sber
    assert sber.info is not None
    assert sber.exchange == exchange
    assert sber.type == asset_type
    assert sber.ticker == "SBER"
    assert sber.name == "Сбер Банк"
    assert sber.figi == "BBG004730N88"
    assert sber.uid == "e6123145-9665-43e0-8413-cd61b8aa9b13"
    assert sber.min_price_step == 0.01
    assert sber.lot == 10

    await sber.cacheChart("D")
    assert sber.chart("D").timeframe == TimeFrame("D")

    await sber.cacheChart("1H")
    assert sber.chart("1H").timeframe == TimeFrame("1H")

    sber.clearCache()

    chart = await sber.loadChart("1M")
    assert chart.timeframe == TimeFrame("1M")


# }}}
@pytest.mark.asyncio  # test_AssetList  # {{{
async def test_AssetList(event_loop):
    alist = AssetList(name="_unittest")
    assert alist.name == "_unittest"
    assert alist.assets == []
    assert len(alist) == 0

    afks = await Asset.fromTicker(
        Exchange.MOEX, Instrument.Type.SHARE, "AFKS"
    )
    aflt = await Asset.fromTicker(
        Exchange.MOEX, Instrument.Type.SHARE, "AFLT"
    )
    sber = await Asset.fromTicker(
        Exchange.MOEX, Instrument.Type.SHARE, "SBER"
    )

    # add
    alist.add(afks)
    assert len(alist) == 1
    alist.add(aflt)
    assert len(alist) == 2

    # no duplicating items
    alist.add(sber)
    # alist.add(sber)  # logger - warning
    # alist.add(sber)  # logger - warning
    assert len(alist) == 3

    # getitem
    assert alist[0].ticker == "AFKS"
    assert alist[1].ticker == "AFLT"

    # iter
    for i in alist:
        assert isinstance(i, Asset)

    # contain
    assert afks in alist
    assert sber in alist

    # remove
    alist.remove(sber)
    assert sber not in alist
    assert len(alist) == 2

    # find by ID
    result = alist.find(afks)
    assert result == afks
    result = alist.find(sber)
    assert result is None

    # find by figi
    result = alist.find(figi=afks.figi)
    assert result == afks

    # save
    await AssetList.save(alist)

    # load
    loaded = await AssetList.load("_unittest")
    assert alist.name == loaded.name
    assert len(alist) == len(loaded)
    assert alist[0].ticker == loaded[0].ticker

    # copy
    await AssetList.copy(alist, "_unittest_copy")
    alist_copy = await AssetList.load("_unittest_copy")
    assert alist_copy.name != alist.name
    assert alist_copy.name == "_unittest_copy"
    loaded = await AssetList.load("_unittest_copy")
    assert loaded.name == "_unittest_copy"

    # rename runtime object
    alist_copy.name = "_unittest_copy_rename"  # rename just object, not in db
    assert alist_copy.name == "_unittest_copy_rename"
    loaded = await AssetList.load("_unittest_copy_rename")  # this not in db
    assert loaded is None
    alist_copy.name = "_unittest_copy"  # revert name

    # rename runtime object and record in db
    await AssetList.rename(alist_copy, "_unittest_copy_rename_2")
    assert alist_copy.name == "_unittest_copy_rename_2"
    loaded = await AssetList.load("_unittest_copy_rename_2")
    assert loaded.name == alist_copy.name
    assert len(loaded) == len(alist_copy)

    # delete
    await AssetList.delete(alist)  # delete only from db, not current object
    await AssetList.delete(alist_copy)  # delete only from db...
    loaded = await AssetList.load("_unittest")
    assert loaded is None
    loaded = await AssetList.load("_unittest_copy")
    assert loaded is None
    loaded = await AssetList.load("_unittest_copy_rename_2")
    assert loaded is None

    # clear list
    alist.clear()
    assert alist.name == "_unittest"
    assert alist.assets == []
    assert len(alist) == 0


# }}}
@pytest.mark.asyncio  # test_Trade  # {{{
async def test_Trade():
    # create TradeList in db
    tlist_name = "_unittest"
    tlist = TradeList(tlist_name)
    await TradeList.save(tlist)  # save only TradeList name in db

    # create strategy and trade
    dt = DateTime(2024, 8, 27, 16, 33, tzinfo=UTC)
    strategy = await Strategy.load("Every", "minute")
    trade_type = Trade.Type.LONG
    sber = await Asset.fromTicker(Exchange.MOEX, Asset.Type.SHARE, "SBER")
    trade_id = Id("1111")
    trade = Trade(
        dt=dt,
        strategy=strategy.name,
        version=strategy.version,
        trade_type=trade_type,
        instrument=sber,
        trade_id=trade_id,
        trade_list_name=tlist_name,
    )
    assert trade.trade_id == trade_id
    assert trade.dt == dt
    assert trade.status == Trade.Status.INITIAL
    assert trade.strategy == strategy.name
    assert trade.version == strategy.version
    assert trade.type == trade_type
    assert trade.instrument == sber
    assert trade.orders == []
    assert trade.operations == []

    await Trade.save(trade)

    # create order
    order_id = Id("2222")
    order = LimitOrder(
        account_name="_unittest",
        direction=Direction.BUY,
        instrument=sber,
        lots=1,
        quantity=10,
        price=100,
        order_id=order_id,
    )
    await trade.attachOrder(order)  # signals of order connect automaticaly
    assert order.trade_id == trade.trade_id  # and parent trade_id was seted

    await order.posted.aemit(order)
    assert (
        trade.status == Trade.Status.AWAIT_EXEC
    )  # side effect - status changed

    # create operation
    operation_id = Id("3333")
    operation = Operation(
        account_name="_unittest",
        dt=dt,
        direction=Direction.BUY,
        instrument=sber,
        price=100,
        lots=1,
        quantity=10,
        amount=100 * 10,
        commission=5,
        operation_id=operation_id,
        order_id=order_id,
        meta=None,
    )

    await order.executed.aemit(order, operation)
    assert trade.status == Trade.Status.OPENED  # side effect - status changed

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
    assert trade.openDateTime() == dt

    # Add second order and operation
    dt2 = dt + ONE_DAY
    order_id_2 = Id("2223")
    order_2 = LimitOrder(
        account_name="_unittest",
        direction=Direction.SELL,
        instrument=sber,
        lots=1,
        quantity=10,
        price=110,
        order_id=order_id_2,
    )
    operation_id_2 = Id("3334")
    operation_2 = Operation(
        account_name="_unittest",
        dt=dt2,
        direction=Direction.SELL,
        instrument=sber,
        price=110,
        lots=1,
        quantity=10,
        amount=110 * 10,
        commission=5,
        operation_id=operation_id_2,
        order_id=order_id_2,
        meta=None,
    )
    await trade.attachOrder(order_2)  # signals of order connect automaticaly
    await order_2.posted.aemit(order_2)
    await order_2.executed.aemit(order_2, operation_2)

    assert trade.status == Trade.Status.CLOSED
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
    assert trade.openDateTime() == dt
    assert trade.openPrice() == 100
    assert trade.closeDateTime() == dt2
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
    await TradeList.save(tlist)  # save only TradeList name in db

    chart = await trade.loadChart(TimeFrame("D"))
    assert chart.now.dt.date() == dt.date()

    chart = await trade.loadChart(TimeFrame("1M"))
    assert chart.now.dt == dt - ONE_MINUTE


# }}}
@pytest.mark.asyncio  # test_TradeList  # {{{
async def test_TradeList():
    # create trade list
    tlist_name = "_unittest"
    tlist = TradeList(tlist_name)
    assert tlist.name == tlist_name

    # create strategy
    strategy = await Strategy.load("Every", "minute")

    # create trades
    dt = DateTime(2024, 8, 27, 16, 33, tzinfo=UTC)
    trade_type = Trade.Type.LONG
    asset = await Asset.fromTicker(
        Exchange.MOEX, Instrument.Type.SHARE, "SBER"
    )
    trade_id_1 = Id(1111.0)
    trade_1 = Trade(
        dt=dt,
        strategy=strategy.name,
        version=strategy.version,
        trade_type=trade_type,
        instrument=asset,
        trade_id=trade_id_1,
        trade_list_name=tlist_name,
    )
    trade_id_2 = Id(1112.0)
    trade_2 = Trade(
        dt=dt,
        strategy=strategy.name,
        version=strategy.version,
        trade_type=trade_type,
        instrument=asset,
        trade_id=trade_id_2,
        trade_list_name=tlist_name,
    )
    tlist.add(trade_1)  # only add in TradeList, not in db
    tlist.add(trade_2)  # only add in TradeList, not in db
    assert len(tlist) == 2

    # create child - select trade status
    child1 = tlist.selectStatus(Trade.Status.INITIAL)
    assert child1.name == tlist.name
    assert child1.subname == "INITIAL"
    assert len(tlist.childs) == 1

    # create child - select strategy
    child2 = tlist.selectStrategy(strategy.name, strategy.version)
    assert len(child2) == 2
    assert len(tlist.childs) == 2

    # remove child
    tlist.removeChild(child1)
    assert len(tlist.childs) == 1

    # clear child
    tlist.clearChilds()
    assert len(tlist.childs) == 0

    # select filter list
    filter_list = FilterList.load("size")
    await tlist.selectFilterList(filter_list)

    # save
    await TradeList.save(tlist)  # save only TradeList name in db
    await Trade.save(trade_1)  # save trade in db
    await Trade.save(trade_2)  # save trade in db

    # load
    loaded = await TradeList.load(tlist_name)
    assert loaded.name == tlist.name
    assert len(loaded) == len(tlist)

    # clear
    tlist.clear()  # only in RAM, not in db

    # delete
    await TradeList.delete(tlist)  # del in db tlist & del trades too


# }}}
@pytest.mark.asyncio  # test_Order  # {{{
async def test_Order(event_loop):
    sber = await Instrument.fromTicker(
        Exchange.MOEX, Instrument.Type.SHARE, "SBER"
    )
    order_id = Id(100500)
    o = MarketOrder(
        "_unittest",
        Direction.SELL,
        sber,
        lots=15,
        quantity=150,
        order_id=order_id,
    )
    assert o.account_name == "_unittest"
    assert o.direction == Direction.SELL
    assert o.instrument == sber
    assert o.lots == 15
    assert o.quantity == 150
    assert o.order_id == order_id
    assert o.trade_id is None
    assert o.exec_lots == 0
    assert o.exec_quantity == 0
    assert o.status == Order.Status.NEW

    # Limit order
    o_limit = LimitOrder(
        "_unittest",
        Direction.BUY,
        sber,
        lots=15,
        quantity=150,
        price=300,
    )
    assert o_limit.account_name == "_unittest"
    assert o_limit.direction == Direction.BUY
    assert o_limit.instrument == sber
    assert o_limit.lots == 15
    assert o_limit.quantity == 150
    assert o_limit.price == 300
    assert o_limit.order_id is None
    assert o_limit.trade_id is None
    assert o_limit.exec_lots == 0
    assert o_limit.exec_quantity == 0
    assert o_limit.status == Order.Status.NEW

    # Stop order
    o_stop = StopOrder(
        "_unittest",
        Direction.BUY,
        sber,
        lots=15,
        quantity=150,
        stop_price=301,
        exec_price=302,
    )
    assert o_stop.account_name == "_unittest"
    assert o_stop.direction == Direction.BUY
    assert o_stop.instrument == sber
    assert o_stop.lots == 15
    assert o_stop.quantity == 150
    assert o_stop.stop_price == 301
    assert o_stop.exec_price == 302
    assert o_stop.order_id is None
    assert o_stop.trade_id is None
    assert o_stop.exec_lots == 0
    assert o_stop.exec_quantity == 0
    assert o_stop.status == Order.Status.NEW


# }}}
@pytest.mark.asyncio  # test_Operation  # {{{
async def test_Operation():
    sber = await Asset.fromTicker(Exchange.MOEX, Asset.Type.SHARE, "SBER")
    dt = DateTime(2024, 8, 27, 15, 12, tzinfo=UTC)

    op = Operation(
        account_name="_unittest",
        dt=dt,
        direction=Direction.SELL,
        instrument=sber,
        lots=1,
        quantity=50,
        price=100,
        amount=100 * 50,
        commission=10,
        trade_id=None,
        meta=None,
    )

    assert op.dt == dt
    assert op.direction == Direction.SELL
    assert op.instrument == sber
    assert op.price == 100
    assert op.lots == 1
    assert op.quantity == 50
    assert op.amount == 5000
    assert op.commission == 10
    assert op.meta is None
    assert str(op) == "2024-08-27 18:12 SELL SBER 50 * 100 = 5000 + 10"


# }}}
@pytest.mark.asyncio  # test_Filter  # {{{
async def test_Filter():
    code = """# {{{
from avin import *

async def conditionChart(chart: Chart) -> bool:
    if chart[3] is None:
        return False

    b3 = chart[3]
    b2 = chart[2]
    b1 = chart[1]

    if b3.isBull() and b2.isBull() and b1.isBull():
        return True

    return False

async def conditionAsset(asset: Asset) -> bool:
    assert False

async def conditionTrade(trade: Trade) -> bool:
    chart = await trade.loadChart("D")
    result = await conditionChart(chart)
    return result

"""  # }}}
    f = Filter("_bull_3", code)

    asset = await Asset.fromStr("MOEX-SHARE-AFKS")
    timeframe = TimeFrame("D")
    begin = DateTime(2023, 1, 1, tzinfo=UTC)
    end = DateTime(2024, 1, 1, tzinfo=UTC)
    await asset.cacheChart(timeframe, begin, end)

    chart = asset.chart("D")

    chart.setHeadIndex(0)
    while chart.nextHead():
        result = await f.acheck(chart)
        if result:
            assert chart[3].isBull()
            assert chart[2].isBull()
            assert chart[1].isBull()

    # Filter.save(f)
    # file_path = Cmd.path(Usr.FILTER, "_bull_3.py")
    # assert Cmd.isExist(file_path)
    #
    # f = Filter.rename(f, "_bbb")
    # file_path = Cmd.path(Usr.FILTER, "_bbb.py")
    # assert Cmd.isExist(file_path)
    #
    # loaded = Filter.load("_bbb")
    # assert loaded.name == f.name
    # assert loaded.code == f.code
    #
    # loaded = Filter.delete(loaded)
    # assert not Cmd.isExist(file_path)


# }}}
@pytest.mark.asyncio  # test_FilterList  # {{{
async def test_FilterList():
    filter_list = FilterList("_unittest")
    assert str(filter_list) == "FilterList=_unittest"
    assert len(filter_list) == 0
    assert filter_list.name == "_unittest"

    # load filters from files
    f1 = Filter.loadFromFile(
        "/home/alex/AVIN/usr/filter/size/b1/body/1_big.py"
    )
    f2 = Filter.loadFromFile(
        "/home/alex/AVIN/usr/filter/size/b1/body/2_bigger.py"
    )
    f3 = Filter.loadFromFile(
        "/home/alex/AVIN/usr/filter/size/b1/body/3_biggest.py"
    )

    # without filter list path = "Usr.FILTER/filter_name.py"
    assert f1.path == "/home/alex/AVIN/usr/filter/1_big.py"
    assert f2.path == "/home/alex/AVIN/usr/filter/2_bigger.py"
    assert f3.path == "/home/alex/AVIN/usr/filter/3_biggest.py"

    # add filter
    filter_list.add(f1)
    filter_list.add(f2)
    assert f1.path == "/home/alex/AVIN/usr/filter/_unittest/1_big.py"
    assert f2.path == "/home/alex/AVIN/usr/filter/_unittest/2_bigger.py"
    assert len(filter_list) == 2

    # create new filter list
    child_list = FilterList("child")
    assert f3.path == "/home/alex/AVIN/usr/filter/3_biggest.py"
    child_list.add(f3)
    assert f3.path == "/home/alex/AVIN/usr/filter/child/3_biggest.py"

    # add child filter list
    filter_list.addChild(child_list)
    filter_list.addChild(child_list)
    assert len(filter_list.childs) == 2
    assert child_list.parent_list == filter_list
    assert (
        f3.path == "/home/alex/AVIN/usr/filter/_unittest/child/3_biggest.py"
    )

    # iteration
    for child in filter_list.childs:
        assert isinstance(child, FilterList)
    for f in filter_list:
        assert isinstance(f, Filter)

    # remove filter
    filter_list.remove(f1)
    assert len(filter_list) == 1

    # clear filter
    filter_list.clear()
    assert len(filter_list) == 0

    # remove child filter lists
    filter_list.removeChild(child_list)
    assert len(filter_list.childs) == 1

    # clear child filter lists
    filter_list.clearChilds()
    assert len(filter_list.childs) == 0

    # request all filter list names
    names = FilterList.requestAll()
    for name in names:
        assert isinstance(name, str)


# }}}


@pytest.mark.asyncio  # test_clear_all_test_vars  # {{{
async def test_clear_all_test_vars():
    request = """
    DELETE FROM "AssetList"
    WHERE
        asset_list_name = '_unittest' OR
        asset_list_name = '_unittest_copy' OR
        asset_list_name = '_unittest_copy_rename' OR
        asset_list_name = '_unittest_copy_rename_2';
    """
    await Keeper.transaction(request)

    request = """
    DELETE FROM "Operation"
    WHERE
        operation_id = '3333' OR
        operation_id = '3333';
    """
    await Keeper.transaction(request)

    request = """
    DELETE FROM "Order"
    WHERE
        order_id = '100500' OR
        order_id = '2222' OR
        order_id = '2223';
    """
    await Keeper.transaction(request)

    request = """
    DELETE FROM "Trade"
    WHERE
        trade_id = '1111' OR
        trade_id = '1112';
    """
    await Keeper.transaction(request)

    request = """
    DELETE FROM "TradeList"
    WHERE
        trade_list_name = '_name' OR
        trade_list_name = '_unittest';
    """
    await Keeper.transaction(request)


# }}}
