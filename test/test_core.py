#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.const import *
from avin.core import *
from avin.data import *
from avin.utils import *


def test_Range():  # {{{
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
    assert bar.isBull()
    assert not bar.isBear()
    assert 11.9 in bar.upper
    assert 10.9 not in bar.upper
    line = Bar.toCSV(bar)
    fields = line.split(";")
    decode_bar = Bar.fromCSV(fields, chart=None)
    assert bar == decode_bar

    # }}}


def test_TimeFrame():  # {{{
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


def test_Chart():  # {{{
    afks_id = Data.find(Exchange.MOEX, AssetType.SHARE, "AFKS")
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
    bar = Bar(1, 1, 5000, 1, 1, now())
    chart.update([bar, bar])
    bars = chart.getBars()
    assert bars[-1] == bar
    assert bars[-2] == bar
    # chart._setHeadIndex(15)
    # assert chart.now.dt == datetime(2023, 8, 1, 7, 14, tzinfo=UTC)
    # chart._setHeadDatetime(datetime(2023, 8, 3, 10, 0, tzinfo=UTC))
    # assert chart.now.dt == datetime(2023, 8, 3, 10, 0, tzinfo=UTC)
    # assert chart.last.dt == datetime(2023, 8, 3, 9, 59, tzinfo=UTC)
    # bars = chart.getTodayBars()
    # assert bars[0].dt == datetime(2023, 8, 3, 6, 59, tzinfo=UTC)
    # assert bars[-1].dt == datetime(2023, 8, 3, 9, 59, tzinfo=UTC)
    # assert len(bars) == 181


