#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


import pytest

from avin import *
from avin.data._data import _Bar, _BarsData
from avin.trader.account import Account


@pytest.mark.asyncio  # test_info  # {{{
async def test_info(event_loop):
    # receive info by exhange + asset_type + ticker
    info_list = await Keeper.info(
        DataSource.TINKOFF, AssetType.SHARE, ticker="SBER"
    )
    sber_info = info_list[0]
    assert sber_info["ticker"] == "SBER"
    assert sber_info["type"] == "SHARE"
    assert sber_info["name"] == "Сбер Банк"
    assert sber_info["sector"] == "financial"
    assert sber_info["figi"] == "BBG004730N88"
    assert sber_info["exchange"] == "MOEX"
    assert sber_info["lot"] == 10

    # receive info by figi, without specifi source and asset_type
    info_list = await Keeper.info(
        source=None, asset_type=None, figi="BBG004730N88"
    )
    sber_info = info_list[0]
    assert sber_info["ticker"] == "SBER"

    # receive all shares availible on Tinkoff broker
    info_list = await Keeper.info(DataSource.TINKOFF, AssetType.SHARE)
    assert sber_info in info_list
    assert len(info_list) > 100  # about 150 shares abailible now


# }}}
@pytest.mark.asyncio  # test_exchange  # {{{
async def test_exchange(event_loop):
    # Exchange._TEST_EXCHANGE with name '_TEST_EXCHANGE'
    # created special for pytest
    assert Exchange._TEST_EXCHANGE.name == "_TEST_EXCHANGE"

    # _TEST_EXCHANGE not in db
    request = """
        SELECT name FROM "Exchange"
        WHERE name = '_TEST_EXCHANGE'
        """
    records = await Keeper.transaction(request)
    # assert len(records) == 0

    # add _TEST_EXCHANGE in db
    await Keeper.add(Exchange._TEST_EXCHANGE)
    request = """
        SELECT name FROM "Exchange"
        WHERE name = '_TEST_EXCHANGE'
        """
    records = await Keeper.transaction(request)
    assert records[0]["name"] == "_TEST_EXCHANGE"

    # delete _TEST_EXCHANGE from db
    await Keeper.delete(Exchange._TEST_EXCHANGE)
    request = """
        SELECT name FROM "Exchange"
        WHERE name = '_TEST_EXCHANGE'
        """
    records = await Keeper.transaction(request)
    assert len(records) == 0


# }}}
@pytest.mark.asyncio  # test_instrument_id  # {{{
async def test_instrument_id(event_loop):
    # create fake share
    share_id = InstrumentId(
        AssetType.SHARE,
        Exchange._TEST_EXCHANGE,
        ticker="ORIK",
        figi="bbyby",
        name="ООО Рога и Копыта",
    )
    # add instrument id into db
    await Keeper.add(Exchange._TEST_EXCHANGE)
    await Keeper.add(share_id)

    # get instrument id
    ids = await Keeper.get(InstrumentId, figi="bbyby")
    assert len(ids) == 1
    assert share_id == ids[0]

    # clear all
    await Keeper.delete(share_id)
    await Keeper.delete(Exchange._TEST_EXCHANGE)


# }}}
@pytest.mark.asyncio  # test_bars_data  # {{{
async def test_bars_data(event_loop):
    # create fake share and bars data
    share_id = InstrumentId(
        AssetType.SHARE,
        Exchange._TEST_EXCHANGE,
        ticker="ORIK",
        figi="bbyby",
        name="ООО Рога и Копыта",
    )
    data_type = DataType.BAR_D
    b1 = _Bar(datetime(2024, 8, 15, 0, 0, tzinfo=UTC), 10, 12, 9, 11, 100)
    b2 = _Bar(datetime(2024, 8, 16, 0, 0, tzinfo=UTC), 11, 13, 10, 12, 200)
    b3 = _Bar(datetime(2024, 8, 17, 0, 0, tzinfo=UTC), 12, 14, 11, 13, 300)
    b4 = _Bar(datetime(2024, 8, 18, 0, 0, tzinfo=UTC), 13, 15, 12, 14, 400)
    b5 = _Bar(datetime(2024, 8, 19, 0, 0, tzinfo=UTC), 14, 16, 13, 15, 500)
    bars = [b1, b2, b3, b4, b5]
    source = DataSource.MOEX
    data = _BarsData(share_id, data_type, bars, source)

    # add data in db
    await Keeper.add(Exchange._TEST_EXCHANGE)
    await Keeper.add(data)

    # side effect - added Instrument
    ids = await Keeper.get(InstrumentId, figi="bbyby")
    assert len(ids) == 1
    assert share_id == ids[0]

    # side effect - added Asset
    asset = await Keeper.get(Asset, figi="bbyby")
    assert asset.name == share_id.name
    assert asset.figi == share_id.figi

    # side effect - added information about availible data types
    received_data_type_list = await Keeper.get(DataType, ID=share_id)
    assert len(received_data_type_list) == 1
    assert received_data_type_list[0] == data_type

    # side effect - added information about availible data
    # table with figi, data_type, source, first_dt, last_dt
    data_info_list = await Keeper.get(Data, ID=share_id)
    assert len(data_info_list) == 1
    data_info = data_info_list[0]
    assert data_info["figi"] == share_id.figi
    assert data_info["type"] == "BAR_D"
    assert data_info["source"] == "MOEX"
    assert data_info["first_dt"] == datetime(2024, 8, 15, 0, 0, tzinfo=UTC)
    assert data_info["last_dt"] == datetime(2024, 8, 19, 0, 0, tzinfo=UTC)

    # get bars data from db
    received_bars = await Keeper.get(_Bar, ID=share_id, data_type=data_type)

    # Compare the data
    assert received_bars[0]["volume"] == 100
    assert received_bars[1]["volume"] == 200
    assert received_bars[4]["volume"] == 500

    # get bars data from period  [begin, end)
    begin = datetime(2024, 8, 16)
    end = datetime(2024, 8, 18)
    received_bars = await Keeper.get(
        _Bar, ID=share_id, data_type=data_type, begin=begin, end=end
    )
    assert len(received_bars) == 2
    assert received_bars[0]["open"] == b2.open
    assert received_bars[1]["open"] == b3.open

    # get bars data from period where database not has bars
    begin = datetime(2024, 1, 1)
    end = datetime(2024, 2, 1)
    received_bars = await Keeper.get(
        _Bar, ID=share_id, data_type=data_type, begin=begin, end=end
    )
    assert len(received_bars) == 0

    # clear all
    await Keeper.delete(_Bar, ID=share_id, data_type=data_type)
    await Keeper.delete(share_id)
    await Keeper.delete(Exchange._TEST_EXCHANGE)


