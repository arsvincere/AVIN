#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys
from avin.utils import *
from avin.const import *
from avin.core import *
from avin.company import *
from avin.gui.asset import *

def test_IShare():
    afks = IShare("AFKS")
    assert afks.exchange == Exchange.MOEX
    assert afks.type == Type.SHARE
    assert afks.ticker == "AFKS"
    assert afks.figi == "BBG004S68614"
    assert afks.uid == "53b67587-96eb-4b41-8e0c-d2e3c0bdd234"
    assert afks.name == "АФК Система"
    assert afks.dir_path == Cmd.join(SHARES_DIR, "AFKS")
    assert afks.lot == 100
    assert afks.min_price_step == 0.001
    afks.loadChart("D")
    assert afks.chart("D").timeframe == TimeFrame("D")
    assert afks.chart("1H") is None
    afks.loadChart("1H")
    assert afks.chart("1H").timeframe == TimeFrame("1H")
    afks.loadAllChart()
    assert afks.chart("5M").timeframe == TimeFrame("5M")
    afks.closeAllChart()
    assert afks.chart("1M") is None
    assert afks.chart("5M") is None
    assert afks.chart("1H") is None
    assert afks.chart("D") is None

def test_IAssetList():
    ialist = IAssetList.load(name="XX5")
    ialist = AssetList(name="example")
    assert ialist.name == "example"
    assert ialist.assets == []
    assert ialist.count == 0
    afks = IShare("AFKS")
    sber = IShare("SBER")
    ialist.add(afks)
    assert ialist.count == 1
    ialist.add(afks)
    ialist.add(afks)
    ialist.add(sber)
    ialist.add(afks)
    assert ialist.count == 5
    assert ialist[3].ticker == "SBER"
    ialist.remove(sber)
    assert ialist.count == 4
    assert not Cmd.isExist(ialist.path)
    AssetList.save(ialist)
    assert Cmd.isExist(ialist.path)
    loaded = AssetList.load(ialist.path)
    assert ialist.count == 4
    assert ialist[0].ticker == "AFKS"
    AssetList.delete(ialist)
    assert not Cmd.isExist(ialist.path)
    ialist.clear()
    assert ialist.name == "example"
    assert ialist.assets == []
    assert ialist.count == 0











