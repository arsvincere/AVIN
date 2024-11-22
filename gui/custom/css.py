#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from gui.custom.theme import Theme


class Css:
    # STYLE  # {{{
    STYLE = f"""
        font-family: Monospace;
        background-color: {Theme.bg_normal};
        color: {Theme.fg_normal};
        """
    # }}}
    # DIALOG  # {{{
    DIALOG = f"""
        font-family: Monospace;
        background-color: {Theme.bg_normal};
        color: {Theme.fg_normal};
        """
    # }}}
    # LINE_EDIT  # {{{
    LINE_EDIT = f"""
        QLineEdit {{
            font-family: Monospace;
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
    # TOOL_BAR  # {{{
    TOOL_BAR = f"""
        font-family: Monospace;
        background-color: {Theme.bg_normal};
        color: {Theme.fg_normal};

        border-color: transparent;
        border-width: 2px;
        border-style: solid;

        """
    # }}}
    # TOOL_BUTTON  # {{{
    TOOL_BUTTON = f"""
        QToolButton {{
            font-family: Monospace;
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
            background-color: {Theme.hl_hover};
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
    # PUSH_BUTTON  # {{{
    PUSH_BUTTON = f"""
        QPushButton {{
            font-family: Monospace;
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
    # MENU  # {{{
    MENU = f"""
        QMenu {{
            font-family: Monospace;
            font-size: 12px;
            background-color: {Theme.bg_mild};
            background-color: {Theme.bg_normal};
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
        QMenu::item:disabled {{
            background-color: transparent;
            color: {Theme.fg_disabled};
        }}
        // QMenu::separator {{
        //     height: 20px;
        //     background: lightblue;
        //     margin-left: 10px;
        //     margin-right: 5px;
        // }}
        // QMenu::indicator {{
        //     background: red;
        //     width: 13px;
        //     height: 13px;
        // }}
    """
    # }}}
    # MENU_SECTION  # {{{
    MENU_SECTION = f"""
        font-family: Source Code Pro;
        font-size: 12px;
        background-color: {Theme.bg_normal};
        color: {Theme.border};
        padding-left: 5px;
        padding-top: 4px;
        padding-bottom: 1px;
    """
    # }}}
    # LABEL  # {{{
    LABEL = f"""
        font-family: Sans;
        background-color: {Theme.bg_normal};
        color: {Theme.fg_normal};
    """
    # }}}
    # FRAMED_LABEL  # {{{
    FRAMED_LABEL = f"""
        font-family: Sans;
        background-color: {Theme.bg_normal};
        color: {Theme.fg_normal};
        border-color: {Theme.border};
        border-style: solid;
        border-width: 1px;
        border-radius: 2px;
        padding: 4px;
    """
    # }}}
    # TITLE   # {{{
    TITLE = f"""
        font-family: Sans;
        font-weight: 700;
        background-color: {Theme.bg_normal};
        color: {Theme.fg_normal};
        font-size: 14px;
    """
    # }}}
    # SUB_TITLE   # {{{
    SUB_TITLE = f"""
        font-family: Sans;
        background-color: {Theme.bg_normal};
        color: {Theme.fg_high};
        font-size: 14px;
    """
    # }}}
    # TREE # {{{
    TREE = f"""
        QTreeWidget {{
            background-color: {Theme.bg_normal};
        }}
        QTreeWidget::item {{
            font-family: Monospace;
            background-color: {Theme.bg_normal};
            color: {Theme.fg_normal};
            padding: 5px;
        }}
        QTreeWidget::item:hover {{
            background-color: {Theme.hl_hover};
        }}
        QTreeWidget::item:selected {{
            border-top: 1px solid {Theme.hl_active};
            border-bottom: 1px solid {Theme.hl_active};
        }}

    """
    # }}}
    # TREE_HEADER # {{{
    TREE_HEADER = f"""
        QHeaderView::section {{
            font-family: Monospace;
            background-color: {Theme.bg_normal};
            color: {Theme.border};
            border: 1px solid {Theme.border};
            margin: 0px 1px;
            padding: 1px 5px;
        }}
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
