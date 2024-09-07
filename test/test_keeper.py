#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from datetime import datetime

import pytest

from avin import *
from avin.data._bar import _Bar, _BarsData
from avin.data._manager import _Manager
from avin.trader.account import Account

# TEST VARS{{{

exchange = Exchange._TEST_EXCHANGE

asset_id = InstrumentId(
    AssetType.SHARE,
    exchange,
    ticker="ORIK",
    figi="bbyby",
    name="ООО Рога и Копыта",
)

data_type = DataType.BAR_D

share = Share(asset_id)

acc = Account("_pytest", "Tinkoff", None)

strategy = Strategy("pytest", "v0")

dt = datetime(2024, 8, 15, 15, 37, tzinfo=UTC)
trade_id = Id("111")
trade = Trade(
    dt=dt,
    strategy=strategy.name,
    version=strategy.version,
    trade_type=Trade.Type.LONG,
    asset_id=asset_id,
    trade_id=trade_id,
)

order_id = Id("222")
order = Order.Limit(
    account_name="_unittest",
    direction=Order.Direction.BUY,
    asset_id=asset_id,
    lots=1,
    quantity=10,
    price=303.33,
    order_id=order_id,
    trade_id=trade_id,
)

operation_id = Id("333")
operation = Operation(
    account_name="_unittest",
    dt=now(),
    direction=Operation.Direction.BUY,
    asset_id=asset_id,
    lots=1,
    quantity=10,
    price=303.33,
    amount=10 * 303.33,
    commission=0.05,
    operation_id=operation_id,
    trade_id=trade_id,
    order_id=order_id,
)
# }}}


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


# }}}
@pytest.mark.asyncio  # test_instrument_id  # {{{
async def test_instrument_id(event_loop):
    # add instrument id into db
    await Keeper.add(asset_id)

    # get instrument id
    ids = await Keeper.get(InstrumentId, figi="bbyby")
    assert len(ids) == 1
    assert asset_id == ids[0]


# }}}
@pytest.mark.asyncio  # test_bars_data  # {{{
async def test_bars_data(event_loop):
    # create bars data
    b1 = _Bar(datetime(2024, 8, 15, 0, 0, tzinfo=UTC), 10, 12, 9, 11, 100)
    b2 = _Bar(datetime(2024, 8, 16, 0, 0, tzinfo=UTC), 11, 13, 10, 12, 200)
    b3 = _Bar(datetime(2024, 8, 17, 0, 0, tzinfo=UTC), 12, 14, 11, 13, 300)
    b4 = _Bar(datetime(2024, 8, 18, 0, 0, tzinfo=UTC), 13, 15, 12, 14, 400)
    b5 = _Bar(datetime(2024, 8, 19, 0, 0, tzinfo=UTC), 14, 16, 13, 15, 500)
    bars = [b1, b2, b3, b4, b5]
    source = DataSource.MOEX
    data = _BarsData(asset_id, data_type, bars, source)

    # add data in db
    await Keeper.add(data)

    # side effect - added Instrument
    ids = await Keeper.get(InstrumentId, figi="bbyby")
    assert len(ids) == 1
    assert asset_id == ids[0]

    # side effect - added Asset
    asset = await Keeper.get(Asset, figi="bbyby")
    assert asset.name == asset_id.name
    assert asset.figi == asset_id.figi

    # side effect - added information about availible data types
    received_data_type_list = await Keeper.get(DataType, ID=asset_id)
    assert len(received_data_type_list) == 1
    assert received_data_type_list[0] == data_type

    # side effect - added information about availible data
    # table with figi, data_type, source, first_dt, last_dt
    data_info_list = await Keeper.get(_Manager, ID=asset_id)
    assert len(data_info_list) == 1
    data_info = data_info_list[0]
    assert data_info["figi"] == asset_id.figi
    assert data_info["type"] == "BAR_D"
    assert data_info["source"] == "MOEX"
    assert data_info["first_dt"] == datetime(2024, 8, 15, 0, 0, tzinfo=UTC)
    assert data_info["last_dt"] == datetime(2024, 8, 19, 0, 0, tzinfo=UTC)

    # get bars data from db
    bars_records = await Keeper.get(_Bar, ID=asset_id, data_type=data_type)

    # Compare the data
    assert bars_records[0]["volume"] == 100
    assert bars_records[1]["volume"] == 200
    assert bars_records[2]["volume"] == 300
    assert bars_records[3]["volume"] == 400
    assert bars_records[4]["volume"] == 500

    # get bars data from period  [begin, end)
    begin = datetime(2024, 8, 16)
    end = datetime(2024, 8, 18)
    bars_records = await Keeper.get(
        _Bar, ID=asset_id, data_type=data_type, begin=begin, end=end
    )
    assert len(bars_records) == 2
    assert bars_records[0]["open"] == b2.open
    assert bars_records[1]["open"] == b3.open

    # get bars data from period where database not has bars
    begin = datetime(2024, 1, 1)
    end = datetime(2024, 2, 1)
    bars_records = await Keeper.get(
        _Bar, ID=asset_id, data_type=data_type, begin=begin, end=end
    )
    assert len(bars_records) == 0


# }}}
@pytest.mark.asyncio  # test_asset  # {{{
async def test_asset(event_loop):
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


# }}}
@pytest.mark.asyncio  # test_strategy  # {{{
async def test_strategy(event_loop):
    strategy = Strategy("pytest", "v0")
    await Keeper.add(strategy)


# }}}
@pytest.mark.asyncio  # test_trade  # {{{
async def test_trade(event_loop):
    await Keeper.add(trade)
    await trade.attachOrder(order)
    await trade.attachOperation(operation)
    await Order.save(order)
    await Operation.save(operation)

    trades = await Keeper.get(
        Trade,
        strategy=strategy,
        status=[
            Trade.Status.INITIAL,
            Trade.Status.PENDING,
            Trade.Status.OPENED,
        ],
    )
    t = trades[0]

    assert str(t) == "2024-08-15 18:37 [INITIAL] pytest-v0 ORIK long"
    assert t.orders[0].order_id == order_id
    assert t.operations[0].operation_id == operation_id


# }}}
@pytest.mark.asyncio  # test_clear_all_test_records  # {{{
async def test_clear_all_test_records(event_loop):
    await Keeper.delete(operation)
    await Keeper.delete(order)
    await Keeper.delete(trade)

    # delete strategy
    await Keeper.delete(strategy)

    # delete account
    await Keeper.delete(acc)

    # delete bars data
    await Keeper.delete(_Bar, ID=asset_id, data_type=data_type)

    # delete share from db
    await Keeper.delete(share)
    request = """
        SELECT exchange, type, ticker, figi, name FROM "Asset"
        WHERE figi = 'bbyby'
        """
    records = await Keeper.transaction(request)
    assert len(records) == 0

    # delete _TEST_EXCHANGE
    await Keeper.delete(Exchange._TEST_EXCHANGE)
    request = """
        SELECT name FROM "Exchange"
        WHERE name = '_TEST_EXCHANGE'
        """
    records = await Keeper.transaction(request)
    assert len(records) == 0
