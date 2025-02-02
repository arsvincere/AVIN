#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from PyQt6 import QtCore, QtWidgets

from avin.utils import logger
from gui.custom.css import Css
from gui.custom.icon import Icon
from gui.custom.label import Label
from gui.custom.line_edit import LineEdit
from gui.custom.tool_button import ToolButton


class Dialog:
    """Fasade class"""

    @classmethod  # confirm  # {{{
    def confirm(cls, msg: str = "Are you serious?") -> bool:
        logger.debug(f"{cls.__name__}.confirm()")

        dial = _ConfirmDialog()
        result = dial.confirm(msg)
        return result

    # }}}
    @classmethod  # info  # {{{
    def info(cls, msg: str) -> None:
        logger.debug(f"{cls.__name__}.info()")

        dial = _InfoDialog()
        dial.info(msg)
        logger.info(msg)

    # }}}
    @classmethod  # error  # {{{
    def error(cls, msg: str) -> None:
        logger.debug(f"{cls.__name__}.error()")

        dial = _ErrorDialog()
        dial.error(msg)
        logger.error(msg)

    # }}}
    @classmethod  # name  # {{{
    def name(cls, default_name: str = "Enter name") -> str | None:
        logger.debug(f"{cls.__name__}.name()")

        dial = _NameDialog()
        name = dial.enterName(default_name)
        return name

    # }}}


class _ConfirmDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__message_label = Label("", parent=self)
        self.__btn_ok = ToolButton(Icon.OK, parent=self)
        self.__btn_cancel = ToolButton(Icon.CANCEL, parent=self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.__btn_ok)
        btn_box.addWidget(self.__btn_cancel)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__message_label)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    # }}}
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

        sp = QtWidgets.QSizePolicy.Policy.Minimum
        self.setSizePolicy(sp, sp)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__btn_ok.clicked.connect(self.accept)
        self.__btn_cancel.clicked.connect(self.reject)

    # }}}
    def confirm(self, message: str) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.confirm()")
        self.__message_label.setText(message)
        result = self.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            return True
        else:
            return False

    # }}}


# }}}
class _InfoDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.__message_label = QtWidgets.QLabel(self)
        self.__btn_ok = ToolButton(Icon.OK, parent=self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.__btn_ok)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__message_label)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    # }}}
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

        sp = QtWidgets.QSizePolicy.Policy.Minimum
        self.setSizePolicy(sp, sp)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.__btn_ok.clicked.connect(self.accept)

    # }}}
    def info(self, message: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.info()")

        self.__message_label.setText(message)
        self.exec()


# }}}


# }}}
class _ErrorDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.__message_label = QtWidgets.QLabel(self)
        self.__btn_ok = ToolButton(Icon.OK, parent=self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.__btn_ok)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__message_label)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    # }}}
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

        sp = QtWidgets.QSizePolicy.Policy.Minimum
        self.setSizePolicy(sp, sp)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.__btn_ok.clicked.connect(self.accept)

    # }}}
    def error(self, message: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.info()")

        self.__message_label.setText(message)
        self.exec()


# }}}


# }}}
class _NameDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__lineedit = LineEdit("Enter name", self)
        self.__btn_ok = ToolButton(Icon.OK, parent=self)
        self.__btn_cancel = ToolButton(Icon.CANCEL, parent=self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.__btn_ok)
        btn_box.addWidget(self.__btn_cancel)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__lineedit)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    # }}}
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

        sp = QtWidgets.QSizePolicy.Policy.Minimum
        self.setSizePolicy(sp, sp)

        self.__lineedit.setMinimumWidth(250)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__btn_ok.clicked.connect(self.accept)
        self.__btn_cancel.clicked.connect(self.reject)

    # }}}
    def enterName(self, message: str) -> str | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.enterName()")

        self.__lineedit.setText(message)
        result = self.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            name = self.__lineedit.text()
            return name
        else:
            return None


# }}}

# }}}

if __name__ == "__main__":
    ...
