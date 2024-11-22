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


class TestEditDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__createForm()
        self.__connect()
        self.__initUI()

    # }}}

    def newTest(self):  # {{{
        new_test = ITest(name="")
        self.alist = gui.asset.IAssetList(".tmp", parent=new_test)
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.__writeTestConfig(new_test)
            ITest.save(new_test)
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

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.testname_lineedit = LineEdit()
        self.sset_lineedit = LineEdit()
        self.dblspinbox_deposit = QtWidgets.QDoubleSpinBox()
        self.dblspinbox_commission = QtWidgets.QDoubleSpinBox()
        self.begin = QtWidgets.QDateEdit()
        self.end = QtWidgets.QDateEdit()
        self.description = QtWidgets.QPlainTextEdit()
        self.ok_btn = ToolButton(Icon.OK)
        self.cancel_btn = ToolButton(Icon.CANCEL)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        self.hbox_btn = QtWidgets.QHBoxLayout()
        self.hbox_btn.addStretch()
        self.hbox_btn.addWidget(self.ok_btn)
        self.hbox_btn.addWidget(self.cancel_btn)

    # }}}
    def __createForm(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createForm()")
        form = QtWidgets.QFormLayout()
        form.addRow("Test name", self.testname_lineedit)
        form.addRow("Strategy set", self.sset_lineedit)
        form.addRow("Deposit", self.dblspinbox_deposit)
        form.addRow("Commission %", self.dblspinbox_commission)
        form.addRow("Begin date", self.begin)
        form.addRow("End date", self.end)
        form.addRow(QtWidgets.QLabel("Description"))
        form.addRow(self.description)
        form.addRow(self.hbox_btn)
        self.setLayout(form)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    # }}}
    def __initUI(self):  # {{{
        self.testname_lineedit.setText("unnamed")

        self.dblspinbox_deposit.setMinimum(0.0)
        self.dblspinbox_deposit.setMaximum(1_000_000_000.0)
        self.dblspinbox_deposit.setValue(100_000.0)

        self.dblspinbox_commission.setMinimum(0.0)
        self.dblspinbox_commission.setMaximum(1.0)
        self.dblspinbox_commission.setValue(0.05)

        self.begin.setDate(QtCore.QDate(2018, 1, 1))
        self.end.setDate(QtCore.QDate(2023, 1, 1))

    # }}}
    def __writeTest(self, test: Test):  # {{{
        test.name = self.lineedit_testname.text()
        test.description = self.description.toPlainText()
        test.strategy = self.combobox_strategy.currentText()
        test.version = self.combobox_version.currentText()
        test.alist = self.alist
        test.deposit = self.dblspinbox_deposit.value()
        test.commission = self.dblspinbox_commission.value() / 100
        test.begin = str(self.begin.date().toPyDate())
        test.end = str(self.end.date().toPyDate())
        return test

    # }}}
    def __readTest(self, test):  # {{{
        self.lineedit_testname.setText(test.name)
        self.combobox_strategy.setCurrentText(test.strategy)
        self.combobox_version.setCurrentText(test.version)
        self.dblspinbox_deposit.setValue(test.deposit)
        self.dblspinbox_commission.setValue(test.commission * 100)
        self.begin.setDate(test.begin.date())
        self.end.setDate(test.end.date())
        self.description.setPlainText(test.description)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TestEditDialog()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
