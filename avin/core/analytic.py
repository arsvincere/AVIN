#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import importlib
from abc import ABC, abstractmethod

import asyncpg

from avin.config import Auto, Usr
from avin.core.asset import Asset
from avin.keeper import Keeper
from avin.utils import Cmd, logger


class Analytic(ABC):  # {{{
    __AUTO_UPDATE = Auto.UPDATE_ANALYTIC
    __UPDATE_PERIOD = Auto.UPDATE_ANALYTIC_PERIOD
    __LAST_UPDATE_FILE = Cmd.path(Usr.ANALYTIC, "last_update")
    __ANALYTIC_IS_UP_TO_DATE = False

    @classmethod  # abstractmethod update  # {{{
    @abstractmethod
    async def update(cls, analytic_name) -> None:
        logger.debug(f"{cls.__name__}.update()")

        uanalytic = await Analytic.load(analytic_name)
        cls.save(uanalytic)
        await uanalytic.update()

    # }}}

    @classmethod  # save  # {{{
    async def save(cls, uanalytic):
        logger.debug(f"{cls.__name__}.save()")

        await Keeper.delete(cls, name=uanalytic.name)
        await Keeper.add(cls, name=uanalytic.name)

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, uanalytic):
        logger.debug(f"{cls.__name__}.delete()")

        await Keeper.delete(uanalytic)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, analytic_name: str) -> Analytic:
        logger.debug(f"{cls.__name__}.load()")

        await cls.__checkUpdate()

        file_path = Cmd.path(Usr.ANALYTIC, f"{analytic_name}.py")
        if not Cmd.isExist(file_path):
            assert False, f"Analytic {analytic_name} not found"

        path = f"usr.analytic.{analytic_name}"
        modul = importlib.import_module(path)
        UAnalytic = modul.__getattribute__("UAnalytic")
        uanalytic = UAnalytic

        return uanalytic

    # }}}
    @classmethod  # requestAll# {{{
    async def requestAll(cls) -> list[str]:
        logger.debug(f"{cls.__name__}.requestAll()")

        all_names = list()
        if not Cmd.isExist(Usr.ANALYTIC):
            Cmd.makeDirs(Usr.ANALYTIC)
            return all_names

        file_names = Cmd.getFiles(Usr.ANALYTIC)
        for file in file_names:
            name = Cmd.name(file)
            if name != "__init__":
                all_names.append(name)

        return all_names

    # }}}
    @classmethod  # updateAll  # {{{
    async def updateAll(cls):
        logger.debug(f"{cls.__name__}.updateAll()")

        all_uanalytic_names = await cls.requestAll()
        for name in all_uanalytic_names:
            await cls.update(name)

    # }}}

    @classmethod  # __checkUpdate  # {{{
    def __checkUpdate(cls):
        logger.debug(f"{cls.__name__}.checkUpdate()")

        # check update flag
        if cls.__ANALYTIC_IS_UP_TO_DATE:
            return

        # check update settings
        if not cls.__AUTO_UPDATE:
            return

        # ckeck file with last update datetime
        if not Cmd.isExist(cls.__LAST_UPDATE_FILE):
            need_update = True
        else:
            # read file, check last update > month ago
            dt_str = Cmd.read(cls.__LAST_UPDATE_FILE)
            last_update = datetime.fromisoformat(dt_str)
            need_update = (now() - last_update) > cls.__UPDATE_PERIOD

        if not need_update:
            return

        # update all user analytics
        logger.info(":: Need update user analytic - starting update")
        await cls.updateAll()

        # save update datetime
        dt = now().isoformat()
        Cmd.write(dt, cls.__LAST_UPDATE_FILE)

        # set class flag
        cls.__ANALYTIC_IS_UP_TO_DATE = True

    # }}}


# }}}
class AnalyticData:  # {{{
    def __init__(  # {{{
        self,
        analytic_name: str,
        analyse_name: str,
        asset: Asset,
        json_str: str,
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__analytic_name = analytic_name
        self.__analyse_name = analyse_name
        self.__asset = asset
        self.__json_str = json_str

    # }}}

    @property  # analytic_name  # {{{
    def analytic_name(self):
        return self.__analytic_name

    # }}}
    @property  # analyse_name  # {{{
    def analyse_name(self):
        return self.__analyse_name

    # }}}
    @property  # asset  # {{{
    def asset(self):
        return self.__asset

    # }}}
    @property  # json_str  # {{{
    def json_str(self):
        return self.__json_str

    # }}}

    @classmethod  # fromRecord  # {{{
    async def fromRecord(cls, record: asyncpg.Record) -> None:
        logger.debug(f"{cls.__name__}.fromRecord()")

        analytic_name = record["analytic_name"]
        analyse_name = record["analyse_name"]
        asset = await Asset.fromFigi(record["figi"])
        json_str = record["analyse_json"]

        analytic_data = AnalyticData(analytic_, analyse_name, asset, json_str)
        return analytic_data

    # }}}
    @classmethod  # save  # {{{
    async def save(cls, analytic_data: AnalyticData) -> None:
        logger.debug(f"{cls.__name__}.save()")

        await Keeper.delete(analytic_data)
        await Keeper.add(analytic_data)

    # }}}
    @classmethod  # load  # {{{
    async def load(
        cls, analytic_name: str, analyse_name: str, asset: Asset
    ) -> AnalyticData | None:
        logger.debug(f"{cls.__name__}.load()")

        analytic_data = await Keeper.get(
            cls,
            analytic_name=analytic_name,
            analyse_name=analyse_name,
            figi=asset.figi,
        )
        return analytic_data

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, analytic_data: AnalyticData) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        await Keeper.delete(analytic_data)

    # }}}


# }}}


class Indicator:  # {{{
    @staticmethod  # BEAR_LEN# {{{
    def BEAR_LEN(chart):
        assert chart.last is not None
        i = -1
        while chart[i] is not None and chart[i].isBear():
            i -= 1
        return abs(i + 1)

    # }}}
    @staticmethod  # BULL_LEN# {{{
    def BULL_LEN(chart):
        assert chart.last is not None
        i = -1
        while chart[i] is not None and chart[i].isBull():
            i -= 1
        return abs(i + 1)

    # }}}
    @staticmethod  # SPEED# {{{
    def SPEED(chart, period):
        assert chart.last is not None

        if chart[-1] is None or chart[-period - 1] is None:
            return None

        first = chart[-period - 1].body.mid()
        last = chart[-1].body.mid()
        delta = last - first

        percent = delta / first * 100
        speed = percent / period

        return speed

    # }}}
    @staticmethod  # MA# {{{
    def MA(chart, period, parameter="close"):
        assert chart.last is not None
        total = 0
        for i in range(-1, -period - 1, -1):
            if chart[i] == None:
                return None
            total += chart[i].close
        return total / period

    # }}}


# }}}


if __name__ == "__main__":
    ...
