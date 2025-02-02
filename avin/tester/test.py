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
from typing import Iterator, Optional

from avin.core import (
    Asset,
    Strategy,
    Summary,
    TimeFrame,
    TradeList,
)
from avin.keeper import Keeper
from avin.utils import Cmd, Signal, logger


class Test:  # {{{
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
        logger.debug(f"{self.__class__.__name__}.__init__()")

        # default values:
        self.__name = name
        self.__strategy: Optional[Strategy] = None
        self.__asset: Optional[Asset] = None
        self.__enable_long = True
        self.__enable_short = True
        self.__deposit = 100000.0
        self.__commission = 0.0005
        self.__begin = date(2018, 1, 1)
        self.__end = date(2023, 1, 1)
        self.__description = ""
        self.__account = "_backtest"
        self.__trade_list = TradeList(f"{self}-trade_list")
        self.__test_list = None
        self.__status = Test.Status.NEW
        self.__time_step = TimeFrame("1M")

        # set owner
        self.__trade_list.setOwner(self)

        # signals
        self.progress = Signal(int)

    # }}}
    def __str__(self):  # {{{
        return f"Test={self.__name}"

    # }}}

    @property  # name  # {{{
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name
        self.__trade_list.name = f"{self}-trade_list"

    # }}}
    @property  # strategy  # {{{
    def strategy(self):
        return self.__strategy

    @strategy.setter
    def strategy(self, strategy: Strategy):
        self.__strategy = strategy

    # }}}
    @property  # asset  # {{{
    def asset(self):
        return self.__asset

    @asset.setter
    def asset(self, asset: Asset):
        self.__asset = asset

    # }}}
    @property  # enable_long  # {{{
    def enable_long(self):
        return self.__enable_long

    @enable_long.setter
    def enable_long(self, value: bool):
        self.__enable_long = value

    # }}}
    @property  # enable_short  # {{{
    def enable_short(self):
        return self.__enable_short

    @enable_short.setter
    def enable_short(self, value: bool):
        self.__enable_short = value

    # }}}
    @property  # deposit  # {{{
    def deposit(self):
        return self.__deposit

    @deposit.setter
    def deposit(self, deposit: float):
        self.__deposit = deposit

    # }}}
    @property  # commission  # {{{
    def commission(self):
        return self.__commission

    @commission.setter
    def commission(self, commission):
        self.__commission = commission

    # }}}
    @property  # begin  # {{{
    def begin(self) -> date:
        return self.__begin

    @begin.setter
    def begin(self, begin: date):
        assert isinstance(begin, date)
        self.__begin = begin

    # }}}
    @property  # end  # {{{
    def end(self) -> date:
        return self.__end

    @end.setter
    def end(self, end: date):
        assert isinstance(end, date)
        self.__end = end

    # }}}
    @property  # description  # {{{
    def description(self):
        return self.__description

    @description.setter
    def description(self, description):
        self.__description = description

    # }}}
    @property  # account  # {{{
    def account(self):
        return self.__account

    @account.setter
    def account(self, account_name: str):
        self.__account = account_name

    # }}}
    @property  # trade_list  # {{{
    def trade_list(self):
        return self.__trade_list

    @trade_list.setter
    def trade_list(self, trade_list: TradeList):
        self.__trade_list = trade_list

        if trade_list is not None:
            trade_list.name = f"{self}-trade_list"
            trade_list.setOwner(self)

    # }}}
    @property  # test_list  # {{{
    def test_list(self):
        return self.__test_list

    @test_list.setter
    def test_list(self, test_list: TestList):
        self.__test_list = test_list

    # }}}
    @property  # status  # {{{
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status):
        self.__status = new_status

    # }}}
    @property  # time_step  # {{{
    def time_step(self):
        return self.__time_step

    @time_step.setter
    def time_step(self, time_step: TimeFrame):
        self.__time_step = time_step

    # }}}

    def summary(self) -> Summary:  # {{{
        logger.debug(f"{self.__class__.__name__}.summary()")

        summary = Summary(self.__trade_list)
        return summary

    # }}}

    @classmethod  # fromRecord  # {{{
    async def fromRecord(cls, record: asyncpg.Record) -> Test:
        logger.debug(f"{cls.__name__}.fromRecord()")

        test = await cls.fromJson(record["config"])
        return test

    # }}}
    @classmethod  # save  # {{{
    async def save(cls, test: Test) -> None:
        logger.debug(f"{cls.__name__}.save()")

        # remove old if exist
        await Keeper.delete(test)

        # save TradeList
        await TradeList.save(test.trade_list)

        # save Test
        await Keeper.add(test)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, name: str) -> Test | None:
        logger.debug(f"{cls.__name__}.load()")

        test = await Keeper.get(cls, name=name)
        return test

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, test) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        await Keeper.delete(test)
        await TradeList.delete(test.trade_list)

    # }}}
    @classmethod  # update  # {{{
    async def update(cls, test: Test) -> None:
        logger.debug(f"{cls.__name__}.update()")

        await Keeper.update(test)

    # }}}
    @classmethod  # rename  # {{{
    async def rename(cls, test: Test, new_name: str) -> Test | None:
        logger.debug(f"{cls.__name__}.rename()")

        existed_names = await Test.requestAll()
        if new_name in existed_names:
            logger.error(f"{new_name} already exist, cancel rename test")
            return None

        await Test.delete(test)  # XXX: иначе гемор с трейд листом...
        test.name = new_name
        await Test.save(test)

        # XXX: это хардкор конечно удалять тест ради переименования...
        # но иначе надо тогда делать и TradeList.rename
        # потом как нибудь.

        return test

    # }}}
    @classmethod  # copy  # {{{
    async def copy(cls, test: Test, new_name: str) -> Test | None:
        logger.debug(f"{cls.__name__}.copy()")

        existed_names = await Test.requestAll()
        if new_name in existed_names:
            logger.error(f"{new_name} already exist, cancel copy test")
            return None

        copy = Test(new_name)
        copy.strategy = test.strategy
        copy.asset = test.asset
        copy.enable_long = test.enable_long
        copy.enable_short = test.enable_short
        copy.deposit = test.deposit
        copy.commission = test.commission
        copy.begin = test.begin
        copy.end = test.end
        copy.description = test.description
        copy.account = test.account
        copy.time_step = test.time_step
        copy.status = Test.Status.NEW

        await cls.save(copy)

        return copy

    # }}}
    @classmethod  # requestAll  # {{{
    async def requestAll(cls) -> list[str]:
        logger.debug(f"{cls.__name__}.requestAll()")

        names = await Keeper.get(cls, get_only_names=True)
        return names

    # }}}

    @classmethod  # loadTrades  # {{{
    async def loadTrades(cls, test: Test) -> None:
        logger.debug(f"{cls.__name__}.loadTrades()")

        trade_list_name = f"{test}-trade_list"

        test.__trade_list = await TradeList.load(trade_list_name)
        test.__trade_list.setOwner(test)

    # }}}
    @classmethod  # deleteTrades  # {{{
    async def deleteTrades(cls, test: Test) -> None:
        logger.debug(f"{cls.__name__}.deleteTrades()")

        # если тест был загружен из БД без трейд листа, то
        # создаем трейд лист со стандартным именем новый и пустой,
        # иначе чистим в рантайме тот что уже загружен
        if test.__trade_list is None:
            test.__trade_list = TradeList(f"{test}-trade_list")
        else:
            test.__trade_list.clear()

        # а потом чистим в БД
        await TradeList.deleteTrades(test.__trade_list)

        test.__status = Test.Status.NEW
        await Test.update(test)

    # }}}

    @staticmethod  # toJson  # {{{
    def toJson(test: Test) -> str:
        logger.debug("Test.toJson()")

        obj = {
            "name": test.name,
            "strategy": test.strategy.name,
            "version": test.strategy.version,
            "figi": test.asset.figi,
            "enable_long": test.enable_long,
            "enable_short": test.enable_short,
            "deposit": test.deposit,
            "commission": test.commission,
            "begin_date": test.begin.isoformat(),
            "end_date": test.end.isoformat(),
            "description": test.description,
            "account": test.account,
            "trade_list": test.trade_list.name,
            "status": test.status.name,
            "time_step": str(test.time_step),
        }
        string = Cmd.toJson(obj)

        return string

    # }}}
    @staticmethod  # fromJson  # {{{
    async def fromJson(string: str) -> Test:
        logger.debug("Test.fromJson()")

        obj = Cmd.fromJson(string)

        test = Test(obj["name"])
        logger.info(f"   - loading {test}")

        test.strategy = await Strategy.load(obj["strategy"], obj["version"])
        test.asset = await Asset.fromFigi(obj["figi"])
        test.enable_long = obj["enable_long"]
        test.enable_short = obj["enable_short"]
        test.deposit = obj["deposit"]
        test.commission = obj["commission"]
        test.begin = date.fromisoformat(obj["begin_date"])
        test.end = date.fromisoformat(obj["end_date"])
        test.description = obj["description"]
        test.account = obj["account"]
        # test.trade_list = await TradeList.load(obj["trade_list"])
        test.status = Test.Status.fromStr(obj["status"])
        test.time_step = TimeFrame(obj["time_step"])

        # NOTE: при загрузке из БД не загружаем сразу трейд лист.
        # только по прямому вызову: await Test.loadTrades(test)
        test.trade_list = None

        return test

    # }}}


