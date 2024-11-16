#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum
import os
from datetime import UTC, time, timedelta


class Dir:  # {{{
    """Program directories"""

    # Specify absolute path to program dir
    ROOT = "/home/alex/AVIN/"

    # All user files by default in the 'ROOT/usr', you can specify
    # an absolute path to another location. All user data be there.
    USR = os.path.join(ROOT, "usr")

    # Default directory for requirements packages, if you want to install
    # the dependencies in a different location, specify it here
    ENV = os.path.join(ROOT, "env")

    # Don't edit other dirs
    LIB = os.path.join(ROOT, "avin")
    GUI = os.path.join(ROOT, "gui")
    DOС = os.path.join(ROOT, "doc")
    LANG = os.path.join(ROOT, "lang")
    LOG = os.path.join(ROOT, "log")
    RES = os.path.join(ROOT, "res")
    TEST = os.path.join(ROOT, "test")
    TMP = os.path.join(ROOT, "tmp")


# }}}
class Res:  # {{{
    """Resource subdirectories"""

    CACHE = os.path.join(Dir.RES, "cache")
    DATA = os.path.join(Dir.RES, "data")
    DOWNLOAD = os.path.join(Dir.RES, "download")
    ICON = os.path.join(Dir.RES, "icon")
    PALETTE = os.path.join(Dir.RES, "palette")
    SOUND = os.path.join(Dir.RES, "sound")
    VOICE = os.path.join(Dir.RES, "voice")
    SPLASH = os.path.join(Dir.RES, "splash.png")
    TEMPLATE = os.path.join(Dir.RES, "template")


# }}}


class WeekDays(enum.Enum):  # {{{
    Mon = 0
    Tue = 1
    Wed = 2
    Thu = 3
    Fri = 4
    Sat = 5
    Sun = 6

    @staticmethod  # isWorkday  # {{{
    def isWorkday(day_number: int):
        return day_number < 5

    # }}}
    @staticmethod  # isHoliday  # {{{
    def isHoliday(day_number):
        return day_number in (5, 6)

    # }}}


# }}}

ONE_SECOND = timedelta(seconds=1)
ONE_MINUTE = timedelta(minutes=1)
FIVE_MINUTE = timedelta(minutes=5)
TEN_MINUTE = timedelta(minutes=10)
ONE_HOUR = timedelta(hours=1)
ONE_DAY = timedelta(days=1)
ONE_WEEK = timedelta(weeks=1)
ONE_MONTH = timedelta(days=30)
ONE_YEAR = timedelta(days=365)
DAY_BEGIN = time(0, 0, tzinfo=UTC)
DAY_END = time(23, 59, tzinfo=UTC)


__all__ = (
    "Dir",
    "Res",
    "WeekDays",
    "UTC",
    "ONE_SECOND",
    "ONE_MINUTE",
    "FIVE_MINUTE",
    "TEN_MINUTE",
    "ONE_HOUR",
    "ONE_DAY",
    "ONE_WEEK",
    "ONE_MONTH",
    "ONE_YEAR",
    "DAY_BEGIN",
    "DAY_END",
)
