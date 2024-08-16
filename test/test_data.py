#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from datetime import datetime, timedelta

import pytest

from avin.const import *
from avin.data import *
from avin.utils import Cmd


def test_Source():  # {{{
    src = Source.TINKOFF
    assert src.name == "TINKOFF"

    file_path = Cmd.path(Dir.TMP, "source")
    Source.save(src, file_path)
    assert Cmd.isExist(file_path)

    loaded_src = Source.load(file_path)
    assert loaded_src == src
    assert loaded_src.name == "TINKOFF"

    Cmd.delete(file_path)


# }}}
def test_DataType():  # {{{
    data_type = DataType.BAR_D
    assert data_type.value == "D"
    assert data_type.toTimedelta() == timedelta(days=1)

    file_path = Cmd.path(Dir.TMP, "data_type")
    DataType.save(data_type, file_path)
    assert Cmd.isExist(file_path)

    loaded_data_type = DataType.load(file_path)
    assert loaded_data_type == data_type
    assert loaded_data_type.value == "D"

    from_str_data_type = DataType.fromStr("1M")
    assert from_str_data_type.name == "BAR_1M"
    assert from_str_data_type.value == "1M"

    Cmd.delete(file_path)


# }}}
def test_Exchange():  # {{{
    moex = Exchange.MOEX
    spb = Exchange.SPB
    assert moex.name == "MOEX"
    assert spb.name == "SPB"
    assert moex != spb


# }}}
def test_AssetType():  # {{{
    share = AssetType.SHARE
    index = AssetType.INDEX
    assert share.name == "SHARE"
    assert index.name == "INDEX"
    assert share != index
    assert share == share


# }}}
def test_InstrumentId():  # {{{
    sber = InstrumentId(
        asset_type=AssetType.SHARE,
        exchange=Exchange.MOEX,
        ticker="SBER",
        figi="BBG004730N88",
        name="Сбер Банк",
    )

    file_path = Cmd.path(Dir.TMP, "id")
    InstrumentId.save(sber, file_path)
    assert Cmd.isExist(file_path)

    loaded_id = InstrumentId.load(file_path)
    assert sber == loaded_id
    Cmd.delete(file_path)


# }}}


@pytest.mark.asyncio  # test_Data_cache  # {{{
async def test_Data_cache(event_loop):
    await Data.cache()


# }}}
@pytest.mark.asyncio  # test_Data_find  # {{{
async def test_Data_find(event_loop):
    id_list = await Data.find(AssetType.SHARE, Exchange.MOEX, "SBER")
    assert len(id_list) == 1
    sber = id_list[0]
    assert sber.name == "Сбер Банк"
    assert sber.figi == "BBG004730N88"

    id_list = await Data.find(AssetType.INDEX, Exchange.MOEX, "IMOEX")
    assert len(id_list) == 1
    imoex = id_list[0]
    assert imoex.name == "Индекс МосБиржи"
    assert imoex.figi == "_MOEX_IMOEX"  # my fake 'figi'


# }}}
@pytest.mark.asyncio  # test_Data_info  # {{{
async def test_Data_info(event_loop):
    id_list = await Data.find(AssetType.SHARE, Exchange.MOEX, "GAZP")
    assert len(id_list) == 1
    gazp_id = id_list[0]

    full_info = await Data.info(gazp_id)
    assert full_info["uid"] == "962e2a95-02a9-4171-abd7-aa198dbe643a"
    assert full_info["short_enabled_flag"] == True
    assert full_info["lot"] == 10
    # and more other keys...

    id_list = await Data.find(AssetType.INDEX, Exchange.MOEX, "IMOEX")
    assert len(id_list) == 1
    imoex = id_list[0]

    full_info = await Data.info(imoex)
    assert full_info["CURRENCYID"] == "RUB"
    assert full_info["BOARDID"] == "SNDX"
    # and more other keys...


# }}}
@pytest.mark.asyncio  # test_Data_firstDateTime  # {{{
async def test_Data_firstDateTime(event_loop):
    id_list = await Data.find(AssetType.SHARE, Exchange.MOEX, "SBER")
    assert len(id_list) == 1
    sber = id_list[0]

    dt_d_moex = await Data.firstDateTime(Source.MOEX, DataType.BAR_D, sber)
    dt_1m_moex = await Data.firstDateTime(Source.MOEX, DataType.BAR_1M, sber)
    assert dt_1m_moex > dt_d_moex

    dt_d_tinkoff = await Data.firstDateTime(
        Source.TINKOFF, DataType.BAR_D, sber
    )
    dt_1m_tinkoff = await Data.firstDateTime(
        Source.TINKOFF, DataType.BAR_1M, sber
    )
    assert dt_1m_tinkoff > dt_d_tinkoff


# }}}
@pytest.mark.asyncio  # test_Data_download  # {{{
async def test_Data_download():
    id_list = await Data.find(AssetType.SHARE, Exchange.MOEX, "ABRD")
    abrd = id_list[0]

    # Download one asset, one year, timeframe D, from MOEX
    await Data.download(Source.MOEX, DataType.BAR_D, abrd, 2023)


# }}}
@pytest.mark.asyncio  # test_Data_convert  # {{{
async def test_Data_convert():
    id_list = await Data.find(AssetType.SHARE, Exchange.MOEX, "ABRD")
    abrd = id_list[0]

    # convert ABRD D -> M
    await Data.convert(abrd, DataType.BAR_D, DataType.BAR_M)


# }}}
@pytest.mark.asyncio  # test_Data_request  # {{{
async def test_Data_request():
    id_list = await Data.find(AssetType.SHARE, Exchange.MOEX, "ABRD")
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
    assert len(records) == 12


# }}}
