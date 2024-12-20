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
from avin.tester.stream import BarStream


@pytest.mark.asyncio  # test_BarStream  # {{{
async def test_BarStream():
    stream = BarStream()

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
    test = Test("_unittest_test")
    assert test.name == "_unittest_test"
    asset = await Asset.fromStr("MOEX-SHARE-SBER")
    strategy = await Strategy.load("Every", "day")
    test.strategy = strategy
    test.asset = asset

    # default values
    assert test.enable_long
    assert test.enable_short
    assert test.trade_list.name == "Test=_unittest_test-trade_list"
    assert test.deposit == 100_000.0
    assert test.commission == 0.0005
    assert test.begin == date(2018, 1, 1)
    assert test.end == date(2023, 1, 1)
    assert test.description == ""
    assert test.account == "_backtest"
    assert test.time_step == ONE_MINUTE
    assert test.status == Test.Status.NEW

    # save
    await Test.save(test)

    # update
    test.status = Test.Status.EDITED
    await Test.update(test)

    # load
    loaded = await Test.load("_unittest_test")
    assert loaded.status == Test.Status.EDITED

    # delete
    await Test.delete(test)
    loaded = await Test.load("_unittest_test")
    assert loaded is None


# }}}
@pytest.mark.asyncio  # test_Tester  # {{{
async def test_Tester():
    asset = await Asset.fromStr("MOEX-SHARE-SBER")
    strategy = await Strategy.load("Every", "day")

    test = Test("_unittest_test")
    test.strategy = strategy
    test.asset = asset
    test.begin = date(2023, 8, 1)
    test.end = date(2023, 8, 2)
    test.description = "unit test <class Tester>"
    await Test.save(test)

    tester = Tester()
    await tester.run(test)

    await Test.delete(test)


# }}}


@pytest.mark.asyncio  # test_clear_all_test_vars  # {{{
async def test_clear_all_test_vars():
    test_name = "_unittest_test"
    test = await Test.load(test_name)
    if test is not None:
        await Test.delete(test)


# }}}


# NOTE: пусть код пока останется, по факту сейчас тест уже
# не использует StrategySet
# StrategySet будет использоваться Trader
# в его тесты этот код потом можно будет перенести
# @pytest.mark.asyncio  # test_Test_with_StrategySet  # {{{
# async def test_Test():
#     pass
#     return
#
#     test_name = "_unittest_test"
#     test = Test(f"{test_name}")
#     assert test.name == f"{test_name}"
#     assert test.status == Test.Status.NEW
#     assert test.trade_list.name == f"{test_name}-tlist"
#     assert test.report is not None
#     assert test.account == "_backtest"
#
#     # create strategy set
#     item1 = StrategySetNode(
#         "Every", "minute", "BBG004S68614", long=True, short=False
#     )
#     item2 = StrategySetNode(
#         "Every", "minute", "BBG004S683W7", long=False, short=True
#     )
#     item3 = StrategySetNode(
#         "Every", "five", "BBG004S68B31", long=True, short=True
#     )
#     item4 = StrategySetNode(
#         "Every", "five", "BBG004730N88", long=True, short=True
#     )
#     s_set = StrategySet(
#         name=f"{test_name}-set",
#         items=[item1, item2, item3, item4],
#     )
#     assert s_set.name == f"{test_name}-set"
#     assert len(s_set) == 4
#
#     # configure test
#     test.description = "unit test <class Test>"
#     test.strategy_set = s_set
#     test.deposit = 100_000.0
#     test.commission = 0.0005
#     test.begin = date(2023, 8, 1)
#     test.end = date(2023, 9, 1)
#
#     # save
#     await Test.save(test)
#
#     # load
#     loaded = await Test.load(f"{test_name}")
#     assert loaded.name == test.name
#     assert loaded.trade_list.name == test.trade_list.name
#     assert loaded.strategy_set.name == test.strategy_set.name
#     assert loaded.account == test.account
#     assert loaded.description == test.description
#
#     assert loaded.deposit == test.deposit
#     assert loaded.commission == test.commission
#     assert loaded.begin == test.begin
#     assert loaded.end == test.end
#
#     # delete
#     await Test.delete(test)
#
#
# # }}}
# @pytest.mark.asyncio  # test_Tester  # {{{
# async def test_Tester():
#     pass
#     return
#
#     tester = Tester()
#
#     test_name = "_unittest_test"
#     test = Test(f"{test_name}")
#
#     # create strategy set
#     item1 = StrategySetNode(
#         "Every", "day", "BBG004S68614", long=True, short=False
#     )
#     # item2 = StrategySetNode(
#     #     "Every", "minute", "BBG004S683W7", long=True, short=True
#     # )
#     # item3 = StrategySetNode(
#     #     "Every", "five", "BBG004S68B31", long=True, short=True
#     # )
#     s_set = StrategySet(
#         name=f"{test_name}-set",
#         # items=[item1, item2, item3],
#         items=[item1],
#     )
#
#     # configure test
#     test.description = "unit test <class Tester>"
#     test.strategy_set = s_set
#     test.deposit = 100_000.0
#     test.commission = 0.0005
#     test.begin = date(2023, 8, 1)
#     test.end = date(2023, 8, 2)
#
#     # save
#     await Test.save(test)
#
#     tester.setTest(test)
#     await tester.runTest()
#
#
# # }}}
