#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional

from avin.config import Usr
from avin.data.data_type import DataType
from avin.data.instrument import Instrument
from avin.utils import Cmd, logger


@dataclass  # ConvertTask  # {{{
class ConvertTask:
    instrument: Instrument
    in_type: DataType
    out_type: DataType

    @classmethod  # toCSV  # {{{
    def toCSV(cls, task: ConvertTask) -> str:
        logger.debug(f"{cls.__name__}.toCSV()")

        string = f"{task.instrument};{task.in_type};{task.out_type};"
        return string

    # }}}
    @classmethod  # fromCSV  # {{{
    async def fromCSV(cls, string: str) -> ConvertTask:
        logger.debug(f"{cls.__name__}.fromCSV()")

        INSTRUMENT, FROM, TO = range(3)
        fields = string.split(";")

        instrument = await Instrument.fromStr(fields[INSTRUMENT])
        in_type = DataType.fromStr(fields[FROM])
        out_type = DataType.fromStr(fields[TO])

        convert_task = cls(instrument, in_type, out_type)
        return convert_task

    # }}}


# }}}
class ConvertTaskList:  # {{{
    def __init__(
        self, name: str, tasks: Optional[list[ConvertTask]] = None
    ):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__name = name
        self.__tasks = tasks if tasks else list()

    # }}}
    def __str__(self) -> str:  # {{{
        return f"ConvertTaskList={self.__name}"

    # }}}
    def __getitem__(self, index: int) -> ConvertTask:  # {{{
        assert index < len(self.__tasks)
        return self.__tasks[index]

    # }}}
    def __iter__(self) -> Iterator:  # {{{
        return iter(self.__tasks)

    # }}}
    def __contains__(self, task: ConvertTask) -> bool:  # {{{
        return any(i == task for i in self.__tasks)

    # }}}
    def __len__(self):  # {{{
        return len(self.__tasks)

    # }}}

    @property  # name  # {{{
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self.__name = name

    # }}}
    @property  # path  # {{{
    def path(self) -> str:
        file_path = Cmd.path(Usr.DATA, f"{self.__name}.csv")
        return file_path

    # }}}

    def add(self, task: ConvertTask) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")

        if task not in self:
            self.__tasks.append(task)
            return

        logger.warning(f"{task} already in {self}'")

    # }}}
    def remove(self, task: ConvertTask) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove()")

        try:
            self.__tasks.remove(task)
        except ValueError:
            logger.warning(
                "ConvertTaskList.remove(task) failed: "
                f"'{task}' not in list"
            )

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")

        self.__tasks.clear()

    # }}}

    @classmethod  # save  # {{{
    def save(cls, convert_list: ConvertTaskList) -> None:
        logger.debug(f"{cls.__name__}.save()")

        text = list()
        for task in convert_list:
            string = ConvertTask.toCSV(task) + "\n"
            text.append(string)

        Cmd.saveText(text, convert_list.path)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, name: str) -> ConvertTaskList:
        logger.debug(f"{cls.__name__}.load()")

        file_path = Cmd.path(Usr.DATA, f"{name}.csv")
        text = Cmd.loadText(file_path)
        clist = ConvertTaskList(name)

        for row in text:
            task = await ConvertTask.fromCSV(row)
            clist.add(task)

        return clist

    # }}}
    @classmethod  # delete  # {{{
    def delete(cls, convert_list: ConvertTaskList) -> None:
        logger.debug(f"{cls.__name__}.delete()")
        assert isinstance(convert_list, ConvertTaskList)

        file_path = convert_list.path
        if Cmd.isExist(file_path):
            Cmd.delete(file_path)

    # }}}


# }}}


if __name__ == "__main__":
    ...
