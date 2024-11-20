#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets

import avin.gui as gui
from avin.const import STRATEGY_DIR
from avin.core import Strategy, Test, TimeFrame
from avin.gui.custom import Icon
from avin.utils import Cmd, logger


class Editor(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__createForm()
        self.__configButton()
        self.__connect()
        self.__config()
        self.__loadUserStrategy()
        self.__loadUserTimeframes()
        self.__initUI()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.lineedit_testname = QtWidgets.QLineEdit()
        self.combobox_strategy = QtWidgets.QComboBox()
        self.combobox_version = QtWidgets.QComboBox()
        self.combobox_timeframe = QtWidgets.QComboBox()
        self.dblspinbox_deposit = QtWidgets.QDoubleSpinBox()
        self.dblspinbox_commission = QtWidgets.QDoubleSpinBox()
        self.begin = QtWidgets.QDateEdit()
        self.end = QtWidgets.QDateEdit()
        self.description = QtWidgets.QPlainTextEdit()
        self.btn_alist = QtWidgets.QToolButton()
        self.btn_save = QtWidgets.QToolButton()
        self.btn_cancel = QtWidgets.QToolButton()

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        self.hbox_btn = QtWidgets.QHBoxLayout()
        self.hbox_btn.addStretch()
        self.hbox_btn.addWidget(self.btn_save)
        self.hbox_btn.addWidget(self.btn_cancel)
        self.hbox_alist = QtWidgets.QHBoxLayout()
        self.hbox_alist.addStretch()
        self.hbox_alist.addWidget(self.btn_alist)

    # }}}
    def __createForm(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createForm()")
        form = QtWidgets.QFormLayout()
        form.addRow("Test name", self.lineedit_testname)
        form.addRow("Strategy", self.combobox_strategy)
        form.addRow("Version", self.combobox_version)
        form.addRow("Timeframe", self.combobox_timeframe)
        form.addRow("Asset list", self.hbox_alist)
        form.addRow("Deposit", self.dblspinbox_deposit)
        form.addRow("Commission %", self.dblspinbox_commission)
        form.addRow("Begin date", self.begin)
        form.addRow("End date", self.end)
        form.addRow(QtWidgets.QLabel("Description"))
        form.addRow(self.description)
        form.addRow(self.hbox_btn)
        self.setLayout(form)

    # }}}
    def __configButton(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__configButton()")
        self.btn_alist.setIcon(Icon.ASSET)
        self.btn_alist.setFixedSize(32, 32)
        self.btn_alist.setIconSize(QtCore.QSize(30, 30))
        self.btn_save.setIcon(Icon.SAVE)
        self.btn_save.setFixedSize(32, 32)
        self.btn_save.setIconSize(QtCore.QSize(30, 30))
        self.btn_cancel.setIcon(Icon.CANCEL)
        self.btn_cancel.setFixedSize(32, 32)
        self.btn_cancel.setIconSize(QtCore.QSize(30, 30))

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.combobox_strategy.currentTextChanged.connect(self.__loadVersions)
        self.btn_alist.clicked.connect(self.__editAssetList)
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    # }}}
    def __loadUserStrategy(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserStrategy()")
        dirs = Cmd.getDirs(STRATEGY_DIR)
        for name in dirs:
            self.combobox_strategy.addItem(name)

    # }}}
    def __loadVersions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadVersions()")
        name = self.combobox_strategy.currentText()
        versions = Strategy.versions(name)
        self.combobox_version.clear()
        self.combobox_version.addItems(versions)

    # }}}
    def __loadUserTimeframes(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserTimeframes()")
        for timeframe in TimeFrame.ALL:
            self.combobox_timeframe.addItem(str(timeframe))

    # }}}
    def __initUI(self):  # {{{
        self.combobox_timeframe.setCurrentText("1M")
        self.lineedit_testname.setText("unnamed")
        self.dblspinbox_deposit.setMinimum(0.0)
        self.dblspinbox_deposit.setMaximum(1_000_000_000.0)
        self.dblspinbox_deposit.setValue(100_000.0)
        self.dblspinbox_commission.setMinimum(0.0)
        self.dblspinbox_commission.setMaximum(1.0)
        self.dblspinbox_commission.setValue(0.05)
        self.begin.setDate(QtCore.QDate(2018, 1, 1))
        self.end.setDate(QtCore.QDate(2023, 1, 1))

    # }}}
    def __editAssetList(self):  # {{{
        editor = gui.asset.Editor()
        editor.editAssetList(self.alist)

    # }}}
    def __writeTestConfig(self, test):  # {{{
        test.name = self.lineedit_testname.text()
        test.description = self.description.toPlainText()
        test.strategy = self.combobox_strategy.currentText()
        test.version = self.combobox_version.currentText()
        test.timeframe = TimeFrame(self.combobox_timeframe.currentText())
        test.alist = self.alist
        test.deposit = self.dblspinbox_deposit.value()
        test.commission = self.dblspinbox_commission.value() / 100
        test.begin = str(self.begin.date().toPyDate())
        test.end = str(self.end.date().toPyDate())
        test.updateText()
        return test

    # }}}
    def __readTestConfig(self, test):  # {{{
        self.lineedit_testname.setText(test.name)
        self.combobox_strategy.setCurrentText(test.strategy)
        self.combobox_version.setCurrentText(test.version)
        self.combobox_timeframe.setCurrentText(str(test.timeframe))
        self.dblspinbox_deposit.setValue(test.deposit)
        self.dblspinbox_commission.setValue(test.commission * 100)
        self.begin.setDate(test.begin.date())
        self.end.setDate(test.end.date())
        self.description.setPlainText(test.description)

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
# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TestWidget()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
