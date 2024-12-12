#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum
from datetime import date, timedelta

from avin.const import ONE_MINUTE
from avin.core import StrategySet, Summary, TradeList
from avin.keeper import Keeper
from avin.utils import Signal, logger

# TODO:
# ( ) 1. Сделать тест атомарным: одна стратегия, один актив, один TradeList
# ( ) 2. Summary - можно пределать теперь к трейд листу
# ( ) 3. Tester - прогоняет тест, просто и очевидно все
#        Возможно в будущем появится более сложный тестер который
#        будет учитывать и несколько стретегий и несколько активов и
#        и деньги на счету...
# ( ) 4. GUI визуализация - это будет уже надстройка над Test
#        а не над TradeList, а из теста можно будет достать
#        и asset, begin, end, trades
#        и без всяких там owner и прочей хуйни можно будет
#        визуализировать тест.
#        GTest - придет на смену GTradeList
# ( ) 5. Над тестами можно построить TestList
#        Который сможет объединять сколько угодно тестов
#        по разным стратегиям, по разным активам, как угодно, лишь бы
#        без дублей, один и тот же тест нельзя добавить.
#        И вот тут уже можно делать более сложную версию Report
#        которая будет не просто там трейд лист смотреть и делать по нему
#        Summary а делать разрезы...
#        по дням, неделям, месяцам, кварталам, годам
#        по стратегиям, по версиям
#        по аккаунтом по брокерам...
#        как это делать - вот дойдет до этого время там и буду делать.
#        Но если на входе отдельные трейд листы - то не проблема повыбирать
#        из них то что нужно.
#        В крайнем случае - это будет отдельный модуль
#        он будет принимать в себя даже не трейд листы а просто кучу трейдов
#        и будет работать с ними через базу данных


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
        self.__strategy_set = StrategySet(f"{name}-sset")
        self.__trade_list = TradeList(f"{name}-tlist")
        self.__report = Summary(test=self)
        self.__deposit = 100000.0
        self.__commission = 0.0005
        self.__begin = date(2018, 1, 1)
        self.__end = date(2023, 1, 1)
        self.__description = ""
        self.__account = "_backtest"
        self.__time_step = ONE_MINUTE

        # signals
        self.progress = Signal(int)

    # }}}
    def __str__(self):  # {{{
        return f"Test='{self.name}'"

    # }}}

    @property  # name# {{{
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name) -> bool:
        self.__name = new_name
        self.__strategy_set.name = f"{new_name}-sset"
        self.__trade_list.name = f"{new_name}-tlist"

    # }}}
    @property  # status# {{{
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status) -> bool:
        self.__status = new_status

    # }}}
    @property  # strategy_set# {{{
    def strategy_set(self):
        return self.__strategy_set

    @strategy_set.setter
    def strategy_set(self, strategy_set: StrategySet):
        strategy_set.name = f"{self.__name}-sset"
        self.__strategy_set = strategy_set

    # }}}
    @property  # trade_list# {{{
    def trade_list(self):
        return self.__trade_list

    @trade_list.setter
    def trade_list(self, trade_list: TradeList):
        trade_list.name = f"{self.__name}-tlist"
        self.__trade_list = trade_list

    # }}}
    @property  # report# {{{
    def report(self):
        return self.__report

    @report.setter
    def report(self, report: Summary):
        self.__report = report

    # }}}
    @property  # deposit# {{{
    def deposit(self):
        return self.__deposit

    @deposit.setter
    def deposit(self, deposit: float):
        self.__deposit = deposit

    # }}}
    @property  # commission# {{{
    def commission(self):
        return self.__commission

    @commission.setter
    def commission(self, commission):
        self.__commission = commission

    # }}}
    @property  # begin# {{{
    def begin(self) -> date:
        return self.__begin

    @begin.setter
    def begin(self, begin: date):
        assert isinstance(begin, date)
        self.__begin = begin

    # }}}
    @property  # end# {{{
    def end(self) -> date:
        return self.__end

    @end.setter
    def end(self, end: date):
        assert isinstance(end, date)
        self.__end = end

    # }}}
    @property  # description# {{{
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
    @property  # time_step  # {{{
    def time_step(self):
        return self.__time_step

    @time_step.setter
    def time_step(self, time_step: timedelta):
        self.__time_step = time_step

    # }}}

    def updateSummary(self):  # {{{
        logger.debug("Test.updateSummary()")
        self.__report = Summary(test=self)

    # }}}
    async def clear(self):  # {{{
        logger.debug("Test.clear()")

        self.__trade_list.clear()  # clear runtime
        await Keeper.delete(self.__trade_list, only_trades=True)  # in db

        self.__report.clear()  # TODO: че выпиливаем report summary или как?
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
        test.__report = Summary(test)

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
        # save Summary????

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
    async def rename(cls, test, new_name: str) -> Test | None:
        logger.debug(f"{cls.__name__}.rename()")

        # check new name
        availible = await cls.__checkName(new_name)
        if not availible:
            return None

        await cls.delete(test)
        test.name = new_name
        await cls.save(test)

        return test

    # }}}
    @classmethod  # copy# {{{
    async def copy(cls, test, new_name: str) -> Test | None:
        logger.debug(f"{cls.__name__}.copy()")

        # check new name
        availible = await cls.__checkName(new_name)
        if not availible:
            return None

        new_test = Test(new_name)
        new_test.status = test.status
        new_test.strategy_set = test.strategy_set
        new_test.trade_list = test.trade_list
        new_test.report = test.report
        new_test.deposit = test.deposit
        new_test.commission = test.commission
        new_test.begin = test.begin
        new_test.end = test.end
        new_test.description = test.description
        new_test.account = test.account
        new_test.time_step = test.time_step

        await cls.save(new_test)
        return new_test

    # }}}
    @classmethod  # requestAll# {{{
    async def requestAll(cls) -> list[str]:
        logger.debug(f"{cls.__name__}.requestAll()")

        names = await Keeper.get(cls, get_only_names=True)
        return names

    # }}}

    @classmethod  # __checkName{{{
    async def __checkName(cls, name):
        logger.debug(f"{cls.__name__}.__checkName()")

        existed_names = await cls.requestAll()
        if name in existed_names:
            return False

        return True

    # }}}


if __name__ == "__main__":
    ...
