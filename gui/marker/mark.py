#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin import Cmd, Filter, Usr, logger
from gui.marker.gshape import GShape


class Mark:  # {{{
    def __init__(  # {{{
        self, filter: Filter, shape: GShape, parent=None
    ):
        self.__filter = filter
        self.__shape = shape

    # }}}

    @property  # name  # {{{
    def name(self):
        return self.__filter.name

    # }}}
    @property  # filter  # {{{
    def filter(self):
        return self.__filter

    # }}}
    @property  # shape  # {{{
    def shape(self):
        # create new shape graphic item
        shape = GShape(
            self.__shape.type, self.__shape.size, self.__shape.color
        )
        return shape

    # }}}

    @classmethod  # toCSV  # {{{
    def toCSV(cls, mark: Mark) -> str:
        logger.debug(f"{cls.__name__}.toCSV()")

        string = (
            f"{mark.name};"
            f"{mark.shape.type.name};"
            f"{mark.shape.size.name};"
            f"{mark.shape.color.name};"
        )
        return string

    # }}}
    @classmethod  # fromCSV  # {{{
    def fromCSV(cls, string: str) -> Mark:
        logger.debug(f"{cls.__name__}.fromCSV()")

        FILTER_NAME, TYPE, SIZE, COLOR = range(4)
        fields = string.split(";")

        f = Filter.load(fields[FILTER_NAME])
        t = GShape.Type.fromStr(fields[TYPE])
        s = GShape.Size.fromStr(fields[SIZE])
        c = GShape.Color.fromStr(fields[COLOR])

        gshape = GShape(t, s, c)
        mark = Mark(f, gshape)

        return mark

    # }}}


# }}}
class MarkList:  # {{{
    def __init__(self, name: str, markers: Optional[list] = None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__({name})")

        self.__name = name
        self.__marks = markers if markers else list()

    # }}}
    def __str__(self) -> str:  # {{{
        return f"MarkList={self.__name}"

    # }}}
    def __getitem__(self, index: int) -> Mark:  # {{{
        assert index < len(self.__marks)
        return self.__marks[index]

    # }}}
    def __iter__(self) -> Iterator:  # {{{
        return iter(self.__marks)

    # }}}
    def __contains__(self, mark: Mark) -> bool:  # {{{
        return any(i == mark for i in self.__marks)

    # }}}
    def __len__(self):  # {{{
        return len(self.__marks)

    # }}}

    @property  # name  # {{{
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self.__name = name

    # }}}
    @property  # markers  # {{{
    def markers(self) -> list[Mark]:
        return self.__marks

    @markers.setter
    def markers(self, markers: list[Mark]):
        assert isinstance(markers, list)
        for i in self.__marks:
            assert isinstance(i, Mark)

        self.__marks = markers

    # }}}
    @property  # path  # {{{
    def path(self) -> str:
        file_path = Cmd.path(Usr.MARK, f"{self.__name}.csv")
        return file_path

    # }}}

    def add(self, mark: Mark) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")
        assert isinstance(mark, Mark)

        if mark not in self:
            self.__marks.append(mark)
            return

        logger.warning(f"{mark} already in list '{self.name}'")

    # }}}
    def remove(self, mark: Mark) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove()")

        try:
            self.__marks.remove(mark)
        except ValueError:
            logger.exception(
                f"MarkList.remove(mark) failed: " f"'{mark}' not in list",
            )

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")

        self.__marks.clear()

    # }}}

    @classmethod  # save  # {{{
    def save(cls, marker_list: MarkList) -> None:
        logger.debug(f"{cls.__name__}.save()")
        assert isinstance(marker_list, MarkList)

        text = list()
        for mark in marker_list.__marks:
            string = Mark.toCSV(mark) + "\n"
            text.append(string)

        file_path = marker_list.path

        Cmd.saveText(text, file_path)

    # }}}
    @classmethod  # load  # {{{
    def load(cls, name: str) -> MarkList | None:
        logger.debug(f"{cls.__name__}.load()")

        file_path = Cmd.path(Usr.MARK, f"{name}.csv")
        if not Cmd.isExist(file_path):
            logger.error(f"MarkList={name} not found")
            return None

        text = Cmd.loadText(file_path)
        mark_list = MarkList(name)
        for line in text:
            mark = Mark.fromCSV(line)
            mark_list.add(mark)

        return mark_list

    # }}}
    @classmethod  # delete  # {{{
    def delete(cls, marker_list: MarkList) -> None:
        logger.debug(f"{cls.__name__}.delete()")
        assert isinstance(marker_list, MarkList)

        file_path = marker_list.path
        if Cmd.isExist(file_path):
            Cmd.delete(file_path)

    # }}}
    @classmethod  # rename  # {{{
    def rename(cls, marker_list: MarkList, new_name: str) -> None:
        logger.debug(f"{cls.__name__}.rename()")

        assert isinstance(new_name, str)
        assert len(new_name) > 0

        cls.delete(marker_list)
        marker_list.name = new_name
        cls.save(marker_list)

    # }}}
    @classmethod  # copy  # {{{
    def copy(cls, marker_list: MarkList, new_name: str) -> None:
        logger.debug(f"{cls.__name__}.copy()")

        new_list = cls(new_name)
        new_list.markers = marker_list.markers
        cls.save(new_list)

    # }}}


# }}}


if __name__ == "__main__":
    ...
