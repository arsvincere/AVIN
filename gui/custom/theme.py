#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from gui.custom.color import Color


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


if __name__ == "__main__":
    ...
