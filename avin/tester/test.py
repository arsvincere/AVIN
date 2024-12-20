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
from avin.core import Asset, Strategy, Summary, TradeList
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
        logger.debug(f"{self.__class__.__name__}.__init__()")

        # default values:
        self.__name = name
        self.__strategy = None
        self.__asset = None
        self.__enable_long = True
        self.__enable_short = True
        self.__trade_list = TradeList(f"{self}-trade_list")
        self.__deposit = 100000.0
        self.__commission = 0.0005
        self.__begin = date(2018, 1, 1)
        self.__end = date(2023, 1, 1)
        self.__description = ""
        self.__account = "_backtest"
        self.__time_step = ONE_MINUTE
        self.__status = Test.Status.NEW

        # set owner
        self.__trade_list.setOwner(self)

        # signals
        self.progress = Signal(int)

    # }}}
    def __str__(self):  # {{{
        return f"Test={self.name}"

    # }}}

    @property  # name  # {{{
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

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
    @property  # trade_list  # {{{
    def trade_list(self):
        return self.__trade_list

    @trade_list.setter
    def trade_list(self, trade_list: TradeList):
        trade_list.name = f"{self}-trade_list"
        self.__trade_list = trade_list

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
    @property  # time_step  # {{{
    def time_step(self):
        return self.__time_step

    @time_step.setter
    def time_step(self, time_step: timedelta):
        self.__time_step = time_step

    # }}}
    @property  # status  # {{{
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status):
        self.__status = new_status

    # }}}

    def summary(self) -> Summary:  # {{{
        logger.debug(f"{self.__class__.__name__}.summary()")

        summary = Summary(self.__trade_list)
        return summary

    # }}}

    @classmethod  # fromRecord  # {{{
    async def fromRecord(cls, record: asyncpg.Record) -> Test:
        logger.debug(f"{cls.__name__}.fromRecord()")

        asset = Asset.fromRecord(record)
        strategy = await Strategy.load(
            record["strategy"],
            record["version"],
        )

        test = Test(record["name"])
        test.__strategy = strategy
        test.__asset = asset
        test.__enable_long = record["enable_long"]
        test.__enable_short = record["enable_short"]
        test.__deposit = record["deposit"]
        test.__commission = record["commission"]
        test.__begin = record["begin_date"]
        test.__end = record["end_date"]
        test.__description = record["description"]
        test.__status = Test.Status.fromStr(record["status"])

        # request trade list
        loaded = await TradeList.load(record["trade_list"])
        assert loaded is not None
        test.__trade_list = loaded
        test.__trade_list.setOwner(test)

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

        await Test.delete(test)
        test.name = new_name
        await Test.save(test)

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

        return copy

    # }}}
    @classmethod  # requestAll  # {{{
    async def requestAll(cls) -> list[str]:
        logger.debug(f"{cls.__name__}.requestAll()")

        names = await Keeper.get(cls, get_only_names=True)
        return names

    # }}}
    @classmethod  # deleteTrades  # {{{
    async def deleteTrades(cls, test: Test) -> None:
        logger.debug(f"{cls.__name__}.deleteTrades()")

        test.__trade_list.clear()  # clear runtime
        await TradeList.deleteTrades(test.__trade_list)  # clear db

        test.__status = Test.Status.NEW
        await Test.update(test)

    # }}}

    @classmethod  # toJson  # {{{
    def toJson(cls, test: Test) -> dict:
        logger.debug(f"{cls.__name__}.toJson()")

        obj = {
            "name": test.name,
            "strategy": test.strategy.name,
            "version": test.strategy.version,
            "asset": str(test.asset),
            "enable_long": test.enable_long,
            "enable_short": test.enable_short,
            "deposit": test.deposit,
            "commission": test.commission,
            "begin_date": test.begin.isoformat(),
            "end_date": test.end.isoformat(),
            "description": test.description,
            "status": test.status.name,
        }
        return obj

    # }}}
    @classmethod  # fromJson  # {{{
    async def fromJson(cls, obj) -> Test:
        logger.debug(f"{cls.__name__}.fromJson()")

        test = Test(obj["name"])
        test.strategy = await Strategy.load(obj["strategy"], obj["version"])
        test.asset = await Asset.fromStr(obj["asset"])
        test.enable_long = obj["enable_long"]
        test.enable_short = obj["enable_short"]
        test.deposit = obj["deposit"]
        test.commission = obj["commission"]
        test.begin = date.fromisoformat(obj["begin_date"])
        test.end = date.fromisoformat(obj["end_date"])
        test.description = obj["description"]
        test.status = Test.Status.fromStr(obj["status"])

        return test

    # }}}


if __name__ == "__main__":
    ...
