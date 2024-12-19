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
    ANALYTIC = os.path.join(Dir.USR, "analytic")
    CONNECT = os.path.join(Dir.USR, "connect")
    DATA = os.path.join(Dir.USR, "data")
    FILTER = os.path.join(Dir.USR, "filter")
    STRATEGY = os.path.join(Dir.USR, "strategy")

    # User notes
    NOTE = os.path.join(Dir.USR, "note.un")

    # Your local timeshift from UTC+0
    # set it if you want see time with offset-aware
    # for example for Moscow +3 hours, set 0 if you want see default UTC time
    TIME_DIF = timedelta(hours=3)

    # TODO: move to utils
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

    # Number of stored log files
    LOG_HISTORY = 5

    # Tinkoff token file, by default in dir
    # 'usr/connect/tinkoff/token.txt'
    TINKOFF_TOKEN = os.path.join(CONNECT, "tinkoff", "token.txt")

    # MOEX account file, by default in dir
    # 'usr/connect/moex/account.txt'
    MOEX_ACCOUNT = os.path.join(CONNECT, "moex", "account.txt")

    # Postresql settings
    PG_USER = "alex"
    PG_PASSWORD = ""
    PG_DATABASE = "ars_vincere"
    PG_HOST = "127.0.0.1"


# }}}
class Auto:  # {{{
    # Update assets info every day
    UPDATE_ASSET_CACHE: bool = True

    # Update all availible market data every day
    UPDATE_MARKET_DATA: bool = True

    # Run all convert tasks after update market data
    CONVERT_MARKET_DATA: bool = True


# }}}
class Cfg:  # {{{
    class Chart:  # {{{
        BAR_WIDTH = 8
        BAR_HEIGHT = 10  # px на 1% цены
        BAR_INDENT = 1
        CUNDLE_INDENT = 2
        SHADOW_WIDTH = 1

    # }}}


# }}}


__all__ = ("Usr", "Auto", "Cfg")
