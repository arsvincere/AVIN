#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import os
from datetime import timedelta

from avin.const import Dir


class Usr:  # {{{
    # User subdirectories
    ANALYTIC = os.path.join(Dir.USR, "analytic")
    ASSET = os.path.join(Dir.USR, "asset")
    CONDITION = os.path.join(Dir.USR, "broker")
    CONNECT = os.path.join(Dir.USR, "connect")
    FILTER = os.path.join(Dir.USR, "filter")
    GENERAL = os.path.join(Dir.USR, "general")
    MARKER = os.path.join(Dir.USR, "marker")
    SANDBOX = os.path.join(Dir.USR, "sandbox")
    SETTINGS = os.path.join(Dir.USR, "settings")
    STRATEGY = os.path.join(Dir.USR, "strategy")
    TEST = os.path.join(Dir.USR, "test")

    # Your local timeshift from UTC+0
    # set it if you want see time with offset-aware
    # for example for Moscow +3 hours, set 0 if you want see default UTC time
    TIME_DIF = timedelta(hours=3)

    # Your applications
    TERMINAL = "alacritty"
    EDITOR = "nvim"
    PYTHON = "python3"

    # exec flag for your terminal: -e for alacritty, -x for xfce4-terminal...
    # example: 'alacritty -e nvim', 'xfce4-terminal -x nvim'
    # it is use for run subprocesses
    EXEC = "-e"

    # Number of stored log files
    LOG_HISTORY = 5

    # Tinkoff token file, by default in dir
    # 'ROOT/usr/connect/tinkoff/token.txt'
    TINKOFF_TOKEN = os.path.join(CONNECT, "tinkoff", "token.txt")

    # MOEX account file, by default in dir
    # 'ROOT/usr/connect/moex/account.txt'
    MOEX_ACCOUNT = os.path.join(CONNECT, "moex", "account.txt")

    # Auto update
    AUTO_UPDATE_ASSET_CACHE = True
    AUTO_UPDATE_MARKET_DATA = True

    # Postresql settings
    PG_USER = "alex"
    PG_PASSWORD = ""
    PG_DATABASE = "appdb"
    PG_HOST = "127.0.0.1"


# }}}


__all__ = ("Usr",)
