#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from gui.custom.theme import Theme


class Css:
    # Style  # {{{
    STYLE = f"""
        font-family: Hack;
        background-color: {Theme.bg_normal};
        color: {Theme.fg_normal};
        """
    # }}}
    # Dialog  # {{{
    DIALOG = f"""
        font-family: Hack;
        background-color: {Theme.bg_normal};
        color: {Theme.fg_normal};
        """
    # }}}
    # Line edit  # {{{
    LINE_EDIT = f"""
        QLineEdit {{
            font-family: Hack;
            background-color: {Theme.bg_normal};
            selection-background-color: {Theme.hl_hover};
            color: {Theme.fg_high};
            border-color: {Theme.border};
            border-style: solid;
            border-width: 1px;
            border-radius: 2px;
            padding: 4px;
        }}
        """
    # }}}
    # Tool button  # {{{
    TOOL_BUTTON = f"""
        QToolButton {{
            font-family: Hack;
            background-color: {Theme.bg_normal};
            border-width: 0px;
            border-radius: 4px;
        }}
        QToolButton:hover {{
            background-color: {Theme.hl_hover};
        }}
        QToolButton:checked {{
            background-color: {Theme.hl_hover};
        }}
        QToolButton:pressed {{
            background-color: {Theme.hl_cliked};
        }}
        QToolButton:disabled {{
            background-color: {Theme.bg_dim};
            border-color: {Theme.border};
            border-width: 1px;
            border-style: solid;
        }}

        QToolButton[popupMode="1"]  {{ /* only for MenuButtonPopup */
            padding-right: 20px; /* make way for the popup button */
        }}
        /* the subcontrols below are used only in the MenuButtonPopup mode */
        QToolButton::menu-button {{
            border: 2px solid gray;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            /* 16px width + 4px for border = 20px allocated above */
            width: 16px;
        }}
        QToolButton::menu-arrow {{
            image: url(downarrow.png);
        }}
        QToolButton::menu-arrow:open {{
            top: 1px; left: 1px; /* shift it a bit */
        }}

        """
    # }}}
    # Push button  # {{{
    PUSH_BUTTON = f"""
        QPushButton {{
            font-family: Hack;
            background-color: {Theme.bg_normal};
            border-color: {Theme.border};
            border-width: 1px;
            border-style: solid;
            border-radius: 4px;
            margin: 0px 2px;
        }}
        QPushButton:hover {{
            background-color: {Theme.hl_hover};
        }}
        QPushButton:pressed {{
            background-color: {Theme.hl_cliked};
        }}
        QPushButton:disabled {{
            background-color: {Theme.bg_dim};
            color: {Theme.fg_disabled};
            border-color: {Theme.border};
            border-width: 1px;
            border-style: solid;
        }}
        """
    # }}}
    # Menu  # {{{
    MENU = f"""
        QMenu {{
            font-family: Hack;
            background-color: {Theme.bg_mild};
            color: {Theme.fg_normal};
            border-width: 1px;
            border-radius: 4px;
            border-style: solid;
            border-color: {Theme.bg_high};
        }}
        QMenu::item {{
            background-color: transparent;
        }}
        QMenu::item:selected {{
            background-color: {Theme.hl_hover};
        }}
        """
    # }}}
    # FramedLabel{{{
    FRAMED_LABEL = f"""
        font-family: Hack;
        background-color: {Theme.bg_normal};
        color: {Theme.fg_normal};
        border-color: {Theme.border};
        border-style: solid;
        border-width: 1px;
        border-radius: 2px;
        padding: 4px;
    """
    # }}}
    BUY_BUTTON = """# {{{
        QPushButton {
            color: white;
            padding: 1px;
            border-width: 0px;
            border-radius: 3px;
            background-color: #AA98BB6C;
        }
        QPushButton:hover {
            color: white;
            background-color: #CC98BB6C;

        }
        QPushButton:pressed {
            color: white;
            background-color: #98BB6C;
        }
        QPushButton:disabled {
            color: #848388;
            border-width: 1px;
            border-style: solid;
            border-color: #5d5e60;
            background-color: #373737;
        }
        """  # }}}
    SELL_BUTTON = """# {{{
        QPushButton {
        color: white;
        padding: 1px;
        border-width: 0px;
        border-radius: 3px;
        background-color: #AAFF5D62;
        }
        QPushButton:hover {
        color: white;
        background-color: #CCFF5D62;
        }
        QPushButton:pressed {
        color: white;
        background-color: #FF5D62
        }
        QPushButton:disabled {
        color: #848388;
        border-style: solid;
        border-width: 1px;
        border-color: #5d5e60;
        background-color: #373737;
        }
        """  # }}}


if __name__ == "__main__":
    ...
