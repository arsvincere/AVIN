#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from datetime import date

import pytest

from avin import *
from avin.tester._stream import _BarStream


@pytest.mark.asyncio  # test_BarStream  # {{{
async def test_BarStream():
    stream = _BarStream()

    afks = await Asset.fromTicker(Exchange.MOEX, Asset.Type.SHARE, "AFKS")
    aflt = await Asset.fromTicker(Exchange.MOEX, Asset.Type.SHARE, "AFLT")
    alrs = await Asset.fromTicker(Exchange.MOEX, Asset.Type.SHARE, "ALRS")
    stream.subscribe(afks, TimeFrame("1M"))
    stream.subscribe(afks, TimeFrame("D"))
    stream.subscribe(afks, TimeFrame("5M"))

    begin = date(2023, 8, 1)
    end = date(2023, 8, 2)
    await stream.loadData(begin, end)

    for i in stream:
        isinstance(i, Event)


# }}}
@pytest.mark.asyncio  # test_Test  # {{{
async def test_Test():
    test_name = "_unittest_test"
    test = Test(f"{test_name}")
    assert test.name == f"{test_name}"
    assert test.status == Test.Status.NEW
    assert test.trade_list.name == f"{test_name}-tlist"
    assert test.report is not None
    assert test.account == "_backtest"

    # create strategy set
    item1 = StrategySetItem(
        "Every", "minute", "BBG004S68614", long=True, short=False
    )
    item2 = StrategySetItem(
        "Every", "minute", "BBG004S683W7", long=False, short=True
    )
    item3 = StrategySetItem(
        "Every", "five", "BBG004S68B31", long=True, short=True
    )
    item4 = StrategySetItem(
        "Every", "five", "BBG004730N88", long=True, short=True
    )
    s_set = StrategySet(
        name=f"{test_name}-set",
        items=[item1, item2, item3, item4],
    )
    assert s_set.name == f"{test_name}-set"
    assert len(s_set) == 4

    # configure test
    test.description = "unit test <class Test>"
    test.strategy_set = s_set
    test.deposit = 100_000.0
    test.commission = 0.0005
    test.begin = date(2023, 8, 1)
    test.end = date(2023, 9, 1)

    # save
    await Test.save(test)

    # load
    loaded = await Test.load(f"{test_name}")
    assert loaded.name == test.name
    assert loaded.trade_list.name == test.trade_list.name
    assert loaded.strategy_set.name == test.strategy_set.name
    assert loaded.account == test.account
    assert loaded.description == test.description

    assert loaded.deposit == test.deposit
    assert loaded.commission == test.commission
    assert loaded.begin == test.begin
    assert loaded.end == test.end

    # delete
    await Test.delete(test)


# }}}
@pytest.mark.asyncio  # test_Tester  # {{{
async def test_Tester():
    tester = Tester()

    test_name = "_unittest_test"
    test = Test(f"{test_name}")

    # create strategy set
    item1 = StrategySetItem(
        "Every", "day", "BBG004S68614", long=True, short=False
    )
    # item2 = StrategySetItem(
    #     "Every", "minute", "BBG004S683W7", long=True, short=True
    # )
    # item3 = StrategySetItem(
    #     "Every", "five", "BBG004S68B31", long=True, short=True
    # )
    s_set = StrategySet(
        name=f"{test_name}-set",
        # items=[item1, item2, item3],
        items=[item1],
    )

    # configure test
    test.description = "unit test <class Tester>"
    test.strategy_set = s_set
    test.deposit = 100_000.0
    test.commission = 0.0005
    test.begin = date(2023, 8, 1)
    test.end = date(2023, 8, 2)

    # save
    await Test.save(test)

    tester.setTest(test)
    await tester.runTest()


# }}}


# }}}
