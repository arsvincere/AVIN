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
from avin.core.chart import Chart
from avin.core.trade import Trade
from avin.utils import Cmd, logger


class Filter:  # {{{
    def __init__(  # {{{
        self, name: str, code: str, filter_list: Optional[FilterList] = None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__name = name
        self.__code = code
        self.__filter_list = filter_list
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
        self.__condition = self.__createCondition()

    # }}}
    @property  # path  # {{{
    def path(self) -> str:
        if self.__filter_list is None:
            dir_path = Usr.FILTER
        else:
            dir_path = self.__filter_list.path

        return Cmd.path(dir_path, f"{self.__name}.py")

    # }}}
    @property  # filter_list  # {{{
    def filter_list(self):
        return self.__filter_list

    # }}}
    @property  # full_name  # {{{
    def name(self):
        full_name = f"{self.__name}"

        parent = self.__filter_list
        while parent is not None:
            full_name = parent.name + "-" + full_name
            parent = parent.parent_list

        return full_name

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

        new_path = Cmd.path(Usr.FILTER, f"{new_name}.py")
        Cmd.copy(f.path, new_path)

        f_copy = Filter.load(new_name)
        return f_copy

    # }}}
    @classmethod  # rename  # {{{
    def rename(cls, f: Filter, new_name: str) -> Filter | None:
        logger.debug(f"{cls.__name__}.rename()")

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

    def __createCondition(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createCondition()")

        context = globals().copy()
        exec(self.__code, context)

        self.__conditionChart = context["conditionChart"]
        self.__conditionAsset = context["conditionAsset"]
        self.__conditionTrade = context["conditionTrade"]

    # }}}


# }}}
class FilterList:  # {{{
    def __init__(  # {{{
        self,
        name: str,
        filters: Optional[list] = None,
        parent: Optional[FilterList] = None,
        childs: Optional[FilterList] = None,
    ):
        logger.debug(f"{self.__class__.__name__}.__init__({name})")

        self.__name = name
        self.__filters = filters if filters else list()
        self.__parent_list = parent
        self.__childs = childs if childs else list()

    # }}}
    def __str__(self) -> str:  # {{{
        return f"FilterList={self.__name}"

    # }}}
    def __getitem__(self, index: int) -> Filter:  # {{{
        assert index < len(self.__filters)
        return self.__filters[index]

    # }}}
    def __iter__(self) -> Iterator:  # {{{
        return iter(self.__filters)

    # }}}
    def __contains__(self, f: Filter) -> bool:  # {{{
        return any(i == f for i in self.__filters)

    # }}}
    def __len__(self):  # {{{
        return len(self.__filters)

    # }}}

    @property  # name  # {{{
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self.__name = name

    # }}}
    @property  # filters  # {{{
    def filters(self) -> list[Filter]:
        return self.__filters

    @filters.setter
    def filters(self, filters: list[Filter]):
        assert isinstance(filters, list)
        for i in self.__filters:
            assert isinstance(i, Filter)

        self.__filters = filters

    # }}}
    @property  # childs  # {{{
    def childs(self):
        return self.__childs

    @childs.setter
    def childs(self, childs: list[FilterList]):
        assert isinstance(childs, list)
        for i in self.__childs:
            assert isinstance(i, FilterList)

        self.__childs = childs

    # }}}
    @property  # parent_list  # {{{
    def parent_list(self):
        return self.__parent_list

    @parent_list.setter
    def parent_list(self, parent: FilterList):
        assert isinstance(parent, FilterList)

        self.__parent_list = parent

    # }}}
    @property  # path  # {{{
    def path(self) -> str:
        if self.__parent_list is None:
            dir_path = Usr.FILTER
        else:
            dir_path = self.__filter_list.path

        return Cmd.path(dir_path, f"{self.__name}")

    # }}}

    def add(self, f: Filter) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add({f.ticker})")
        assert isinstance(f, Filter)

        if f not in self:
            self.__filters.append(f)
            return

        logger.warning(f"{f} already in {self}")

    # }}}
    def remove(self, f: Filter) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove({f.ticker})")

        try:
            self.__filters.remove(f)
        except ValueError:
            logger.warning(f"'{f}' not in {self}")

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")

        self.__filters.clear()

    # }}}

    def addChild(self, child: FilterList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.addChild()")

        self.__childs.append(child)

    # }}}
    def removeChild(self, child: FilterList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeChild()")

        self.__childs.append(child)

        try:
            self.__filters.remove(f)
        except ValueError:
            logger.warning(f"{child} not in {self}")

    # }}}
    def clearChilds(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearChilds()")

        self.__childs.clear()

    # }}}

    @classmethod  # load  # {{{
    def load(cls, name: str) -> FilterList | None:
        logger.debug(f"{cls.__name__}.load()")

        dir_path = Cmd.path(Usr.FILTER, name)
        if not Cmd.isExist(path):
            return None

        filter_list = FilterList(name)
        FilterList.__loadChilds(filter_list)

    # }}}
    @classmethod  # requestAll # {{{
    def requestAll(cls) -> list[str]:
        logger.debug(f"{cls.__name__}.requestAll()")

        if not Cmd.isExist(Usr.FILTER):
            Cmd.makeDirs(Usr.FILTER)

        names = Cmd.getDirs(Usr.FILTER)
        return names

    # }}}


# }}}


if __name__ == "__main__":
    ...
