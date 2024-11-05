#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from PyQt6 import QtGui


class Palette(QtGui.QPalette):
    def __init__(self):
        QtGui.QPalette.__init__(self)
        g = QtGui.QPalette.ColorGroup
        r = QtGui.QPalette.ColorRole
        c = Color
        self.setColor(g.Normal, r.Window, c.NORMAL)
        self.setColor(g.Inactive, r.Window, c.INACTIVE)
        self.setColor(g.Disabled, r.Window, c.INACTIVE)

        self.setColor(g.Normal, r.Base, c.NORMAL)
        self.setColor(g.Inactive, r.Base, c.INACTIVE)
        self.setColor(g.Disabled, r.Base, c.INACTIVE)

        self.setColor(g.Normal, r.Button, c.NORMAL)
        self.setColor(g.Inactive, r.Button, c.INACTIVE)
        self.setColor(g.Disabled, r.Button, c.NORMAL)
        self.setColor(g.Normal, r.Highlight, c.HIGHLIGHT)
        self.setColor(g.Inactive, r.Highlight, c.HIGHLIGHT)
        self.setColor(g.Normal, r.HighlightedText, c.HIGHLIGHT_TEXT)
        self.setColor(g.Inactive, r.HighlightedText, c.HIGHLIGHT_TEXT)
        self.setColor(g.Normal, r.WindowText, c.WINDOW_TEXT)
        self.setColor(g.Inactive, r.WindowText, c.WINDOW_TEXT)
        self.setColor(g.Disabled, r.WindowText, c.DISABLED_TEXT)
        self.setColor(g.Normal, r.ButtonText, c.BUTTON_TEXT)
        self.setColor(g.Inactive, r.ButtonText, c.BUTTON_TEXT)
        self.setColor(g.Disabled, r.ButtonText, c.DISABLED_TEXT)
        self.setColor(g.Normal, r.Text, c.TEXT)
        self.setColor(g.Inactive, r.Text, c.TEXT)
        self.setColor(g.Disabled, r.Text, c.DISABLED_TEXT)


if __name__ == "__main__":
    ...
