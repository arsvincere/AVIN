#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import os
from datetime import datetime, timedelta

from avin.const import Dir


class Usr:  # {{{
    # User subdirectories
    ANALYSE = os.path.join(Dir.USR, "analyse")
    ANALYTIC = os.path.join(Dir.USR, "analytic")
    CACHE = os.path.join(Dir.USR, "cache")
    CONNECT = os.path.join(Dir.USR, "connect")
    DATA = os.path.join(Dir.USR, "data")
    FILTER = os.path.join(Dir.USR, "filter")
    MARK = os.path.join(Dir.USR, "mark")
    RESEARCH = os.path.join(Dir.USR, "research")
    STRATEGY = os.path.join(Dir.USR, "strategy")

    # User notes
    NOTE = os.path.join(Dir.USR, "note.un")

    # Your local timeshift from UTC+0
    # set it if you want see time with offset-aware
    # for example for Moscow +3 hours, set 0 if you want see default UTC time
    TIME_DIF = timedelta(hours=3)

    @classmethod  # localTime
    def localTime(cls, dt: datetime) -> str:
        return (dt + Usr.TIME_DIF).strftime("%Y-%m-%d %H:%M")

    # Your applications
    TERMINAL = "alacritty"
    OPT = ["-T", "AlacrittyFloat"]
    EDITOR = "nvim"
    PYTHON = "python3"

    # exec flag for your terminal: -e for alacritty, -x for xfce4-terminal...
    # example: 'alacritty -e nvim', 'xfce4-terminal -x nvim'
    # it is use for run subprocesses
    EXEC = "-e"

    # Log
    LOG_HISTORY = 5  # days
    LOG_DEBUG = True
    LOG_INFO = True

    # Tinkoff token file, by default in dir
    # 'usr/connect/tinkoff/token.txt'
    TINKOFF_TOKEN = os.path.join(CONNECT, "tinkoff", "token.txt")

    # MOEX account file, by default in dir
    # 'usr/connect/moex/account.txt'
    MOEX_ACCOUNT = os.path.join(CONNECT, "moex", "account.txt")

    # PostresQL settings
    PG_USER = "alex"
    PG_PASSWORD = ""
    PG_DATABASE = "ars_vincere"
    PG_HOST = "127.0.0.1"


# }}}
class Auto:  # {{{
    # Update assets info
    UPDATE_ASSET_CACHE: bool = True

    # Update market data
    UPDATE_MARKET_DATA: bool = True

    # Run convert tasks after update market data
    CONVERT_MARKET_DATA: bool = True

    # Update user analytics
    UPDATE_ANALYTIC: bool = True
    UPDATE_ANALYTIC_PERIOD: timedelta = timedelta(days=30)

    # Postgres backup
    BACKUP_PATH: str = Usr.DATA
    BACKUP_MARKET_DATA: bool = True
    BACKUP_USER_DB: bool = True
    BACKUP_DATA_HISTORY: int = 2  # files
    BACKUP_PUBLIC_HISTORY: int = 10  # files


# }}}
class Cfg:  # {{{
    class Chart:  # {{{
        SHADOW_WIDTH = 1

        BAR_WIDTH = 8  # px
        BAR_HEIGHT_D = 10  # px на 1% цены
        BAR_HEIGHT_1H = 30  # px на 1% цены
        BAR_HEIGHT_5M = 60  # px на 1% цены
        BAR_HEIGHT_1M = 90  # px на 1% цены
        BAR_INDENT = 1  # px
        CUNDLE_INDENT = 2  # px

        ZOOM_BAR_WIDTH = 4  # px
        ZOOM_BAR_HEIGHT = 30  # px на 1% цены
        ZOOM_BAR_INDENT = 1  # px
        ZOOM_CUNDLE_INDENT = 2  # px

        VOL_WIDTH = BAR_WIDTH
        VOL_HEIGHT = 200  # px
        VOL_INDENT = 3  # px

    # }}}
    class ShapeSize:  # {{{
        VERY_SMALL = 4  # px
        SMALL = 6
        NORMAL = 8
        BIG = 12
        VERY_BIG = 16

    # }}}


# }}}


__all__ = ("Usr", "Auto", "Cfg")
