#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum
from datetime import timedelta

from avin.utils import Cmd


class DataType(enum.Enum):  # {{{
    """doc# {{{
    Enum for selet what data type want to download.
    """

    # }}}
    BAR_1M = "1M"
    BAR_5M = "5M"
    BAR_10M = "10M"
    BAR_1H = "1H"
    BAR_D = "D"
    BAR_W = "W"
    BAR_M = "M"
    TIC = "tic"
    BOOK = "book"
    ANALYSE = "analyse"

    def __hash__(self):  # {{{
        return hash(self.name)

    # }}}
    def toTimedelta(self):  # {{{
        periods = {
            "1M": timedelta(minutes=1),
            "5M": timedelta(minutes=5),
            "10M": timedelta(minutes=10),
            "1H": timedelta(hours=1),
            "D": timedelta(days=1),
            "W": timedelta(weeks=1),
            "M": timedelta(days=30),
        }
        return periods[self.value]

    # }}}
    @classmethod  # save# {{{
    def save(cls, data_type, file_path):
        string = data_type.value
        Cmd.write(string, file_path)

    # }}}
    @classmethod  # load# {{{
    def load(cls, file_path):
        string = Cmd.read(file_path).strip()
        data_type = DataType.fromStr(string)
        return data_type

    # }}}
    @classmethod  # fromStr#{{{
    def fromStr(cls, string_type: str):
        types = {
            "1M": DataType.BAR_1M,
            "5M": DataType.BAR_5M,
            "10M": DataType.BAR_10M,
            "1H": DataType.BAR_1H,
            "D": DataType.BAR_D,
            "W": DataType.BAR_W,
            "M": DataType.BAR_M,
            "BAR_1M": DataType.BAR_1M,
            "BAR_5M": DataType.BAR_5M,
            "BAR_10M": DataType.BAR_10M,
            "BAR_1H": DataType.BAR_1H,
            "BAR_D": DataType.BAR_D,
            "BAR_W": DataType.BAR_W,
            "BAR_M": DataType.BAR_M,
            "book": DataType.BOOK,
            "tic": DataType.TIC,
            "analyse": DataType.ANALYSE,
        }
        return types[string_type]

    # }}}


# }}}
