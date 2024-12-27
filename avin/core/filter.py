#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin.config import Usr
from avin.const import Res
from avin.core.asset import Asset
from avin.core.chart import Chart
from avin.core.trade import Trade
from avin.utils import Cmd, logger


class Filter:
    def __init__(self, name: str, code: str):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__name = name
        self.__code = code
        self.__createCondition()

    # }}}

    @property  # name  # {{{
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    # }}}
    @property  # code  # {{{
    def code(self):
        return self.__code

    @code.setter
    def code(self, code):
        self.__code = code
        self.__condition = self.__createCondition(code)

    # }}}
    @property  # path  # {{{
    def path(self) -> str:
        return Cmd.path(Usr.FILTER, f"{self.__name}.py")

    # }}}

    async def acheck(self, item: Asset | Trade | Chart) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.check()")

        class_name = item.__class__.__name__
        match class_name:
            case "Chart":
                result = await self.__conditionChart(item)
            case "Asset":
                result = await self.__conditionAsset(item)
            case "Share":
                result = await self.__conditionAsset(item)
            case "Trade":
                result = await self.__conditionTrade(item)

        return result

    # }}}

    @classmethod  # new  # {{{
    def new(cls, name: str) -> Filter | None:
        logger.debug(f"{cls.__name__}.new()")

        # check name
        if not cls.__checkName(name):
            return None

        # copy template to user directory
        template_path = Cmd.path(Res.TEMPLATE, "filter", "filter.py")
        user_path = Cmd.path(Usr.FILTER, f"{name}.py")
        Cmd.copy(template_path, user_path)

        # load
        f = cls.load(name)

        return f

    # }}}
    @classmethod  # edit  # {{{
    def edit(cls, f: Filter) -> Filter:
        logger.debug(f"{cls.__name__}.edit()")

        command = [
            Usr.TERMINAL,
            *Usr.OPT,
            Usr.EXEC,
            Usr.EDITOR,
            f.path,
        ]
        Cmd.subprocess(command)

        code = Cmd.read(f.path)
        f.code = code

        return f

    # }}}
    @classmethod  # save  # {{{
    def save(cls, f: Filter, file_path=None) -> None:
        logger.debug(f"{cls.__name__}.save()")

        if file_path is None:
            file_path = f.path

        Cmd.write(f.code, file_path)

    # }}}
    @classmethod  # load  # {{{
    def load(cls, name: str) -> Filter | None:
        logger.debug(f"{cls.__name__}.load()")

        file_path = Cmd.path(Usr.FILTER, f"{name}.py")
        if not Cmd.isExist(file_path):
            return None

        code = Cmd.read(file_path)

        f = Filter(name, code)
        return f

    # }}}
    @classmethod  # copy  # {{{
    def copy(cls, f: Filter, new_name: str) -> Filter | None:
        logger.debug(f"{cls.__name__}.copy()")

        if not cls.__checkName(new_name):
            logger.error(f"{new_name} already exist, copy canceled")
            return None

        new_path = Cmd.path(Usr.FILTER, f"{new_name}.py")
        Cmd.copy(f.path, new_path)

        f_copy = Filter.load(new_name)
        return f_copy

    # }}}
    @classmethod  # rename  # {{{
    def rename(cls, f: Filter, new_name: str) -> Filter | None:
        logger.debug(f"{cls.__name__}.rename()")

        if not cls.__checkName(new_name):
            logger.error(f"{new_name} already exist, rename canceled")
            return None

        if Cmd.isExist(f.path):
            new_path = Cmd.path(Usr.FILTER, f"{new_name}.py")
            Cmd.rename(f.path, new_path)

        renamed = Filter.load(new_name)
        return renamed

    # }}}
    @classmethod  # delete  # {{{
    def delete(cls, f: Filter) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        Cmd.delete(f.path)

    # }}}
    @classmethod  # requestAll  # {{{
    def requestAll(cls) -> list[str]:
        logger.debug(f"{cls.__name__}.requestAll()")

        files = Cmd.getFiles(Usr.FILTER)
        files = Cmd.select(files, extension=".py")

        all_names = list()
        for file in files:
            name = Cmd.name(file)
            all_names.append(name)

        return all_names

    # }}}

    def __createCondition(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createCondition()")

        context = globals().copy()
        exec(self.__code, context)

        self.__conditionChart = context["conditionChart"]
        self.__conditionAsset = context["conditionAsset"]
        self.__conditionTrade = context["conditionTrade"]

    # }}}
    @classmethod  # __checkName  # {{{
    def __checkName(cls, name) -> bool:
        logger.debug(f"{cls.__name__}.__checkName()")

        existed_names = cls.requestAll()
        return name not in existed_names

    # }}}


if __name__ == "__main__":
    ...
