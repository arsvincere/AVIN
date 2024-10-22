#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum

from avin.core import Report, TradeList
from avin.keeper import Keeper
from avin.utils import logger


class Test:
    class Status(enum.Enum):  # {{{
        UNDEFINE = 0
        NEW = 1
        EDITED = 2
        ACTIVE = 3
        COMPLETE = 4

        @classmethod  # fromStr
        def fromStr(cls, string):
            statuses = {
                "NEW": Test.Status.NEW,
                "EDITED": Test.Status.EDITED,
                "ACTIVE": Test.Status.ACTIVE,
                "COMPLETE": Test.Status.COMPLETE,
            }
            return statuses[string]

    # }}}
    def __init__(self, name):  # {{{
        logger.debug(f"Test.__init__({name})")
        self.__status = Test.Status.NEW
        self.__name = name
        self.__cfg = dict()
        self.__tlist = TradeList(name="tlist")
        self.__report = Report(test=self)

    # }}}
    @property  # status# {{{
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status) -> bool:
        self.__status = new_status

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name) -> bool:
        self.__name = new_name

    # }}}
    @property  # description# {{{
    def description(self):
        return self.__cfg["description"]

    @description.setter
    def description(self, description):
        self.__cfg["description"] = description

    # }}}
    @property  # strategy# {{{
    def strategy(self):
        return self.__cfg["strategy"]

    @strategy.setter
    def strategy(self, strategy):
        self.__cfg["strategy"] = strategy

    # }}}
    @property  # version# {{{
    def version(self):
        # XXX: vestions list???
        # тогда можно будет внутри одного теста сравнивать разные версии
        # и прогонять тест сразу по всем версиям... это удобно будет вроде...
        # и как то сгруппированы они получаются.
        # test_smash_day
        #   - v1_tlist
        #       - short
        #       - long
        #       - 2018
        #       - 2019
        #   - v2_tlist
        #       - short
        #       - long
        #       - 2018
        #       - 2019
        return self.__cfg["version"]

    @version.setter
    def version(self, version):
        self.__cfg["version"] = version

    # }}}
    @property  # deposit# {{{
    def deposit(self):
        return self.__cfg["deposit"]

    @deposit.setter
    def deposit(self, deposit):
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
    def begin(self):
        dt = datetime.fromisoformat(self.__cfg["begin"])
        return dt.replace(tzinfo=UTC)

    @begin.setter
    def begin(self, begin):
        self.__cfg["begin"] = begin

    # }}}
    @property  # end# {{{
    def end(self):
        dt = datetime.fromisoformat(self.__cfg["end"])
        return dt.replace(tzinfo=UTC)

    @end.setter
    def end(self, end):
        self.__cfg["end"] = end

    # }}}
    @property  # tlist# {{{
    def tlist(self):
        return self.__tlist

    # }}}
    @property  # report# {{{
    def report(self):
        return self.__report

    # }}}
    def updateReport(self):  # {{{
        logger.debug("Test.updateReport()")
        self.__report = Report(test=self)

    # }}}
    def clear(self):  # {{{
        logger.debug("Test.clear()")
        self.__tlist.clear()
        self.__report.clear()
        self.__status = Test.Status.NEW

    # }}}
    @classmethod  # fromRecord# {{{
    async def record(cls, record) -> Test:
        test = Test(record["name"])
        test.status = Test.Status.fromStr(record["status"])
        test.description = record["description"]
        test.strategy = record["strategy"]
        test.version = record["version"]
        test.deposit = record["deposit"]
        test.commission = record["commission"]
        test.begin = record["begin_date"]
        test.end = record["end_date"]
        return test

    # }}}
    @classmethod  # save# {{{
    async def save(cls, test) -> None:
        await Keeper.add(self)

    # }}}
    @classmethod  # load#{{{
    async def load(cls, name: str) -> Test:
        test_list = await Keeper.get(cls, name=name)
        assert len(test_list) == 1
        return test_list[0]

    # }}}
    @classmethod  # delete# {{{
    async def delete(cls, test) -> None:
        await Keeper.delete(test)

    # }}}
    @classmethod  # rename# {{{
    async def rename(cls, test, new_name: str) -> None:
        await Keeper.delete(test)
        test.name = new_name
        await Keeper.add(test)

    # }}}
