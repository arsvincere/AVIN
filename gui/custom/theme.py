#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtGui

from gui.custom.color import Color

# TODO: move to config.py


class Theme:
    # background
    bg_black = Color.black2  # #040404
    bg_dark = Color.dragonBlack0  # #0d0c0c
    bg_dim = Color.dragonBlack1  # #12120f
    bg_normal = Color.dragonBlack3  # #181616
    bg_mild = Color.dragonBlack4  # #282727
    bg_warm = Color.dragonBlack5  # #393836
    bg_high = Color.dragonBlack6  # #625e5a

    # foreground
    fg_disabled = Color.gray4  # #848388
    fg_normal = Color.gray5  # #B7B7AF
    fg_high = Color.white5  # #EEEEEE
    fg_mild = Color.fujiWhite  # #DCD7BA
    fg_old = Color.oldWhite  # #C8C093

    # border
    border = Color.gray3  # #5D5E60

    # highligh
    hl_hover = Color.gray3  # #5D5E60
    hl_cliked = Color.gray4  # #848388
    hl_active = Color.dragonBlue  # #658594

    # bars
    bull = Color.springGreen  # #98BB6C
    bear = Color.peachRed  # #FF5D62

    class Chart:  # {{{
        BG = QtGui.QColor(Color.dragonBlack0)  # #0d0c0c

        BULL = QtGui.QColor("#98BB6C")  # kanagawa 4.2
        BEAR = QtGui.QColor("#FF5D62")  # kanagawa 5.3
        UNDEFINE = QtGui.QColor("#FFFFFF")

        BULL_BEHIND = QtGui.QColor("#2298BB6C")  # kanagawa 4.2
        BEAR_BEHIND = QtGui.QColor("#22FF5D62")  # kanagawa 5.3
        UNDEFINE_BEHIND = QtGui.QColor("#22FFFFFF")

        # Black & white bar
        # BG =                QtGui.QColor("#242424")
        # BULL =              QtGui.QColor("#BBBBBB")
        # BEAR =              QtGui.QColor("#646464")
        # UNDEFINE =          QtGui.QColor("#000000")
        ZOOM_BULL = QtGui.QColor("#00FF00")
        ZOOM_BEAR = QtGui.QColor("#FF0000")
        # Trade
        STOP = QtGui.QColor("#FF0000")
        TAKE = QtGui.QColor("#00FF00")
        OPEN = QtGui.QColor("#AAAAAA")
        TRADE_WIN = QtGui.QColor("#00AA00")
        TRADE_LOSS = QtGui.QColor("#AA0000")
        TRADE_UNDEFINE = QtGui.QColor("#888888")
        # Mark
        MARK = QtGui.QColor("#0000AA")
        # Extremum
        SHORTTERM = QtGui.QColor("#FFFFFF")
        MIDTERM = QtGui.QColor("#AAAA00")
        LONGTERM = QtGui.QColor("#AA0000")
        INSIDE_BG = QtGui.QColor("#AA000000")
        OUTSIDE_BG = QtGui.QColor("#44FFFFFF")

        # TODO: delete it
        # common color
        NONE = QtGui.QColor("#00000000")
        BLACK = QtGui.QColor("#000000")
        WHITE = QtGui.QColor("#FFFFFF")
        RED = QtGui.QColor("#AA0000")
        GREEN = QtGui.QColor("#00AA00")
        GREEN = QtGui.QColor("#0000AA")
        YELLOW = QtGui.QColor("#AAAA00")
        # Window palette
        DARK = QtGui.QColor("#0F0F0F")  # 5
        NORMAL = QtGui.QColor("#323232")
        INACTIVE = QtGui.QColor("#373737")  # 4
        HIGHLIGHT = QtGui.QColor("#5D5E60")  # 3
        DISABLED_TEXT = QtGui.QColor("#848388")  # 2
        TEXT = QtGui.QColor("#B7B7AF")  # 1
        BUTTON_TEXT = QtGui.QColor("#CCCCCC")
        WINDOW_TEXT = QtGui.QColor("#EEEEEE")
        HIGHLIGHT_TEXT = QtGui.QColor("#FAFAFA")
        # Button
        BUY = QtGui.QColor("#98BB6C")  # kanagawa 4.2
        SELL = QtGui.QColor("#FF5D62")  # kanagawa 5.3

    # }}}


if __name__ == "__main__":
    ...
