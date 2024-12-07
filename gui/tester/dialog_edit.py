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
from gui.custom import Css, Icon, LineEdit, ToolButton
from gui.strategy import StrategySetWidget
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

    def newTest(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.newTest()")

        new_test = Test("unnamed")
        self.__readTest(new_test)
        result = self.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.__writeTest(new_test)
            Thread.saveTest(new_test)
            logger.info(f"New test '{new_test.name}' created")
            return new_test
        else:
            logger.info("Cancel new test")
            return False

    # }}}
    def editTest(self, itest):  # {{{
        self.__readTestConfig(itest)
        self.alist = itest.alist
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            ITest.delete(itest)
            edited = ITest(name="")
            edited = self.__writeTestConfig(edited)
            edited.status = Test.Status.EDITED
            ITest.save(edited)
            logger.info("Test edited")
            return edited
        else:
            logger.info("Cancel edit test")
            return False

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.testname_lineedit = LineEdit()
        self.dblspinbox_deposit = QtWidgets.QDoubleSpinBox()
        self.dblspinbox_commission = QtWidgets.QDoubleSpinBox()
        self.begin = QtWidgets.QDateEdit()
        self.end = QtWidgets.QDateEdit()
        self.description = QtWidgets.QPlainTextEdit()

        self.sset_widget = StrategySetWidget(self)

        self.ok_btn = ToolButton(Icon.OK)
        self.cancel_btn = ToolButton(Icon.CANCEL)

    # }}}
    def __createForm(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createForm()")
        form = QtWidgets.QFormLayout()
        form.addRow("Test name", self.testname_lineedit)
        form.addRow("Deposit", self.dblspinbox_deposit)
        form.addRow("Commission %", self.dblspinbox_commission)
        form.addRow("Begin date", self.begin)
        form.addRow("End date", self.end)
        form.addRow(QtWidgets.QLabel("Description"))
        form.addRow(self.description)

        self.form = form

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(self.form)
        hbox.addWidget(self.sset_widget)

        hbox_btn = QtWidgets.QHBoxLayout()
        hbox_btn.addStretch()
        hbox_btn.addWidget(self.ok_btn)
        hbox_btn.addWidget(self.cancel_btn)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox_btn)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    # }}}

    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    # }}}
    def __initUI(self):  # {{{
        self.dblspinbox_deposit.setMinimum(0.0)
        self.dblspinbox_deposit.setMaximum(1_000_000_000.0)

        self.dblspinbox_commission.setMinimum(0.0)
        self.dblspinbox_commission.setMaximum(1.0)

    # }}}
    def __writeTest(self, test: Test):  # {{{
        test.name = self.testname_lineedit.text()
        test.strategy_set = self.sset_widget.currentStrategySet()
        test.deposit = self.dblspinbox_deposit.value()
        test.commission = self.dblspinbox_commission.value() / 100
        test.begin = self.begin.date().toPyDate()
        test.end = self.end.date().toPyDate()
        test.description = self.description.toPlainText()
        return test

    # }}}
    def __readTest(self, test):  # {{{
        self.testname_lineedit.setText(test.name)
        self.sset_widget.setStrategySet(test.strategy_set)
        self.dblspinbox_deposit.setValue(test.deposit)
        self.dblspinbox_commission.setValue(test.commission * 100)
        self.begin.setDate(test.begin)
        self.end.setDate(test.end)
        self.description.setPlainText(test.description)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TestEditDialog()
    w.show()
    sys.exit(app.exec())
