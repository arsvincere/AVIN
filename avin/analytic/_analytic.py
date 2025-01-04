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

from avin.config import Usr
from avin.core import Asset
from avin.keeper import Keeper
from avin.utils import Cmd, logger


class Analytic(ABC):  # {{{
    @classmethod
    @abstractmethod  # classmethod update  # {{{
    async def update(cls, analytic_name) -> None:
        logger.debug(f"{cls.__name__}.update()")

        uanalytic = await Analytic.load(analytic_name)
        await uanalytic.update()

    # }}}
    @classmethod  # updateAll  # {{{
    async def updateAll(cls):
        logger.debug(f"{cls.__name__}.updateAll()")

        all_uanalytic_names = await cls.requestAll()
        for name in all_uanalytic_names:
            await cls.update(name)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, analytic_name: str) -> Analytic:
        logger.debug(f"{cls.__name__}.load()")

        file_path = Cmd.path(Usr.ANALYTIC, f"{analytic_name}.py")
        if not Cmd.isExist(file_path):
            assert False, f"Analytic {analytic_name} not found"

        path = f"usr.analytic.{analytic_name}"
        modul = importlib.import_module(path)
        UAnalytic = modul.__getattribute__("UAnalytic")
        uanalytic = UAnalytic()

        return uanalytic

    # }}}
    @classmethod  # requestAll# {{{
    async def requestAll(cls) -> list[str]:
        logger.debug(f"{cls.__name__}.requestAll()")

        names = await Keeper.get(cls, get_only_names=True)
        return names

    # }}}


# }}}
class AnalyticData:  # {{{
    def __init__(self, name: str, asset: Asset, json_str: str):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__name = name
        self.__asset = asset
        self.__json_str = json_str

    # }}}

    @property  # name  # {{{
    def name(self):
        return self.__name

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

        name = record["analytic_name"]
        asset = Asset.fromRecord(record)
        json_str = record["analyse_json"]

        analytic_data = AnalyticData(name, asset, json_str)
        return analytic_data

    # }}}
    @classmethod  # save  # {{{
    async def save(cls, analytic_data: AnalyticData) -> None:
        logger.debug(f"{cls.__name__}.save()")

        await Keeper.delete(analytic_data)
        await Keeper.add(analytic_data)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, name: str, asset: Asset) -> AnalyticData | None:
        logger.debug(f"{cls.__name__}.load()")

        analytic_data = await Keeper.get(cls, name=name, figi=asset.figi)
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
