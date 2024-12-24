#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets

from avin.tester import Test
from avin.utils import logger
from gui.asset import AssetSelectDialog
from gui.custom import (
    Css,
    Icon,
    Label,
    LineEdit,
    PushButton,
    Spacer,
    ToolButton,
)
from gui.strategy import StrategySelectDialog
from gui.tester.thread import Thread


class TestEditDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createForm()
        self.__createLayots()
        self.__connect()
        self.__initUI()

    # }}}

    def newTest(self) -> Test | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.newTest()")

        # create new test, and exec edit dialog
        new_test = Test("auto")
        self.__readTest(new_test)
        result = self.exec()

        # check exec status
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            logger.info("Cancel new test")
            return None

        # write config from UI, save
        self.__writeTest(new_test)
        Thread.saveTest(new_test)

        logger.info(f"New test '{new_test.name}' created")
        return new_test

    # }}}
    def editTest(self, test: Test) -> Test | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.editTest()")

        # read test config to UI
        self.__readTest(test)
        result = self.exec()

        # check exec status
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            logger.info("Cancel edit test")
            return None

        # delete old test
        Thread.deleteTest(test)

        # create new test, write cfg from UI, set status, save
        edited = Test("unnamed")
        self.__writeTest(edited)
        edited.status = Test.Status.EDITED
        Thread.saveTest(edited)

        logger.info("Test edited")
        return edited

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")
        self.setMinimumWidth(350)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.tool_bar = _ToolBar(self)
        self.testname_lineedit = LineEdit()
        self.strategy_btn = PushButton(text="Click to select", height=25)
        self.asset_btn = PushButton(text="Click to select", height=25)
        self.long_checkbox = QtWidgets.QCheckBox("Long")
        self.short_checkbox = QtWidgets.QCheckBox("Short")
        self.deposit_dblspinbox = QtWidgets.QDoubleSpinBox()
        self.commission_dblspinbox = QtWidgets.QDoubleSpinBox()
        self.begin = QtWidgets.QDateEdit()
        self.end = QtWidgets.QDateEdit()
        self.description = QtWidgets.QPlainTextEdit()

    # }}}
    def __createForm(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createForm()")

        long_short = QtWidgets.QHBoxLayout()
        long_short.addWidget(self.long_checkbox)
        long_short.addWidget(self.short_checkbox)

        form = QtWidgets.QFormLayout()
        form.addRow("Test name", self.testname_lineedit)
        form.addRow("Strategy", self.strategy_btn)
        form.addRow("Asset", self.asset_btn)
        form.addRow("Enable", long_short)
        form.addRow("Deposit", self.deposit_dblspinbox)
        form.addRow("Commission %", self.commission_dblspinbox)
        form.addRow("Begin date", self.begin)
        form.addRow("End date", self.end)
        form.addRow(QtWidgets.QLabel("Description"))
        form.addRow(self.description)

        self.form = form

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.tool_bar)
        vbox.addLayout(self.form)

        self.setLayout(vbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.tool_bar.btn_ok.clicked.connect(self.accept)
        self.tool_bar.btn_cancel.clicked.connect(self.reject)

        self.strategy_btn.clicked.connect(self.__onStrategy)
        self.asset_btn.clicked.connect(self.__onAsset)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        self.deposit_dblspinbox.setMinimum(0.0)
        self.deposit_dblspinbox.setMaximum(1_000_000_000.0)

        self.commission_dblspinbox.setMinimum(0.0)
        self.commission_dblspinbox.setMaximum(1.0)

        self.begin.setDisplayFormat("yyyy-MM-dd")
        self.end.setDisplayFormat("yyyy-MM-dd")

    # }}}
    def __writeTest(self, test: Test):  # {{{
        logger.debug(f"{self.__class__.__name__}.__writeTest()")

        name = self.testname_lineedit.text()
        if name == "auto":
            name = (
                f"{self.__strategy.name}-"
                f"{self.__strategy.version}-"
                f"{self.__asset.ticker}"
            )

        test.name = name
        test.strategy = self.__strategy
        test.asset = self.__asset
        test.enable_long = self.long_checkbox.isChecked()
        test.enable_short = self.short_checkbox.isChecked()
        test.deposit = self.deposit_dblspinbox.value()
        test.commission = self.commission_dblspinbox.value() / 100
        test.begin = self.begin.date().toPyDate()
        test.end = self.end.date().toPyDate()
        test.description = self.description.toPlainText()

    # }}}
    def __readTest(self, t: Test) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__readTest()")

        self.testname_lineedit.setText(t.name)

        if t.strategy is not None:
            self.strategy_btn.setText(
                f"{t.strategy.name}-{t.strategy.version}"
            )
            self.__strategy = t.strategy
        else:
            self.strategy_btn.setText("Click to select")
            self.__strategy = None

        if t.asset is not None:
            self.asset_btn.setText(t.asset.ticker)
            self.__asset = t.asset
        else:
            self.asset_btn.setText("Click to select")
            self.__asset = None

        self.long_checkbox.setChecked(t.enable_long)
        self.short_checkbox.setChecked(t.enable_short)
        self.deposit_dblspinbox.setValue(t.deposit)
        self.commission_dblspinbox.setValue(t.commission * 100)
        self.begin.setDate(t.begin)
        self.end.setDate(t.end)
        self.description.setPlainText(t.description)

    # }}}

    @QtCore.pyqtSlot()  # __onStrategy  # {{{
    def __onStrategy(self):
        logger.debug(f"{self.__class__.__name__}.__onStrategy()")

        dial = StrategySelectDialog()
        strategy = dial.selectStrategy()
        if strategy is not None:
            self.__strategy = strategy
            self.strategy_btn.setText(f"{strategy.name}-{strategy.version}")
        else:
            self.__strategy = None
            self.strategy_btn.setText("Click to select")

    # }}}
    @QtCore.pyqtSlot()  # __onAsset  # {{{
    def __onAsset(self):
        logger.debug(f"{self.__class__.__name__}.__onAsset()")

        dial = AssetSelectDialog()
        asset = dial.selectAsset()
        if asset is not None:
            self.__asset = asset
            self.asset_btn.setText(asset.ticker)
        else:
            self.__asset = None
            self.asset_btn.setText("Click to select")

    # }}}


class _ToolBar(QtWidgets.QToolBar):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__createWidgets()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        title = Label("| Test config", parent=self)
        title.setStyleSheet(Css.TITLE)
        self.addWidget(title)
        self.addWidget(Spacer())

        self.btn_ok = ToolButton(Icon.OK, "Ok", parent=self)
        self.btn_cancel = ToolButton(Icon.CANCEL, "Cancel", parent=self)
        self.addWidget(self.btn_ok)
        self.addWidget(self.btn_cancel)

    # }}}


# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TestEditDialog()
    w.show()
    sys.exit(app.exec())
