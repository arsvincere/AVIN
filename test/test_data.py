#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from datetime import datetime, timedelta

import pytest

from avin import *


def test_DataSource():  # {{{
    src = DataSource.TINKOFF
    assert src.name == "TINKOFF"

    from_str = DataSource.fromStr("MOEX")
    assert from_str == DataSource.MOEX


# }}}
def test_DataType():  # {{{
    data_type = DataType.BAR_D
    assert data_type.name == "BAR_D"
    assert data_type.value == "D"
    assert str(data_type) == "D"

    assert data_type.toTimeDelta() == timedelta(days=1)

    from_str_data_type = DataType.fromStr("1M")
    assert from_str_data_type.name == "BAR_1M"
    assert from_str_data_type.value == "1M"


# }}}
def test_Exchange():  # {{{
    moex = Exchange.MOEX
    spb = Exchange.SPB
    assert moex.name == "MOEX"
    assert spb.name == "SPB"
    assert moex != spb

    from_str = Exchange.fromStr("MOEX")
    assert moex == from_str


# }}}
def test_InstrumentType():  # {{{
    share = Instrument.Type.SHARE
    index = Instrument.Type.INDEX
    assert share.name == "SHARE"
    assert index.name == "INDEX"
    assert share != index
    assert share == share

    bond = Instrument.Type.fromStr("BOND")
    assert bond.name == "BOND"


# }}}


@pytest.mark.asyncio  # test_Instrument  # {{{
async def test_Instrument():
    info = {
        "exchange": "MOEX",
        "type": "SHARE",
        "ticker": "SBER",
        "figi": "BBG004730N88",
        "name": "Сбер Банк",
        "lot": "10",
        "min_price_step": "0.01",
    }

    sber = Instrument(info)

    assert sber.exchange == Exchange.MOEX
    assert sber.type == Instrument.Type.SHARE
    assert sber.ticker == "SBER"
    assert sber.figi == "BBG004730N88"
    assert sber.name == "Сбер Банк"

    by_figi = await Instrument.fromFigi("BBG004730N88")
    assert by_figi.name == sber.name

    by_uid = await Instrument.fromUid("cf1c6158-a303-43ac-89eb-9b1db8f96043")
    assert by_uid.ticker == "MVID"

    by_ticker = await Instrument.fromTicker(
        Exchange.MOEX, Instrument.Type.SHARE, "AFKS"
    )
    assert by_ticker.ticker == "AFKS"

    # string
    assert str(sber) == "MOEX-SHARE-SBER"

    # operator ==
    assert by_figi == sber
    assert by_figi != by_uid


# }}}
@pytest.mark.asyncio  # test_Data_cache  # {{{
async def test_Data_cache(event_loop):
    await Data.cache()


# }}}
@pytest.mark.asyncio  # test_Data_find  # {{{
async def test_Data_find(event_loop):
    id_list = await Data.find(Exchange.MOEX, Instrument.Type.SHARE, "SBER")
    assert len(id_list) == 1
    sber = id_list[0]
    assert sber.name == "Сбер Банк"
    assert sber.figi == "BBG004730N88"

    id_list = await Data.find(Exchange.MOEX, Instrument.Type.INDEX, "IMOEX")
    assert len(id_list) == 1
    imoex = id_list[0]
    assert imoex.name == "Индекс МосБиржи"
    assert imoex.figi == "_MOEX_IMOEX"  # my fake 'figi'


# }}}
@pytest.mark.asyncio  # test_Data_firstDateTime  # {{{
async def test_Data_firstDateTime(event_loop):
    id_list = await Data.find(Exchange.MOEX, Instrument.Type.SHARE, "SBER")
    assert len(id_list) == 1
    sber = id_list[0]

    dt_d_moex = await Data.firstDateTime(
        DataSource.MOEX, sber, DataType.BAR_D
    )
    dt_1m_moex = await Data.firstDateTime(
        DataSource.MOEX, sber, DataType.BAR_1M
    )
    assert dt_1m_moex > dt_d_moex

    dt_d_tinkoff = await Data.firstDateTime(
        DataSource.TINKOFF, sber, DataType.BAR_D
    )
    dt_1m_tinkoff = await Data.firstDateTime(
        DataSource.TINKOFF, sber, DataType.BAR_1M
    )
    assert dt_1m_tinkoff > dt_d_tinkoff


# }}}
@pytest.mark.asyncio  # test_Data_download  # {{{
async def test_Data_download():
    id_list = await Data.find(Exchange.MOEX, Instrument.Type.SHARE, "ABRD")
    abrd = id_list[0]

    # Download one asset, one year, timeframe D, from MOEX
    await Data.download(DataSource.MOEX, abrd, DataType.BAR_D, 2023)


# }}}
@pytest.mark.asyncio  # test_Data_convert  # {{{
async def test_Data_convert():
    id_list = await Data.find(Exchange.MOEX, Instrument.Type.SHARE, "ABRD")
    abrd = id_list[0]

    # convert ABRD D -> M
    await Data.convert(abrd, DataType.BAR_D, DataType.BAR_M)


# }}}
@pytest.mark.asyncio  # test_Data_request  # {{{
async def test_Data_request():
    id_list = await Data.find(Exchange.MOEX, Instrument.Type.SHARE, "ABRD")
    abrd = id_list[0]

    # request period is half open [begin, end)  (august 2023)
    begin = datetime(2023, 8, 1, tzinfo=UTC)
    end = datetime(2023, 9, 1, tzinfo=UTC)
    records = await Data.request(abrd, DataType.BAR_D, begin, end)
    assert records[0]["dt"] == begin
    assert records[-1]["dt"] == end - ONE_DAY

    # request timeframe M from all 2023 year
    begin = datetime(2023, 1, 1, tzinfo=UTC)
    end = datetime(2024, 1, 1, tzinfo=UTC)
    records = await Data.request(abrd, DataType.BAR_M, begin, end)
    assert len(records) == 12  # 12 mounth in year


# }}}
@pytest.mark.asyncio  # test_Data_delete  # {{{
async def test_Data_delete():
    id_list = await Data.find(Exchange.MOEX, Instrument.Type.SHARE, "ABRD")
    abrd = id_list[0]

    await Data.delete(abrd, DataType.BAR_D)
    await Data.delete(abrd, DataType.BAR_M)


# }}}
