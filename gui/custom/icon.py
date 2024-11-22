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
    DIR = QtGui.QIcon(Cmd.path(Res.ICON, "dir.svg"))
    FILE = QtGui.QIcon(Cmd.path(Res.ICON, "file.svg"))
    ARCHIVE = QtGui.QIcon(Cmd.path(Res.ICON, "archive.svg"))
    ASSET = QtGui.QIcon(Cmd.path(Res.ICON, "asset.svg"))
    BIN = QtGui.QIcon(Cmd.path(Res.ICON, "bin.svg"))
    CSV = QtGui.QIcon(Cmd.path(Res.ICON, "csv.svg"))
    JSON = QtGui.QIcon(Cmd.path(Res.ICON, "json.svg"))
    MARKDOWN = QtGui.QIcon(Cmd.path(Res.ICON, "markdown.svg"))
    SCRIPT = QtGui.QIcon(Cmd.path(Res.ICON, "script.svg"))
    TXT = QtGui.QIcon(Cmd.path(Res.ICON, "text.svg"))
    TIMEFRAME = QtGui.QIcon(Cmd.path(Res.ICON, "timeframe.svg"))

    # Left panel
    DATA = QtGui.QIcon(Cmd.path(Res.ICON, "data.svg"))
    LIST = QtGui.QIcon(Cmd.path(Res.ICON, "list.svg"))
    CHART = QtGui.QIcon(Cmd.path(Res.ICON, "chart.svg"))
    STRATEGY = QtGui.QIcon(Cmd.path(Res.ICON, "strategy.svg"))
    TEST = QtGui.QIcon(Cmd.path(Res.ICON, "test.svg"))
    SUMMARY = QtGui.QIcon(Cmd.path(Res.ICON, "summary.svg"))
    CONSOLE = QtGui.QIcon(Cmd.path(Res.ICON, "console.svg"))
    SHUTDOWN = QtGui.QIcon(Cmd.path(Res.ICON, "shutdown.svg"))

    # Right panel
    BABLO = QtGui.QIcon(Cmd.path(Res.ICON, "BABLO.svg"))
    BROKER = QtGui.QIcon(Cmd.path(Res.ICON, "broker.svg"))
    ACCOUNT = QtGui.QIcon(Cmd.path(Res.ICON, "account.svg"))
    ORDER = QtGui.QIcon(Cmd.path(Res.ICON, "order.svg"))
    ANALYTIC = QtGui.QIcon(Cmd.path(Res.ICON, "analytic.svg"))
    SANDBOX = QtGui.QIcon(Cmd.path(Res.ICON, "sandbox.svg"))
    GENERAL = QtGui.QIcon(Cmd.path(Res.ICON, "general.svg"))
    KEEPER = QtGui.QIcon(Cmd.path(Res.ICON, "keeper.svg"))

    # Buttons
    ADD = QtGui.QIcon(Cmd.path(Res.ICON, "add.svg"))
    CANCEL = QtGui.QIcon(Cmd.path(Res.ICON, "cancel.svg"))
    CLEAR = QtGui.QIcon(Cmd.path(Res.ICON, "clear.svg"))
    CLOSE = QtGui.QIcon(Cmd.path(Res.ICON, "close.svg"))
    CONFIG = QtGui.QIcon(Cmd.path(Res.ICON, "config.svg"))
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
