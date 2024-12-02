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
    ANALYTIC = QtGui.QIcon(Cmd.path(Res.ICON, "left", "analytic.svg"))
    CONFIG = QtGui.QIcon(Cmd.path(Res.ICON, "left", "config.svg"))
    CONSOLE = QtGui.QIcon(Cmd.path(Res.ICON, "left", "console.svg"))
    DATA = QtGui.QIcon(Cmd.path(Res.ICON, "left", "data.svg"))
    FILTER = QtGui.QIcon(Cmd.path(Res.ICON, "left", "filter.svg"))
    LIST = QtGui.QIcon(Cmd.path(Res.ICON, "left", "list.svg"))
    NOTE = QtGui.QIcon(Cmd.path(Res.ICON, "left", "note.svg"))
    SHUTDOWN = QtGui.QIcon(Cmd.path(Res.ICON, "left", "shutdown.svg"))
    STRATEGY = QtGui.QIcon(Cmd.path(Res.ICON, "left", "strategy.svg"))
    SUMMARY = QtGui.QIcon(Cmd.path(Res.ICON, "left", "summary.svg"))
    TESTER = QtGui.QIcon(Cmd.path(Res.ICON, "left", "tester.svg"))

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
    ADD = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "add.svg"))
    CANCEL = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "cancel.svg"))
    CLOSE = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "close.svg"))
    CONVERT = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "convert.svg"))
    DELETE = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "delete.svg"))
    DOWN = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "down.svg"))
    DOWNLOAD = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "download.svg"))
    EDIT = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "edit.svg"))
    EXTRACT = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "extract.svg"))
    LEFT = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "left.svg"))
    LIST = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "list.svg"))
    NO = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "no.svg"))
    OK = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "ok.svg"))
    OTHER = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "other.svg"))
    PAUSE = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "pause.svg"))
    REFRASH = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "refrash.svg"))
    REMOVE = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "remove.svg"))
    RENAME = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "rename.svg"))
    RIGHT = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "right.svg"))
    RUN = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "run.svg"))
    SAVE = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "save.svg"))
    SEARCH = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "search.svg"))
    STOP = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "stop.svg"))
    UP = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "up.svg"))
    UPDATE = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "update.svg"))
    UPLOAD = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "upload.svg"))
    YES = QtGui.QIcon(Cmd.path(Res.ICON, "btn", "yes.svg"))


if __name__ == "__main__":
    ...
