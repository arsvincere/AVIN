#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from avin import (
    Test,
    TestList,
    logger,
)
from gui.tester.progress_bar import TestProgressBar


class TestItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0
        Status = 1

    # }}}

    def __init__(self, test: Test, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.test = test
        self.progress_bar = TestProgressBar()
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )

        self.updateText()

    # }}}

    def updateText(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.update()")

        self.setText(self.Column.Name, self.test.name)
        self.setText(self.Column.Status, self.test.status.name)

    # }}}
    def updateProgressBar(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.updateProgressBar()")

        if self.status == Test.Status.UNDEFINE:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Undefine")
        elif self.status == Test.Status.NEW:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("New")
        elif self.status == Test.Status.EDITED:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Edited")
        elif self.status == Test.Status.PROCESS:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("%p%")
        elif self.status == Test.Status.COMPLETE:
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Complete")

        tree = self.parent()
        if tree:
            tree.setItemWidget(
                self, TestTree.Column.Progress, self.progress_bar
            )

    # }}}


# }}}
class TestListItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0

    # }}}

    def __init__(self, test_list: TestList, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.test_list = test_list
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )

        self.setText(self.Column.Name, self.test_list.name)

        for test in self.test_list:
            item = TestItem(test)
            self.addChild(item)

    # }}}


# }}}


if __name__ == "__main__":
    ...
