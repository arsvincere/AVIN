#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import logging
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from avin.utils import Cmd
from avin.const import ICON_DIR
logger = logging.getLogger("LOGGER")

class GuiError(Exception): pass
class Logo(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        logo = QtGui.QPixmap()
        logo.load("/home/alex/yandex/src/moex.data/res/logo.png")
        logo = logo.scaledToWidth(32)
        self.setPixmap(logo)


class Color():
    # common color
    NONE =              QtGui.QColor("#00000000")
    BLACK =             QtGui.QColor("#000000")
    WHITE =             QtGui.QColor("#FFFFFF")
    RED =               QtGui.QColor("#AA0000")
    GREEN =             QtGui.QColor("#00AA00")
    GREEN =             QtGui.QColor("#0000AA")
    YELLOW =            QtGui.QColor("#AAAA00")
    # Window palette
    DARK =              QtGui.QColor("#0F0F0F")  #5
    NORMAL =            QtGui.QColor("#323232")
    INACTIVE =          QtGui.QColor("#373737")  #4
    HIGHLIGHT =         QtGui.QColor("#5D5E60")  #3
    DISABLED_TEXT =     QtGui.QColor("#848388")  #2
    TEXT =              QtGui.QColor("#B7B7AF")  #1
    BUTTON_TEXT =       QtGui.QColor("#CCCCCC")
    WINDOW_TEXT =       QtGui.QColor("#EEEEEE")
    HIGHLIGHT_TEXT =    QtGui.QColor("#FAFAFA")
    # Bar
    BG =                QtGui.QColor("#181616")  # nvim background
    BULL =              QtGui.QColor("#98BB6C")  # kanagawa 4.2
    BEAR =              QtGui.QColor("#FF5D62")  # kanagawa 5.3
    UNDEFINE =          QtGui.QColor("#FFFFFF")
    # Black & white bar
    # BG =                QtGui.QColor("#242424")
    # BULL =              QtGui.QColor("#BBBBBB")
    # BEAR =              QtGui.QColor("#646464")
    # UNDEFINE =          QtGui.QColor("#000000")
    ZOOM_BULL =         QtGui.QColor("#00FF00")
    ZOOM_BEAR =         QtGui.QColor("#FF0000")
    # Trade
    STOP =              QtGui.QColor("#FF0000")
    TAKE =              QtGui.QColor("#00FF00")
    OPEN =              QtGui.QColor("#AAAAAA")
    TRADE_WIN =         QtGui.QColor("#00AA00")
    TRADE_LOSS =        QtGui.QColor("#AA0000")
    # Mark
    MARK =              QtGui.QColor("#0000AA")
    # Extremum
    SHORTTERM =         QtGui.QColor("#FFFFFF")
    MIDTERM =           QtGui.QColor("#AAAA00")
    LONGTERM =          QtGui.QColor("#AA0000")
    INSIDE_BG =         QtGui.QColor("#AA000000")
    OUTSIDE_BG =        QtGui.QColor("#44FFFFFF")
    # Button
    BUY =               QtGui.QColor("#98BB6C")  # kanagawa 4.2
    SELL =              QtGui.QColor("#FF5D62")  # kanagawa 5.3

class Font():
    MONO = QtGui.QFont("monospace")
    SANS = QtGui.QFont("sans")

class Icon():
    # Files
    DIR =       QtGui.QIcon(Cmd.join(ICON_DIR, "dir.svg"))
    FILE =      QtGui.QIcon(Cmd.join(ICON_DIR, "file.svg"))
    ARCHIVE =   QtGui.QIcon(Cmd.join(ICON_DIR, "archive.svg"))
    ASSET =     QtGui.QIcon(Cmd.join(ICON_DIR, "asset.svg"))
    BIN =       QtGui.QIcon(Cmd.join(ICON_DIR, "bin.svg"))
    CSV =       QtGui.QIcon(Cmd.join(ICON_DIR, "csv.svg"))
    JSON =      QtGui.QIcon(Cmd.join(ICON_DIR, "json.svg"))
    MARKDOWN =  QtGui.QIcon(Cmd.join(ICON_DIR, "markdown.svg"))
    SCRIPT =    QtGui.QIcon(Cmd.join(ICON_DIR, "script.svg"))
    TXT =       QtGui.QIcon(Cmd.join(ICON_DIR, "text.svg"))
    TIMEFRAME = QtGui.QIcon(Cmd.join(ICON_DIR, "timeframe.svg"))
    # Left panel
    DATA =      QtGui.QIcon(Cmd.join(ICON_DIR, "data.svg"))
    LIST =      QtGui.QIcon(Cmd.join(ICON_DIR, "list.svg"))
    CHART =     QtGui.QIcon(Cmd.join(ICON_DIR, "chart.svg"))
    STRATEGY =  QtGui.QIcon(Cmd.join(ICON_DIR, "strategy.svg"))
    TEST =      QtGui.QIcon(Cmd.join(ICON_DIR, "test.svg"))
    REPORT =    QtGui.QIcon(Cmd.join(ICON_DIR, "report.svg"))
    CONSOLE =   QtGui.QIcon(Cmd.join(ICON_DIR, "console.svg"))
    SHUTDOWN =  QtGui.QIcon(Cmd.join(ICON_DIR, "shutdown.svg"))
    # Right panel
    BABLO =     QtGui.QIcon(Cmd.join(ICON_DIR, "BABLO.svg"))
    BROKER =    QtGui.QIcon(Cmd.join(ICON_DIR, "broker.svg"))
    ACCOUNT =   QtGui.QIcon(Cmd.join(ICON_DIR, "account.svg"))
    ORDER =     QtGui.QIcon(Cmd.join(ICON_DIR, "order.svg"))
    ANALYTIC =  QtGui.QIcon(Cmd.join(ICON_DIR, "analytic.svg"))
    SANDBOX =   QtGui.QIcon(Cmd.join(ICON_DIR, "sandbox.svg"))
    GENERAL =   QtGui.QIcon(Cmd.join(ICON_DIR, "general.svg"))
    KEEPER =    QtGui.QIcon(Cmd.join(ICON_DIR, "keeper.svg"))
    # Buttons
    ADD =       QtGui.QIcon(Cmd.join(ICON_DIR, "add.svg"))
    APPLY =     QtGui.QIcon(Cmd.join(ICON_DIR, "apply.svg"))
    CANCEL =    QtGui.QIcon(Cmd.join(ICON_DIR, "cancel.svg"))
    CLEAR =     QtGui.QIcon(Cmd.join(ICON_DIR, "clear.svg"))
    CLOSE =     QtGui.QIcon(Cmd.join(ICON_DIR, "close.svg"))
    CONFIG =    QtGui.QIcon(Cmd.join(ICON_DIR, "config.svg"))
    CONVERT =   QtGui.QIcon(Cmd.join(ICON_DIR, "convert.svg"))
    COPY =      QtGui.QIcon(Cmd.join(ICON_DIR, "copy.svg"))
    DELETE =    QtGui.QIcon(Cmd.join(ICON_DIR, "delete.svg"))
    DOWNLOAD =  QtGui.QIcon(Cmd.join(ICON_DIR, "download.svg"))
    EDIT =      QtGui.QIcon(Cmd.join(ICON_DIR, "edit.svg"))
    EXTRACT =   QtGui.QIcon(Cmd.join(ICON_DIR, "extract.svg"))
    HELP =      QtGui.QIcon(Cmd.join(ICON_DIR, "help.svg"))
    HIDE =      QtGui.QIcon(Cmd.join(ICON_DIR, "hide.svg"))
    NEW =       QtGui.QIcon(Cmd.join(ICON_DIR, "new.svg"))
    NO =        QtGui.QIcon(Cmd.join(ICON_DIR, "no.svg"))
    OK =        QtGui.QIcon(Cmd.join(ICON_DIR, "ok.svg"))
    OTHER =     QtGui.QIcon(Cmd.join(ICON_DIR, "other.svg"))
    REMOVE =    QtGui.QIcon(Cmd.join(ICON_DIR, "remove.svg"))
    RENAME =    QtGui.QIcon(Cmd.join(ICON_DIR, "rename.svg"))
    SAVE =      QtGui.QIcon(Cmd.join(ICON_DIR, "save.svg"))
    SEARCH =    QtGui.QIcon(Cmd.join(ICON_DIR, "search.svg"))
    SECTION =   QtGui.QIcon(Cmd.join(ICON_DIR, "section.svg"))
    SETTINGS =  QtGui.QIcon(Cmd.join(ICON_DIR, "settings.svg"))
    THRASH =    QtGui.QIcon(Cmd.join(ICON_DIR, "thrash.svg"))
    UPDATE =    QtGui.QIcon(Cmd.join(ICON_DIR, "update.svg"))
    YES =       QtGui.QIcon(Cmd.join(ICON_DIR, "yes.svg"))

class Palette(QtGui.QPalette):
    def __init__(self):
        QtGui.QPalette.__init__(self)
        g = QtGui.QPalette.ColorGroup
        r = QtGui.QPalette.ColorRole
        c = Color
        self.setColor(g.Normal,    r.Window,           c.NORMAL)
        self.setColor(g.Inactive,  r.Window,           c.INACTIVE)
        self.setColor(g.Disabled,  r.Window,           c.INACTIVE)

        self.setColor(g.Normal,    r.Base,             c.NORMAL)
        self.setColor(g.Inactive,  r.Base,             c.INACTIVE)
        self.setColor(g.Disabled,  r.Base,             c.INACTIVE)

        self.setColor(g.Normal,    r.Button,           c.NORMAL)
        self.setColor(g.Inactive,  r.Button,           c.INACTIVE)
        self.setColor(g.Disabled,  r.Button,           c.NORMAL)
        self.setColor(g.Normal,    r.Highlight,        c.HIGHLIGHT)
        self.setColor(g.Inactive,  r.Highlight,        c.HIGHLIGHT)
        self.setColor(g.Normal,    r.HighlightedText,  c.HIGHLIGHT_TEXT)
        self.setColor(g.Inactive,  r.HighlightedText,  c.HIGHLIGHT_TEXT)
        self.setColor(g.Normal,    r.WindowText,       c.WINDOW_TEXT)
        self.setColor(g.Inactive,  r.WindowText,       c.WINDOW_TEXT)
        self.setColor(g.Disabled,  r.WindowText,       c.DISABLED_TEXT)
        self.setColor(g.Normal,    r.ButtonText,       c.BUTTON_TEXT)
        self.setColor(g.Inactive,  r.ButtonText,       c.BUTTON_TEXT)
        self.setColor(g.Disabled,  r.ButtonText,       c.DISABLED_TEXT)
        self.setColor(g.Normal,    r.Text,             c.TEXT)
        self.setColor(g.Inactive,  r.Text,             c.TEXT)
        self.setColor(g.Disabled,  r.Text,             c.DISABLED_TEXT)

class Spacer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
            )


class HLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)


class VLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)


class ProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent=None):
        QtWidgets.QProgressBar.__init__(self, parent)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setMaximumHeight(20)
        self.setFont(Font.MONO)


class ToolButton(QtWidgets.QToolButton):
    """ Const """
    HEIGHT = 32
    WIDTH =  32
    SIZE =   QtCore.QSize(WIDTH, HEIGHT)

    def __init__(self, icon, parent=None):
        QtWidgets.QToolButton.__init__(self, parent)
        self.setIcon(icon)
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setIconSize(self.SIZE)


class SmallButton(QtWidgets.QToolButton):
    """ Const """
    HEIGHT = 16
    WIDTH =  16
    SIZE =   QtCore.QSize(WIDTH, HEIGHT)

    def __init__(self, icon, parent=None):
        QtWidgets.QToolButton.__init__(self, parent)
        self.setIcon(icon)
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setIconSize(self.SIZE)
        self.setContentsMargins(0, 0, 0, 0)


class DialogInfo(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configButton()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.__message_label = QtWidgets.QLabel()
        self.__btn_ok = QtWidgets.QToolButton(self)

    def __createLayots(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__message_label)
        vbox.addWidget(self.__btn_ok)
        self.setLayout(vbox)

    def __configButton(self):
        self.__btn_ok.setFixedSize(32, 32)
        self.__btn_ok.setIcon(Icon.OK)
        self.__btn_ok.setIconSize(QtCore.QSize(32, 32))

    def __config(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.__btn_ok.clicked.connect(self.accept)

    def info(self, message):
        self.__message_label.setText(message)
        self.exec()



class DialogConfirm(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configButton()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.__message_label = QtWidgets.QLabel()
        self.__btn_yes = QtWidgets.QToolButton(self)
        self.__btn_no = QtWidgets.QToolButton(self)

    def __createLayots(self):
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.__btn_yes)
        btn_box.addWidget(self.__btn_no)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__message_label)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    def __configButton(self):
        self.__btn_yes.setFixedSize(32, 32)
        self.__btn_yes.setIcon(Icon.YES)
        self.__btn_yes.setIconSize(QtCore.QSize(32, 32))
        self.__btn_no.setFixedSize(32, 32)
        self.__btn_no.setIcon(Icon.NO)
        self.__btn_no.setIconSize(QtCore.QSize(32, 32))

    def __config(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.__btn_yes.clicked.connect(self.accept)
        self.__btn_no.clicked.connect(self.reject)

    def confirm(self, message):
        self.__message_label.setText(message)
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            return True
        else:
            return False


class DialogName(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configButton()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.__lineedit = QtWidgets.QLineEdit("Enter name")
        self.__btn_yes = QtWidgets.QToolButton(self)
        self.__btn_no = QtWidgets.QToolButton(self)

    def __createLayots(self):
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.__btn_yes)
        btn_box.addWidget(self.__btn_no)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__lineedit)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    def __configButton(self):
        self.__btn_yes.setFixedSize(32, 32)
        self.__btn_yes.setIcon(Icon.YES)
        self.__btn_yes.setIconSize(QtCore.QSize(32, 32))
        self.__btn_no.setFixedSize(32, 32)
        self.__btn_no.setIcon(Icon.NO)
        self.__btn_no.setIconSize(QtCore.QSize(32, 32))

    def __config(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.__btn_yes.clicked.connect(self.accept)
        self.__btn_no.clicked.connect(self.reject)

    def enterName(self, message):
        self.__lineedit.setText(message)
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            name = self.__lineedit.text()
            return name
        else:
            return False

class Dialog(QtWidgets.QDialog):
    @staticmethod  #info
    def info(message):
        dial = DialogInfo()
        dial.info(message)

    @staticmethod  #confirm
    def confirm(message="Ты хорошо подумал?"):
        dial = DialogConfirm()
        result = dial.confirm(message)
        return result

    @staticmethod  #name
    def name(default="Enter name"):
        dial = DialogName()
        name = dial.enterName(default)
        return name




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = UOrderType()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.showMaximized()
    w.show()
    sys.exit(app.exec())