# }}}
@pytest.mark.asyncio  # test_asset  # {{{
async def test_asset(event_loop):
    # create fake share and exchange
    await Keeper.add(Exchange._TEST_EXCHANGE)
    share_id = InstrumentId(
        AssetType.SHARE,
        Exchange._TEST_EXCHANGE,
        ticker="ORIK",
        figi="bbyby",
        name="ООО Рога и Копыта",
    )
    share = Share(share_id)

    # share not in db
    request = """
        SELECT exchange, type, ticker, figi, name FROM "Asset"
        WHERE figi = 'bbyby'
        """
    records = await Keeper.transaction(request)
    assert len(records) == 0

    # Add share in db
    await Keeper.add(share)
    request = """
        SELECT exchange, type, ticker, figi, name FROM "Asset"
        WHERE figi = 'bbyby'
        """
    records = await Keeper.transaction(request)
    assert len(records) == 1

    # get share from db
    received_share = await Keeper.get(Asset, figi=share.figi)
    assert share.name == received_share.name
    assert share.figi == received_share.figi
    assert share.ticker == received_share.ticker
    assert share.type == received_share.type
    assert share.exchange == received_share.exchange

    # delete share from db
    await Keeper.delete(share)
    request = """
        SELECT exchange, type, ticker, figi, name FROM "Asset"
        WHERE figi = 'bbyby'
        """
    records = await Keeper.transaction(request)
    assert len(records) == 0

    await Keeper.delete(Exchange._TEST_EXCHANGE)


# }}}
@pytest.mark.asyncio  # test_account  # {{{
async def test_account(event_loop):
    acc = Account("_pytest", "Tinkoff", None)
    await Keeper.add(acc)

    received_acc = await Keeper.get(Account, name="_pytest")
    assert len(received_acc) == 1
    received_acc = received_acc[0]
    assert acc.name == received_acc.name
    assert acc.broker == received_acc.broker

    await Keeper.delete(acc)


# }}}
@pytest.mark.asyncio  # test_strategy  # {{{
async def test_strategy(event_loop):
    strategy = Strategy("pytest", "v0")
    await Keeper.add(strategy)
    await Keeper.delete(strategy)


# }}}
@pytest.mark.asyncio  # test_trade  # {{{
async def test_trade(event_loop):
    asset = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "ABIO")
    await Keeper.add(asset)
    strategy = Strategy("Example", "ver")
    await Keeper.add(strategy)

    dt = datetime(2024, 8, 15, 15, 37, tzinfo=UTC)
    trade_id = 111
    trade = Trade(
        dt=dt,
        strategy=strategy.name,
        version=strategy.version,
        trade_type=Trade.Type.LONG,
        figi=asset.figi,
        trade_id=trade_id,
    )
    await Keeper.add(trade)

    order_id = 222
    order = Order.Limit(
        direction=Order.Direction.BUY,
        figi=asset.figi,
        lots=1,
        quantity=10,
        price=303.33,
        account_name="_unittest",
        order_id=order_id,
        trade_id=trade_id,
    )
    await trade.addOrder(order)

    operation_id = 333
    operation = Operation(
        account_name="_unittest",
        dt=now(),
        direction=Operation.Direction.BUY,
        figi=asset.figi,
        lots=1,
        quantity=10,
        price=303.33,
        amount=10 * 303.33,
        commission=0.05,
        operation_id=operation_id,
        trade_id=trade_id,
        order_id=order_id,
    )
    await trade.addOperation(operation)

    trades = await Keeper.get(
        Trade,
        strategy=strategy,
        status=[
            Trade.Status.INITIAL,
            Trade.Status.NEW,
            Trade.Status.OPEN,
        ],
    )
    t = trades[0]
    assert str(t) == "=> Trade 2024-08-15 18:37 Example-ver TCS10A0JNAB6 long"
    assert t.orders[0].order_id == order_id
    assert t.operations[0].operation_id == operation_id

    # clear all
    await Keeper.delete(operation)
    await Keeper.delete(order)
    await Keeper.delete(trade)
    await Keeper.delete(asset)
    await Keeper.delete(strategy)


# }}}
