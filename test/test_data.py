#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from datetime import datetime, timedelta
from avin.const import *
from avin.data import *
from avin.utils import Cmd

def test_Source():# {{{
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
def test_DataType():# {{{
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
def test_Exchange():# {{{
    moex = Exchange.MOEX
    spb = Exchange.SPB
    assert moex.name == "MOEX"
    assert spb.name == "SPB"
    assert moex != spb
# }}}
def test_AssetType():# {{{
    share = AssetType.SHARE
    index = AssetType.INDEX
    assert share.name == "SHARE"
    assert index.name == "INDEX"
    assert share != index
    assert share == share
# }}}
def test_Id():# {{{
    sber = Data.find(Exchange.MOEX, AssetType.SHARE, "SBER")
    assert sber.exchange == Exchange.MOEX
    assert sber.type == AssetType.SHARE
    assert sber.name == "Сбер Банк"
    assert sber.ticker == "SBER"
    assert sber.figi == "BBG004730N88"
    assert str(sber) == "MOEX-SHARE-SBER"

    file_path = Cmd.path(Dir.TMP, "id")
    Id.save(sber, file_path)
    assert Cmd.isExist(file_path)

    loaded_id = Id.load(file_path)
    assert sber == loaded_id
    Cmd.delete(file_path)
# }}}
def test_Data_assets():# {{{
    source = Source.MOEX
    asset_type = AssetType.INDEX
    assets = Data.assets(source, asset_type)
    assert len(assets) > 0
    assert isinstance(assets[0], Id)

    source = Source.TINKOFF
    asset_type = AssetType.SHARE
    assets = Data.assets(source, asset_type)
    assert len(assets) > 0
    assert isinstance(assets[0], Id)
# }}}
def test_Data_find():# {{{
    sber = Data.find(Exchange.MOEX, AssetType.SHARE, "SBER")
    assert sber.name == "Сбер Банк"
    assert sber.figi == "BBG004730N88"

    imoex = Data.find(Exchange.MOEX, AssetType.INDEX, "IMOEX")
    assert imoex.name == "Индекс МосБиржи"
    assert imoex.figi == None
# }}}
def test_Data_info():# {{{
    gazp_id = Data.find(Exchange.MOEX, AssetType.SHARE, "GAZP")
    full_info = Data.info(gazp_id)
    assert full_info["uid"] == "962e2a95-02a9-4171-abd7-aa198dbe643a"
    assert full_info["short_enabled_flag"] == True
    dt = datetime(2018, 3, 7, 18, 33, tzinfo=UTC)
    assert full_info["first_1min_candle_date"] == dt
    # and more other keys...

    imoex = Data.find(Exchange.MOEX, AssetType.INDEX, "IMOEX")
    full_info = Data.info(imoex)
    assert full_info["CURRENCYID"] == "RUB"
    assert full_info["BOARDID"] == "SNDX"
    # ...
# }}}
def test_Data_firstDateTime():# {{{
    sber = Data.find(Exchange.MOEX, AssetType.SHARE, "SBER")
    # dt_d_moex = Data.firstDateTime(Source.MOEX, DataType.BAR_D, sber)
    # dt_1m_moex = Data.firstDateTime(Source.MOEX, DataType.BAR_1M, sber)
    # assert dt_1m_moex > dt_d_moex

    # dt_d_tinkoff = Data.firstDateTime(Source.TINKOFF, DataType.BAR_D, sber)
    # dt_1m_tinkoff = Data.firstDateTime(Source.TINKOFF, DataType.BAR_1M, sber)
    # assert dt_1m_tinkoff > dt_d_tinkoff
# }}}
def test_Data_download_add_clear_convert_delete():# {{{
    # make backup user data abio
    backup_abio = False
    user_abio = Cmd.path(Usr.DATA, "MOEX", "SHARE", "ABIO")
    if Cmd.isExist(user_abio):
        backup_abio_path = Cmd.path(Dir.TMP, "ABIO")
        Cmd.copyDir(user_abio, backup_abio_path)
        Cmd.deleteDir(user_abio)
        backup_abio = True

    # make backup user data abrd
    backup_abrd = False
    user_abrd = Cmd.path(Usr.DATA, "MOEX", "SHARE", "ABRD")
    if Cmd.isExist(user_abrd):
        backup_abrd_path = Cmd.path(Dir.TMP, "ABRD")
        Cmd.copyDir(user_abrd, backup_abrd_path)
        Cmd.deleteDir(user_abrd)
        backup_abrd = True

    # Download one asset, one year, from MOEX
    source = Source.MOEX
    data_type = DataType.BAR_D
    abio_id = Data.find(Exchange.MOEX, AssetType.SHARE, "ABIO")
    Data.download(source, data_type, abio_id, 2024)
    path = Cmd.path(Usr.DOWNLOAD, "moex", "SHARE", "ABIO")
    assert Cmd.isExist(path)

    # Download one asset, one year, from Tinkoff
    source = Source.TINKOFF
    data_type = DataType.BAR_1M
    abrd_id = Data.find(Exchange.MOEX, AssetType.SHARE, "ABRD")
    Data.download(source, data_type, abrd_id, 2024)
    path = Cmd.path(Usr.DOWNLOAD, "tinkoff", "SHARE", "ABRD")
    assert Cmd.isExist(path)

    # test importing moex data, then clear
    Data.add(Source.MOEX)
    path = Cmd.path(Usr.DATA, "MOEX", "SHARE", "ABIO")
    assert Cmd.isExist(path)
    Data.clear(Source.MOEX)

    # test importing tinkoff data, then clear
    path = Cmd.path(Usr.DATA, "MOEX", "SHARE", "ABRD")
    Data.add(Source.TINKOFF)
    assert Cmd.isExist(path)
    Data.clear(Source.TINKOFF)

    # convert ABIO D -> M, then delete
    Data.convert(abio_id, DataType.BAR_D, DataType.BAR_M)
    path_M = Cmd.path(user_abio, "M")
    assert Cmd.isExist(path)
    Data.delete(abio_id, DataType.BAR_M)
    assert not Cmd.isExist(path_M)

    # convert abrd 1M -> D
    Data.convert(abrd_id, DataType.BAR_1M, DataType.BAR_D)
    path_D = Cmd.path(user_abrd, "D")
    assert Cmd.isExist(path)
    Data.delete(abrd_id, DataType.BAR_D)
    assert not Cmd.isExist(path_D)

    # delete all abio, abrd
    Cmd.deleteDir(user_abio)
    Cmd.deleteDir(user_abrd)

    # restore backup
    if backup_abio:
        Cmd.copyDir(backup_abio_path, user_abio)
        Cmd.deleteDir(backup_abio_path)
    if backup_abrd:
        Cmd.copyDir(backup_abrd_path, user_abrd)
        Cmd.deleteDir(backup_abrd_path)
# }}}



