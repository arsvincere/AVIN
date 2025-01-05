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

from avin.core import Filter, FilterList
from avin.utils import logger


class FilterItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0

    # }}}
    def __init__(self, filter: Filter, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.filter = filter
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsUserCheckable
        )

        self.setText(self.Column.Name, self.filter.full_name)

    # }}}


# }}}
class FilterListItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0

    # }}}
    def __init__(self, filter_list: FilterList, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.filter_list = filter_list

        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsUserCheckable
        )
        self.setText(self.Column.Name, self.filter_list.name)

        self.__createChilds()

    # }}}

    def __createChilds(self):
        logger.debug(f"{self.__class__.__name__}.__createChilds()")

        # create filters
        for f in self.filter_list.filters:
            item = FilterItem(f)
            self.addChild(item)

        # create child filter lists
        for child in self.filter_list.childs:
            child_item = FilterListItem(child)
            self.addChild(child_item)


# }}}


if __name__ == "__main__":
    ...
