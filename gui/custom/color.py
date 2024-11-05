#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets


class Color:
    # Polar Night.
    nord0 = "#2E3440"
    nord1 = "#3B4252"
    nord2 = "#434C5E"
    nord3 = "#4C566A"

    # Snow storm.
    nord4 = "#D8DEE9"
    nord5 = "#E5E9F0"
    nord6 = "#ECEFF4"

    # Frost.
    nord7 = "#8FBCBB"
    nord8 = "#88C0D0"
    nord9 = "#81A1C1"
    nord10 = "#5E81AC"

    # Aurora.
    nord11 = "#BF616A"
    nord12 = "#D08770"
    nord13 = "#EBCB8B"
    nord14 = "#A3BE8C"
    nord15 = "#B48EAD"

    # Black
    black1 = "#000000"
    black2 = "#040404"
    black3 = "#080808"

    # Gray
    gray1 = "#0F0F0F"
    gray2 = "#373737"
    gray3 = "#5D5E60"
    gray4 = "#848388"
    gray5 = "#B7B7AF"

    # White
    white1 = "#AAAAAA"
    white2 = "#BBBBBB"
    white3 = "#CCCCCC"
    white4 = "#DDDDDD"
    white5 = "#EEEEEE"
    white6 = "#FFFFFF"

    # Bg Shades
    sumiInk0 = "#16161D"
    sumiInk1 = "#181820"
    sumiInk2 = "#1a1a22"
    sumiInk3 = "#1F1F28"
    sumiInk4 = "#2A2A37"
    sumiInk5 = "#363646"
    sumiInk6 = "#54546D"  # fg

    # Popup and Floats
    waveBlue1 = "#223249"
    waveBlue2 = "#2D4F67"

    # Diff and Git
    winterGreen = "#2B3328"
    winterYellow = "#49443C"
    winterRed = "#43242B"
    winterBlue = "#252535"
    autumnGreen = "#76946A"
    autumnRed = "#C34043"
    autumnYellow = "#DCA561"

    # Diag
    samuraiRed = "#E82424"
    roninYellow = "#FF9E3B"
    waveAqua1 = "#6A9589"
    dragonBlue = "#658594"

    # Fg and Comments
    oldWhite = "#C8C093"
    fujiWhite = "#DCD7BA"
    fujiGray = "#727169"

    oniViolet = "#957FB8"
    oniViolet2 = "#b8b4d0"
    crystalBlue = "#7E9CD8"
    springViolet1 = "#938AA9"
    springViolet2 = "#9CABCA"
    springBlue = "#7FB4CA"
    lightBlue = "#A3D4D5"  # unused yet
    waveAqua2 = "#7AA89F"  # improve lightness: desaturated greenish Aqua

    # waveAqua2  = "#68AD99",
    # waveAqua4  = "#7AA880",
    # waveAqua5  = "#6CAF95",
    # waveAqua3  = "#68AD99",

    springGreen = "#98BB6C"
    boatYellow1 = "#938056"
    boatYellow2 = "#C0A36E"
    carpYellow = "#E6C384"

    sakuraPink = "#D27E99"
    waveRed = "#E46876"
    peachRed = "#FF5D62"
    surimiOrange = "#FFA066"
    katanaGray = "#717C7C"

    dragonBlack0 = "#0d0c0c"
    dragonBlack1 = "#12120f"
    dragonBlack2 = "#1D1C19"
    dragonBlack3 = "#181616"
    dragonBlack4 = "#282727"
    dragonBlack5 = "#393836"
    dragonBlack6 = "#625e5a"

    dragonWhite = "#c5c9c5"
    dragonGreen = "#87a987"
    dragonGreen2 = "#8a9a7b"
    dragonPink = "#a292a3"
    dragonOrange = "#b6927b"
    dragonOrange2 = "#b98d7b"
    dragonGray = "#a6a69c"
    dragonGray2 = "#9e9b93"
    dragonGray3 = "#7a8382"
    dragonBlue2 = "#8ba4b0"
    dragonViolet = "#8992a7"
    dragonRed = "#c4746e"
    dragonAqua = "#8ea4a2"
    dragonAsh = "#737c73"
    dragonTeal = "#949fb5"
    dragonYellow = "#c4b28a"  # a99c8b",
    # "#8a9aa3",

    lotusInk1 = "#545464"
    lotusInk2 = "#43436c"
    lotusGray = "#dcd7ba"
    lotusGray2 = "#716e61"
    lotusGray3 = "#8a8980"
    lotusWhite0 = "#d5cea3"
    lotusWhite1 = "#dcd5ac"
    lotusWhite2 = "#e5ddb0"
    lotusWhite3 = "#f2ecbc"
    lotusWhite4 = "#e7dba0"
    lotusWhite5 = "#e4d794"
    lotusViolet1 = "#a09cac"
    lotusViolet2 = "#766b90"
    lotusViolet3 = "#c9cbd1"
    lotusViolet4 = "#624c83"
    lotusBlue1 = "#c7d7e0"
    lotusBlue2 = "#b5cbd2"
    lotusBlue3 = "#9fb5c9"
    lotusBlue4 = "#4d699b"
    lotusBlue5 = "#5d57a3"
    lotusGreen = "#6f894e"
    lotusGreen2 = "#6e915f"
    lotusGreen3 = "#b7d0ae"
    lotusPink = "#b35b79"
    lotusOrange = "#cc6d00"
    lotusOrange2 = "#e98a00"
    lotusYellow = "#77713f"
    lotusYellow2 = "#836f4a"
    lotusYellow3 = "#de9800"
    lotusYellow4 = "#f9d791"
    lotusRed = "#c84053"
    lotusRed2 = "#d7474b"
    lotusRed3 = "#e82424"
    lotusRed4 = "#d9a594"
    lotusAqua = "#597b75"
    lotusAqua2 = "#5e857a"
    lotusTeal1 = "#4e8ca2"
    lotusTeal2 = "#6693bf"
    lotusTeal3 = "#5a7785"
    lotusCyan = "#d7e3d8"


class OldQtColor:
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
    # Bar
    BG = QtGui.QColor("#181616")  # nvim background
    BULL = QtGui.QColor("#98BB6C")  # kanagawa 4.2
    BEAR = QtGui.QColor("#FF5D62")  # kanagawa 5.3
    UNDEFINE = QtGui.QColor("#FFFFFF")
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
    # Mark
    MARK = QtGui.QColor("#0000AA")
    # Extremum
    SHORTTERM = QtGui.QColor("#FFFFFF")
    MIDTERM = QtGui.QColor("#AAAA00")
    LONGTERM = QtGui.QColor("#AA0000")
    INSIDE_BG = QtGui.QColor("#AA000000")
    OUTSIDE_BG = QtGui.QColor("#44FFFFFF")
    # Button
    BUY = QtGui.QColor("#98BB6C")  # kanagawa 4.2
    SELL = QtGui.QColor("#FF5D62")  # kanagawa 5.3


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = UOrderType()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.showMaximized()
    w.show()
    sys.exit(app.exec())