# }}}
class TestList:  # {{{
    def __init__(self, name: str, tests: Optional[list] = None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__name = name
        self.__tests = tests if tests else list()

        for test in self.__tests:
            test.test_list = self

    # }}}
    def __str__(self):  # {{{
        return f"TestList={self.__name}"

    # }}}
    def __getitem__(self, index: int) -> Test:  # {{{
        assert index < len(self.__tests)
        return self.__tests[index]

    # }}}
    def __iter__(self) -> Iterator:  # {{{
        return iter(self.__tests)

    # }}}
    def __contains__(self, test: Test) -> bool:  # {{{
        return any(i == test for i in self.__tests)

    # }}}
    def __len__(self):  # {{{
        return len(self.__tests)

    # }}}

    @property  # name  # {{{
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self.__name = name

    # }}}
    @property  # tests  # {{{
    def tests(self) -> list[Test]:
        return self.__tests

    @tests.setter
    def tests(self, tests: list[Test]):
        assert isinstance(tests, list)
        for i in tests:
            assert isinstance(i, Test)

        self.__tests = tests

    # }}}

    def add(self, test: Test) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")
        assert isinstance(test, Test)

        if test not in self:
            test.test_list = self
            self.__tests.append(test)
            return

        logger.warning(f"{test} already in list '{self.name}'")

    # }}}
    def remove(self, test: Test) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove()")

        try:
            self.__tests.remove(test)
            test.test_list = None
        except ValueError:
            logger.warning(f"'{test}' not in list '{self.name}'")

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")

        for test in self.__tests:
            test.test_list = None

        self.__tests.clear()

    # }}}

    @classmethod  # fromRecord  # {{{
    async def fromRecord(cls, name: str, record: asyncpg.Record) -> TestList:
        logger.debug(f"{cls.__name__}.fromRecord()")

        test_list = cls(name)
        for i in record:
            test = await Test.fromRecord(i)
            test_list.add(test)

        return test_list

    # }}}
    @classmethod  # save  # {{{
    async def save(cls, test_list: TestList) -> None:
        logger.debug(f"{cls.__name__}.save()")
        assert isinstance(test_list, TestList)

        await Keeper.delete(test_list)
        await Keeper.add(test_list)
        for test in test_list:
            await Test.save(test)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, name: str) -> TestList | None:
        logger.debug(f"{cls.__name__}.load()")

        logger.info(f":: Loading TestList {name}")
        test_list = await Keeper.get(cls, name=name)
        return test_list

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, test_list: TestList) -> None:
        logger.debug(f"{cls.__name__}.delete()")
        assert isinstance(test_list, TestList)

        await Keeper.delete(test_list)

    # }}}
    @classmethod  # requestAll# {{{
    async def requestAll(cls) -> list[str]:
        logger.debug(f"{cls.__name__}.requestAll()")

        names = await Keeper.get(cls, get_only_names=True)
        return names

    # }}}


# }}}


if __name__ == "__main__":
    ...
