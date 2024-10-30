#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum
from datetime import date

from avin.const import ONE_MINUTE
from avin.core import Report, StrategySet, TradeList
from avin.keeper import Keeper
from avin.utils import Signal, logger


class Test:
    class Status(enum.Enum):  # {{{
        UNDEFINE = 0
        NEW = 1
        EDITED = 2
        PROCESS = 3
        COMPLETE = 4

        @classmethod  # fromStr
        def fromStr(cls, string):
            statuses = {
                "NEW": Test.Status.NEW,
                "EDITED": Test.Status.EDITED,
                "PROCESS": Test.Status.PROCESS,
                "COMPLETE": Test.Status.COMPLETE,
            }
            return statuses[string]

    # }}}
    def __init__(self, name: str):  # {{{
        logger.debug(f"Test.__init__({name})")

        self.__name = name
        self.__status = Test.Status.NEW
        self.__trade_list = TradeList(f"{name}-tlist")
        self.__report = Report(test=self)
        self.__cfg = dict()

        # signals
        self.progress = Signal(int)

    # }}}
    def __str__(self):
        return f"Test='{self.name}'"

    @property  # name# {{{
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name) -> bool:
        self.__name = new_name

    # }}}
    @property  # status# {{{
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status) -> bool:
        self.__status = new_status

    # }}}
    @property  # trade_list# {{{
    def trade_list(self):
        return self.__trade_list

    # }}}
    @property  # report# {{{
    def report(self):
        return self.__report

    # }}}
    @property  # description# {{{
    def description(self):
        return self.__cfg["description"]

    @description.setter
    def description(self, description):
        self.__cfg["description"] = description

    # }}}
    @property  # strategy_set# {{{
    def strategy_set(self):
        return self.__cfg["strategy_set"]

    @strategy_set.setter
    def strategy_set(self, strategy_set: StrategySet):
        self.__cfg["strategy_set"] = strategy_set

    # }}}
    @property  # deposit# {{{
    def deposit(self):
        return self.__cfg["deposit"]

    @deposit.setter
    def deposit(self, deposit: float):
        self.__cfg["deposit"] = deposit

    # }}}
    @property  # commission# {{{
    def commission(self):
        return self.__cfg["commission"]

    @commission.setter
    def commission(self, commission):
        self.__cfg["commission"] = commission

    # }}}
    @property  # begin# {{{
    def begin(self) -> date:
        return self.__cfg["begin"]

    @begin.setter
    def begin(self, begin: date):
        assert isinstance(begin, date)
        self.__cfg["begin"] = begin

    # }}}
    @property  # end# {{{
    def end(self) -> date:
        return self.__cfg["end"]

    @end.setter
    def end(self, end: date):
        assert isinstance(end, date)
        self.__cfg["end"] = end

    # }}}
    @property  # account  # {{{
    def account(self):
        return "_backtest"

    # }}}
    @property  # time_step  # {{{
    def time_step(self):
        return ONE_MINUTE

    # }}}
    def updateReport(self):  # {{{
        logger.debug("Test.updateReport()")
        self.__report = Report(test=self)

    # }}}
    async def clear(self):  # {{{
        logger.debug("Test.clear()")

        self.__trade_list.clear()  # clear runtime
        await Keeper.delete(self.__trade_list, only_trades=True)  # in db

        self.__report.clear()
        self.__status = Test.Status.NEW

    # }}}
    @classmethod  # fromRecord# {{{
    async def fromRecord(cls, record: asyncpg.Record) -> Test:
        logger.debug(f"{cls.__name__}.fromRecord()")

        test = Test(record["name"])
        test.status = Test.Status.fromStr(record["status"])

        # request strategy set
        s_set = await Keeper.get(StrategySet, name=record["strategy_set"])
        test.strategy_set = s_set

        # request trade list
        tlist = await Keeper.get(TradeList, name=record["trade_list"])
        test.__trade_list = tlist

        test.description = record["description"]
        test.deposit = record["deposit"]
        test.commission = record["commission"]
        test.begin = record["begin_date"]
        test.end = record["end_date"]

        # create report
        test.__report = Report(test)

        return test

    # }}}
    @classmethod  # save# {{{
    async def save(cls, test: Test) -> None:
        logger.debug(f"{cls.__name__}.save()")

        # remove old if exist
        await Keeper.delete(test)

        # save StrategySet
        await StrategySet.save(test.strategy_set)

        # save TradeList
        await TradeList.save(test.trade_list)

        # TODO:
        # save Report????

        # save Test
        await Keeper.add(test)

    # }}}
    @classmethod  # load#{{{
    async def load(cls, name: str) -> Test | None:
        logger.debug(f"{cls.__name__}.load()")

        test = await Keeper.get(cls, name=name)
        return test

    # }}}
    @classmethod  # delete# {{{
    async def delete(cls, test) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        await Keeper.delete(test)
        await Keeper.delete(test.trade_list)
        await Keeper.delete(test.strategy_set)

    # }}}
    @classmethod  # rename# {{{
    async def rename(cls, test, new_name: str) -> None:
        logger.debug(f"{cls.__name__}.rename()")

        await Keeper.delete(test)
        test.name = new_name
        await Keeper.add(test)

    # }}}
    @classmethod  # copy# {{{
    async def copy(cls, test, new_name: str) -> None:
        logger.debug(f"{cls.__name__}.copy()")

        assert False

    # }}}