# }}}
def test_Share():  # {{{
    exchange = Exchange.MOEX
    asset_type = AssetType.SHARE
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
    assert afks.dir_path == Cmd.path(Usr.DATA, exchange.name, asset_type.name, "AFKS")
    assert afks.analytic_dir == Cmd.path(
        Usr.DATA, exchange.name, asset_type.name, "AFKS", "analytic"
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
def test_AssetList():  # {{{
    tmp_file = Cmd.path(Usr.ASSET, "example.al")
    if Cmd.isExist(tmp_file):
        Cmd.delete(tmp_file)

    alist = AssetList(name="example")
    assert alist.name == "example"
    assert alist.assets == []
    assert alist.count == 0
    afks = Share(Data.find(Exchange.MOEX, AssetType.SHARE, "AFKS"))
    sber = Share(Data.find(Exchange.MOEX, AssetType.SHARE, "SBER"))
    alist.add(afks)
    assert alist.count == 1
    alist.add(afks)
    alist.add(afks)
    assert alist.count == 1
    alist.add(sber)
    assert alist.count == 2
    assert alist[1].ticker == "SBER"
    alist.remove(sber)
    assert alist.count == 1
    assert not Cmd.isExist(alist.path)
    AssetList.save(alist)
    assert Cmd.isExist(alist.path)
    loaded = AssetList.load(alist.path)
    assert alist.count == 1
    assert alist[0].ticker == "AFKS"
    AssetList.delete(alist)
    assert not Cmd.isExist(alist.path)
    alist.clear()
    assert alist.name == "example"
    assert alist.assets == []
    assert alist.count == 0


# }}}
def test_Order():  # {{{
    ID = Data.find(Exchange.MOEX, AssetType.SHARE, "SBER")
    share = Share(ID)
    o = Order.Market(Order.Direction.SELL, share, lots=15, quantity=150)
    assert o.direction == Order.Direction.SELL
    assert o.asset == share
    assert o.lots == 15
    assert o.quantity == 150
    assert o.ID is not None
    assert o.trade_ID == None
    assert o.status == Order.Status.NEW
    assert o.account_name is None  # задается при размещении ордера


# }}}
def test_Operation():  # {{{
    ID = Data.find(Exchange.MOEX, AssetType.SHARE, "SBER")
    share = Share(ID)
    dt = now()
    op = Operation(
        account_name="_unittest",
        dt=dt,
        direction=Operation.Direction.SELL,
        asset=share,
        lots=1,
        quantity=50,
        price=100,
        amount=100 * 50,
        commission=10,
        trade_ID=None,
        meta=None,
    )

    assert op.dt == dt
    assert op.direction == Operation.Direction.SELL
    assert op.asset == share
    assert op.price == 100
    assert op.lots == 1
    assert op.quantity == 50
    assert op.amount == 5000
    assert op.commission == 10
    assert op.meta == None

    obj = Operation.toJson(op)
    assert isinstance(obj, dict)
    fromjson_op = Operation.fromJson(obj)
    assert str(op) == str(fromjson_op)

    assert op.dt == fromjson_op.dt
    assert op.direction == fromjson_op.direction
    assert op.asset == fromjson_op.asset
    assert op.price == fromjson_op.price
    assert op.lots == fromjson_op.lots
    assert op.quantity == fromjson_op.quantity
    assert op.amount == fromjson_op.amount
    assert op.commission == fromjson_op.commission
    assert op.meta == fromjson_op.meta


# }}}
# def test_Position():  # {{{
# TODO
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
def test_Cash():  # {{{
    rub = Cash(Cash.Type.RUB, 1_000_000)
    assert rub.type == Cash.Type.RUB
    assert rub.value == 1_000_000


# }}}
def test_Portfolio():  # {{{
    portfolio = Portfolio()

    # input cash
    rub = Cash(Cash.Type.RUB, 1_000_000)
    portfolio.inputCash(rub)
    cash_in_p = portfolio.cash(Cash.Type.RUB)
    assert cash_in_p.value == rub.value
    assert cash_in_p.type == rub.type

    # output cash
    rub = Cash(Cash.Type.RUB, 100_000)
    portfolio.outputCash(rub)
    cash_in_p = portfolio.cash(Cash.Type.RUB)
    assert cash_in_p.value == 900_000

    # add/get position
    ID = Data.find(Exchange.MOEX, AssetType.SHARE, "SBER")
    share = Share(ID)
    dt = now()
    op = Operation(
        account_name="_unittest",
        dt=dt,
        direction=Operation.Direction.BUY,
        asset=share,
        price=100,
        lots=1,
        quantity=50,
        amount=100 * 50,
        commission=10,
        meta=None,
    )
    pos = Position(operations=[op], meta=None)

    portfolio = Portfolio(
        [
            rub,
        ],
        [
            pos,
        ],
    )
    shares_pos = portfolio.get(AssetType.SHARE)
    assert shares_pos[0] == pos

    # TODO: после рефакторинга сигнала это проедалать
    # remove position (availible only if position closed)
    # op = Operation(
    #     dt=         dt,
    #     direction=  Operation.Direction.SELL,
    #     asset=      share,
    #     price=      100,
    #     lots=       1,
    #     quantity=   50,
    #     amount=     100*50,
    #     commission= 10,
    #     meta=       None
    #     )
    # pos.add(op)
    # assert pos.status == Position.Status.CLOSE
    # portfolio.remove(pos)
    # shares_pos = portfolio.get(AssetType.SHARE)
    # assert len(shares_pos) == 0
    #


# }}}
def test_Filter():  # {{{
    code = """
def condition(x):
    return x * 5
    """
    f = Filter("example", code)
    assert f.check(4) == 20
    assert f.name == "example"
    assert f.code == code
    Filter.save(f)

    loaded = Filter.load(f.path)
    assert Cmd.isExist(loaded.path)
    assert loaded.check(4) == 20
    assert loaded.name == "example"

    Filter.rename(loaded, "blablabla")
    assert Cmd.isExist(loaded.path)
    Filter.delete(loaded)


# }}}
def test_Trade():  # {{{
    dt = now()
    strategy = Strategy("Foobar", "v1")
    trade_type = Trade.Type.LONG
    asset = Asset.byTicker(Exchange.MOEX, AssetType.SHARE, "SBER")
    trade = Trade(dt, strategy, trade_type, asset)
    assert trade.status == Trade.Status.INITIAL

    order = Order.Limit(Order.Direction.BUY, asset, lots=1, quantity=10, price=100)
    trade.addOrder(order)  # signals of order connect automaticaly

    op = Operation(
        account_name="_unittest",
        dt=dt,
        direction=Operation.Direction.BUY,
        asset=asset,
        price=100,
        lots=1,
        quantity=10,
        amount=100 * 10,
        commission=5,
        meta=None,
    )

    order.posted.emit(order)
    assert trade.status == Trade.Status.NEW

    order.fulfilled.emit(
        order,
        [
            op,
        ],
    )
    assert trade.status == Trade.Status.OPEN
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

    dt2 = dt + ONE_DAY
    op2 = Operation(
        account_name="_unittest",
        dt=dt2,
        direction=Operation.Direction.BUY,
        asset=asset,
        price=100,
        lots=1,
        quantity=10,
        amount=100 * 10,
        commission=5,
        meta=None,
    )
    trade.addOperation(op2)
    assert trade.status == Trade.Status.OPEN
    assert trade.isLong()
    assert not trade.isShort()
    assert trade.lots() == 2
    assert trade.quantity() == 20
    assert trade.buyQuantity() == 20
    assert trade.sellQuantity() == 0
    assert trade.amount() == 2000
    assert trade.buyAmount() == 2000
    assert trade.sellAmount() == 0
    assert trade.commission() == 10
    assert trade.buyCommission() == 10
    assert trade.sellCommission() == 0
    assert trade.average() == 100
    assert trade.buyAverage() == 100
    assert trade.sellAverage() == 0
    assert trade.openPrice() == 100
    assert trade.openDatetime() == dt

    dt3 = dt2 + ONE_DAY
    op3 = Operation(
        account_name="_unittest",
        dt=dt3,
        direction=Operation.Direction.SELL,
        asset=asset,
        price=110,
        lots=2,
        quantity=20,
        amount=110 * 20,
        commission=10,
        meta=None,
    )
    trade.addOperation(op3)
    assert trade.status == Trade.Status.CLOSE
    assert trade.isLong()
    assert not trade.isShort()
    assert trade.lots() == 0
    assert trade.quantity() == 0
    assert trade.buyQuantity() == 20
    assert trade.sellQuantity() == 20
    assert trade.amount() == 0
    assert trade.buyAmount() == 2000
    assert trade.sellAmount() == 2200
    assert trade.commission() == 20
    assert trade.buyCommission() == 10
    assert trade.sellCommission() == 10
    assert trade.average() == 0
    assert trade.buyAverage() == 100
    assert trade.sellAverage() == 110
    assert trade.openDatetime() == dt
    assert trade.openPrice() == 100
    assert trade.closeDatetime() == dt3
    assert trade.closePrice() == 110

    # members availible for closed trade
    assert trade.result() == 200 - 20  # sell - commission
    assert trade.holdingDays() == 3
    assert trade.percent() == 9.0
    assert trade.percentPerDay() == 3.0


# }}}
