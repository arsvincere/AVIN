#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc
"""

from avin.const import *
from avin.data import *
from avin.core import *
from avin.utils import *

def test_Range():# {{{
    r = Range(5, 10)
    assert 6 in r
    assert 11 not in r
    assert 8 in r[50:100]
    assert r.min == 5
    assert r.max == 10
    assert r.type == Range.Type.UNDEFINE
    assert r.bar is None
    assert r.percent() == 50.0
    assert r.abs() == 5.0
    assert r.mid() == 7.5
    assert 6 in r.half(1)
    assert 6 in r.third(1)
    assert 6 in r.quarter(1)
    bar = Bar(now(), 10, 12, 9, 11, 1000)
    body = bar.body
    assert isinstance(body, Range)
    assert body.bar == bar
    assert body.type == Range.Type.BODY
    assert 11.0 in bar.body
    assert 11.1 not in bar.body
    # }}}
def test_Bar():# {{{
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
    assert bar.isBull()
    assert not bar.isBear()
    assert 11.9 in bar.upper
    assert 10.9 not in bar.upper
    line = Bar.toCSV(bar)
    fields = line.split(";")
    decode_bar = Bar.fromCSV(fields, chart=None)
    assert bar == decode_bar
    # }}}
def test_TimeFrame():# {{{
    D = TimeFrame("D")
    H = TimeFrame("1H")
    m5 = TimeFrame("5M")
    assert D > m5
    assert H == m5 * 12
    assert H < "D"
    assert m5 > "1M"
    assert H.minutes() == 60
    assert m5.minutes() == 5
    assert repr(H) == "TimeFrame('1H')"
    assert str(H) == "1H"
    # }}}
def test_Chart():# {{{
    afks_id = Data.find(Exchange.MOEX, AssetType.Share, "AFKS")
    share = Share(afks_id)
    tf = TimeFrame("1M")
    begin = datetime(2023, 8, 1, 0, 0, tzinfo=UTC)
    end = datetime(2023, 9, 1, 0, 0, tzinfo=UTC)
    chart = Chart(share, tf, begin, end)
    assert chart.asset.ticker == "AFKS"
    assert chart.timeframe == tf
    assert chart.first.dt == datetime(2023, 8, 1, 6, 59, tzinfo=UTC)
    assert chart.last.dt == datetime(2023, 8, 31, 20, 49, tzinfo=UTC)
    assert chart[1].dt == datetime(2023, 8, 31, 20, 49, tzinfo=UTC)
    assert chart.now is None
    assert chart[0] is None
    assert chart.asset == share
    bar = Bar(1,1,5000,1,1,now())
    chart.update([bar, bar])
    bars = chart.getBars()
    assert bars[-1] == bar
    assert bars[-2] == bar
    chart._setHeadIndex(15)
    assert chart.now.dt == datetime(2023, 8, 1, 7, 14, tzinfo=UTC)
    chart._setHeadDatetime(datetime(2023, 8, 3, 10, 0, tzinfo=UTC))
    assert chart.now.dt == datetime(2023, 8, 3, 10, 0, tzinfo=UTC)
    assert chart.last.dt == datetime(2023, 8, 3, 9, 59, tzinfo=UTC)
    bars = chart.getTodayBars()
    assert bars[0].dt == datetime(2023, 8, 3, 6, 59, tzinfo=UTC)
    assert bars[-1].dt == datetime(2023, 8, 3, 9, 59, tzinfo=UTC)
    assert len(bars) == 181
# }}}
def test_Share():# {{{
    exchange = Exchange.MOEX
    asset_type = AssetType.Share
    ID = Data.find(exchange, asset_type, "AFKS")
    afks = Share(ID)
    assert afks.exchange == exchange
    assert afks.type == asset_type
    assert afks.ticker == "AFKS"
    assert afks.name == "АФК Система"
    assert afks.figi == "BBG004S68614"
    assert afks.uid == "53b67587-96eb-4b41-8e0c-d2e3c0bdd234"
    assert afks.min_price_step == 0.001
    assert afks.lot == 100
    assert afks.dir_path == Cmd.path(
        Usr.DATA,
        exchange.name,
        asset_type.name,
        "AFKS"
        )
    assert afks.analytic_dir == Cmd.path(
        Usr.DATA,
        exchange.name,
        asset_type.name,
        "AFKS",
        "analytic"
        )

    afks.cacheChart("D")
    assert afks.chart("D").timeframe == TimeFrame("D")
    assert afks.chart("1H") is None
    afks.cacheChart("1H")
    assert afks.chart("1H").timeframe == TimeFrame("1H")
    afks.clearCache()
    assert afks.chart("1H") is None
    assert afks.chart("D") is None

    chart = afks.loadChart("1M")
    assert afks.chart("1M") is None  # loading not caching
    assert chart.timeframe == TimeFrame("1M")
# }}}

# def test_AssetList():
#     alist = AssetList(name="example")
#     assert alist.name == "example"
#     assert alist.assets == []
#     assert alist.count == 0
#     afks = Share("AFKS")
#     sber = Share("SBER")
#     alist.add(afks)
#     assert alist.count == 1
#     alist.add(afks)
#     alist.add(afks)
#     alist.add(sber)
#     alist.add(afks)
#     assert alist.count == 5
#     assert alist[3].ticker == "SBER"
#     alist.remove(sber)
#     assert alist.count == 4
#     assert not Cmd.isExist(alist.path)
#     AssetList.save(alist)
#     assert Cmd.isExist(alist.path)
#     loaded = AssetList.load(alist.path)
#     assert alist.count == 4
#     assert alist[0].ticker == "AFKS"
#     AssetList.delete(alist)
#     assert not Cmd.isExist(alist.path)
#     alist.clear()
#     assert alist.name == "example"
#     assert alist.assets == []
#     assert alist.count == 0
#
# def test_Signal():
#     s = Strategy.load("Every", "day")
#     afks = Share("AFKS")
#     sig = Signal(
#         dt=             now(),
#         strategy=       s,
#         signal_type=    Signal.Type.SHORT,
#         asset=          afks,
#         )
#     assert sig.strategy == s
#     assert sig.type == Signal.Type.SHORT
#     assert sig.type.name == "SHORT"
#     assert sig.asset == afks
#     assert sig.position is None
#     assert sig.isShort()
#     assert not sig.isLong()
#
# def test_Strategy():
#     s = Strategy.load("Every", "day")
#     assert s.name == "Every"
#     assert s.version == "day"
#     assert s.long_list[0].ticker == "AFKS"
#     assert s.short_list[0].ticker == "AFKS"
#     assert s.long_list.name == "long"
#     assert s.short_list.name == "short"
#
# def test_Order():
#     strategy = Strategy.load("Every", "day")
#     afks = Share("AFKS")
#     sig = Signal(
#         dt= now(),
#         strategy=strategy,
#         signal_type=Signal.Type.LONG,
#         asset= afks,
#         )
#     o = Order(
#         signal=sig,
#         type=Order.Type.LIMIT,
#         direction=Order.Direction.SELL,
#         asset=afks,
#         lots=10,
#         price=101.1,
#         )
#     assert o.signal == sig
#     assert o.type == Order.Type.LIMIT
#     assert o.direction == Order.Direction.SELL
#     assert o.asset == afks
#     assert o.lots == 10
#     assert o.price == 101.1
#
# def test_Operation():
#     strategy = Strategy.load("Every", "day")
#     afks = Share("AFKS")
#     sig = Signal(
#         dt= now(),
#         strategy=strategy,
#         signal_type=Signal.Type.LONG,
#         asset= afks,
#         )
#     o = Order(
#         signal=sig,
#         type=Order.Type.LIMIT,
#         direction=Order.Direction.SELL,
#         asset=afks,
#         lots=10,
#         price=101.1,
#         )
#     dt=now()
#     quantity = o.lots * o.asset.brockerInfo()["lot"]
#     amount = quantity * o.price
#     com = amount * 0.0005
#     op = Operation(
#         signal=o.signal,
#         dt=dt,
#         direction=Operation.Direction.SELL,
#         asset=o.asset,
#         lots=o.lots,
#         quantity=quantity,
#         price=o.price,
#         amount=amount,
#         commission=com,
#         )
#     assert op.signal == o.signal
#     assert op.dt == dt
#     assert op.direction == Operation.Direction.SELL
#     assert op.asset == afks
#     assert op.lots == o.lots
#     assert op.quantity == quantity
#     assert op.price == o.price
#     assert op.amount == amount
#     assert op.commission == com
#     obj = Operation.toJSON(op)
#     from_obj = Operation.fromJSON(obj)
#     assert op.dt == from_obj.dt
#     assert op.direction == from_obj.direction
#     assert op.asset.name == from_obj.asset.name
#     assert op.lots == from_obj.lots
#     assert op.quantity == from_obj.quantity
#     assert op.price == from_obj.price
#     assert op.amount == from_obj.amount
#     assert op.commission == from_obj.commission
#
# def test_Position():
#     strategy = Strategy.load("Every", "day")
#     afks = Share("AFKS")
#     sig = Signal(
#         dt= now(),
#         strategy=strategy,
#         signal_type=Signal.Type.LONG,
#         asset= afks,
#         )
#     op = Operation(
#         signal=     sig,
#         dt=         now(),
#         direction=  Operation.Direction.SELL,
#         asset=      afks,
#         lots=       100,
#         quantity=   100 * afks.lot,
#         price=      20,
#         amount=     20 * 100 * afks.lot,
#         commission= 20 * 100 * afks.lot * 0.0005,
#         )
#     pos = Position(sig, op)
#     assert pos.asset == sig.asset
#     assert pos.status == Position.Status.OPEN
#     assert len(pos.operations) == 1
#     assert pos.parent() == sig
#     assert pos.lots() == -op.lots
#     assert pos.openDatetime() == op.dt
#     assert pos.quantity() == -op.quantity
#     assert pos.buyQuantity() == 0
#     assert pos.sellQuantity() == op.quantity
#     assert pos.amount() == -op.amount
#     assert pos.buyAmount() == 0
#     assert pos.sellAmount() == op.amount
#     assert pos.buyCommission() == 0
#     assert pos.sellCommission() == op.commission
#     assert pos.average() == op.amount / op.quantity
#     assert pos.averageBuy() == 0
#     assert pos.averageSell() == op.amount / op.quantity
#     op2 = Operation(
#         signal=     sig,
#         dt=         now(),
#         direction=  Operation.Direction.BUY,
#         asset=      afks,
#         lots=       100,
#         quantity=   100 * afks.lot,
#         price=      19,
#         amount=     19 * 100 * afks.lot,
#         commission= 19 * 100 * afks.lot * 0.0005,
#         )
#     pos.add(op2)
#     assert pos.result() == 9805.0
#     assert pos.closeDatetime() == op2.dt
#     assert pos.holdingDays() == 1
#     assert pos.percent() == 5.16
#     assert pos.percentPerDay() == 5.16
#     assert pos.status == Position.Status.CLOSE
#     assert sig.info["position"]["result"] == pos.result()
#
# def test_Trade_TradeList_Test_Report():
#     ...
#
# def test_Filter():
#     code = '''
# def condition(x):
#     y = 1 + 1
#     return x * 5 + y
#     '''
#     f = Filter("example", code)
#     assert f.check(4) == 22
#     assert f.name == "example"
#     Filter.save(f)
#     loaded = Filter.load(f.path)
#     assert loaded.check(4) == 22
#     assert loaded.name == "example"
#     loaded.code = """
# def condition(x):
#     return x + 100
# """
#     assert loaded.check(1) == 101
#     assert loaded.name == "example"
#     assert Cmd.isExist(loaded.path)
#     Filter.delete(loaded)
#
#
#
#
#
