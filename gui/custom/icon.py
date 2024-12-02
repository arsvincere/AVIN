#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtGui

from avin.const import Res
from avin.utils import Cmd


class Icon:
    # Files
    DIR = QtGui.QIcon(Cmd.path(Res.ICON, "file", "dir.svg"))
    FILE = QtGui.QIcon(Cmd.path(Res.ICON, "file", "file.svg"))

    # Left panel
    DATA = QtGui.QIcon(Cmd.path(Res.ICON, "left", "data.svg"))
    LIST = QtGui.QIcon(Cmd.path(Res.ICON, "left", "list.svg"))
    FILTER = QtGui.QIcon(Cmd.path(Res.ICON, "left", "filter.svg"))
    ANALYTIC = QtGui.QIcon(Cmd.path(Res.ICON, "left", "analytic.svg"))
    NOTE = QtGui.QIcon(Cmd.path(Res.ICON, "left", "note.svg"))
    STRATEGY = QtGui.QIcon(Cmd.path(Res.ICON, "left", "strategy.svg"))
    TESTER = QtGui.QIcon(Cmd.path(Res.ICON, "left", "tester.svg"))
    SUMMARY = QtGui.QIcon(Cmd.path(Res.ICON, "left", "summary.svg"))
    CONSOLE = QtGui.QIcon(Cmd.path(Res.ICON, "left", "console.svg"))
    CONFIG = QtGui.QIcon(Cmd.path(Res.ICON, "left", "config.svg"))
    SHUTDOWN = QtGui.QIcon(Cmd.path(Res.ICON, "left", "shutdown.svg"))

    # Right panel
    BROKER = QtGui.QIcon(Cmd.path(Res.ICON, "right", "broker.svg"))
    CHART = QtGui.QIcon(Cmd.path(Res.ICON, "right", "chart.svg"))
    BOOK = QtGui.QIcon(Cmd.path(Res.ICON, "right", "book.svg"))
    TIC = QtGui.QIcon(Cmd.path(Res.ICON, "right", "tic.svg"))
    ORDER = QtGui.QIcon(Cmd.path(Res.ICON, "right", "order.svg"))
    ACCOUNT = QtGui.QIcon(Cmd.path(Res.ICON, "right", "account.svg"))
    TRADER = QtGui.QIcon(Cmd.path(Res.ICON, "right", "trader.svg"))
    REPORT = QtGui.QIcon(Cmd.path(Res.ICON, "right", "report.svg"))
    INFORMER = QtGui.QIcon(Cmd.path(Res.ICON, "right", "informer.svg"))

    # Buttons
    ADD = QtGui.QIcon(Cmd.path(Res.ICON, "add.svg"))
    CANCEL = QtGui.QIcon(Cmd.path(Res.ICON, "cancel.svg"))
    CLEAR = QtGui.QIcon(Cmd.path(Res.ICON, "clear.svg"))
    CLOSE = QtGui.QIcon(Cmd.path(Res.ICON, "close.svg"))
    CONVERT = QtGui.QIcon(Cmd.path(Res.ICON, "convert.svg"))
    COPY = QtGui.QIcon(Cmd.path(Res.ICON, "copy.svg"))
    DELETE = QtGui.QIcon(Cmd.path(Res.ICON, "delete.svg"))
    DOWNLOAD = QtGui.QIcon(Cmd.path(Res.ICON, "download.svg"))
    EDIT = QtGui.QIcon(Cmd.path(Res.ICON, "edit.svg"))
    EXTRACT = QtGui.QIcon(Cmd.path(Res.ICON, "extract.svg"))
    HELP = QtGui.QIcon(Cmd.path(Res.ICON, "help.svg"))
    HIDE = QtGui.QIcon(Cmd.path(Res.ICON, "hide.svg"))
    NEW = QtGui.QIcon(Cmd.path(Res.ICON, "new.svg"))
    NO = QtGui.QIcon(Cmd.path(Res.ICON, "no.svg"))
    OK = QtGui.QIcon(Cmd.path(Res.ICON, "ok.svg"))
    OTHER = QtGui.QIcon(Cmd.path(Res.ICON, "other.svg"))
    REMOVE = QtGui.QIcon(Cmd.path(Res.ICON, "remove.svg"))
    RENAME = QtGui.QIcon(Cmd.path(Res.ICON, "rename.svg"))
    SAVE = QtGui.QIcon(Cmd.path(Res.ICON, "save.svg"))
    SEARCH = QtGui.QIcon(Cmd.path(Res.ICON, "search.svg"))
    SECTION = QtGui.QIcon(Cmd.path(Res.ICON, "section.svg"))
    SETTINGS = QtGui.QIcon(Cmd.path(Res.ICON, "settings.svg"))
    THRASH = QtGui.QIcon(Cmd.path(Res.ICON, "thrash.svg"))
    UPDATE = QtGui.QIcon(Cmd.path(Res.ICON, "update.svg"))
    YES = QtGui.QIcon(Cmd.path(Res.ICON, "yes.svg"))


if __name__ == "__main__":
    ...
