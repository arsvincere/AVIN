#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from avin.core import Asset, Strategy, StrategySetNode
from avin.utils import logger
from gui.strategy.thread import Thread


class StrategyItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):
        Name = 0
        Version = 1

    def __init__(self, name: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.name = name
        self.setFlags(
            # Qt.ItemFlag.ItemIsAutoTristate
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(self.Column.Name, self.name)
        # self.setCheckState(self.Column.Name, Qt.CheckState.Unchecked)

    # }}}
    def __iter__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__iter__()")

        all_childs = list()
        for i in range(self.childCount()):
            item = self.child(i)
            all_childs.append(item)

        return iter(all_childs)

    # }}}
    def loadConfig(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadConfig()")

        cfg_path = Strategy.cfgPath(self.name)
        item = ConfigItem(cfg_path)
        self.addChild(item)

    # }}}
    def loadVersions(self, checkable: bool):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadVersions()")

        versions = Strategy.versions(self.name)
        for ver in versions:
            strategy = Thread.load(self.name, ver)
            item = VersionItem(strategy)
            if checkable:
                item.setCheckState(self.Column.Name, Qt.CheckState.Unchecked)
            self.addChild(item)

    # }}}

    @classmethod  # new  # {{{
    def new(cls, name) -> StrategyItem | None:
        logger.debug(f"{cls.__name__}.new()")

        # try create Strategy & save in db
        strategy = Thread.new(name)
        if not strategy:
            return None

        # create QTreeWidgetItem
        item = StrategyItem(name)
        return item

    # }}}
    @classmethod  # rename  # {{{
    def rename(cls, item: StrategyItem, new_name) -> VersionItem | None:
        logger.debug(f"{cls.__name__}.rename()")

        # try rename strategy & update db
        renamed = Thread.renameStrategy(item.name, new_name)
        if not renamed:
            return None

        # rename QTreeWidgetItem
        item.name = new_name
        item.setText(StrategyItem.Column.Name, new_name)

        # remove childs (versions and config)
        while item.childCount():
            item.takeChild(0)

        # reload config
        # TODO: duplicated code below and
        # func __loadConfig, __loadVersions
        # тут надо конструктор переделать...  и эти функции
        # они должны не в селф результат сразу пихать а
        # возвращать соответствующие значения, а конструктор
        # уже эти значения добавляет как чайлд итем.
        # и тут тоже дернуть эти функции тогда и добавить чайлд итемы.
        # или... передавать этим функциям для какого элемента
        # загрузить конфиг и версии. То есть сделать их тогда
        # classmethod-ами
        # думаю второе предпочтительнее.
        cfg_path = Strategy.cfgPath(renamed)
        cfg_item = ConfigItem(cfg_path)
        item.addChild(cfg_item)

        # reload versions
        versions = Strategy.versions(renamed)
        for ver in versions:
            strategy = Thread.load(renamed, ver)
            ver_item = VersionItem(strategy)
            item.addChild(ver_item)

        return item

    # }}}
    @classmethod  # delete  # {{{
    def delete(cls, item: StrategyItem) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        Thread.deleteStrategy(item.name)

    # }}}


# }}}
class VersionItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):
        Name = 0
        Version = 1

    def __init__(self, strategy, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.strategy = strategy
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(StrategyItem.Column.Name, self.strategy.version)

    # }}}
    @property  # path  # {{{
    def path(self):
        return Strategy.path(self.strategy)

    # }}}
    def isChecked(self) -> bool:
        logger.debug(f"{self.__class__.__name__}.isChecked()")

        check_state = self.checkState(self.Column.Name)

        return check_state == Qt.CheckState.Checked

    @classmethod  # copy  # {{{
    def copy(cls, item, new_name) -> VersionItem | None:
        logger.debug(f"{cls.__name__}.copy()")

        # try create new version & save in db
        new_strategy = Thread.copy(item.strategy, new_name)
        if not new_strategy:
            return None

        # create QTreeWidgetItem
        new_item = cls(new_strategy)
        return new_item

    # }}}
    @classmethod  # rename  # {{{
    def rename(cls, item, new_name) -> VersionItem | None:
        logger.debug(f"{cls.__name__}.rename()")

        # try rename strategy & update db
        renamed = Thread.renameVersion(item.strategy, new_name)
        if not renamed:
            return None

        # rename QTreeWidgetItem
        item.setText(StrategyItem.Column.Name, new_name)
        return item

    # }}}
    @classmethod  # delete  # {{{
    def delete(cls, item: VersionItem) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        Thread.deleteVersion(item.strategy)

    # }}}


# }}}
class ConfigItem(QtWidgets.QTreeWidgetItem):  # {{{
    def __init__(self, path, parent=None):  # {{{
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.path = path
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(StrategyItem.Column.Name, "config")

    # }}}


# }}}
class StrategySetNodeItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0
        Figi = 1
        Long = 2
        Short = 3

    # }}}
    def __init__(self, node: StrategySetNode, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.__node = node
        self.__asset: Optional[Asset] = None

        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )

        self.setText(self.Column.Figi, self.__node.figi)

        yes = Qt.CheckState.Checked
        no = Qt.CheckState.Unchecked
        long = yes if self.__node.long else no
        short = yes if self.__node.short else no
        self.setCheckState(self.Column.Long, long)
        self.setCheckState(self.Column.Short, short)

    # }}}
    @property  # node  # {{{
    def node(self):
        return self.__node

    # }}}
    @property  # strategy  # {{{
    def strategy(self):
        return self.__node.strategy

    # }}}
    @property  # version  # {{{
    def version(self):
        return self.__node.version

    # }}}
    @property  # figi  # {{{
    def figi(self):
        return self.__node.figi

    # }}}
    @property  # long  # {{{
    def long(self):
        return self.__node.long

    # }}}
    @property  # short  # {{{
    def short(self):
        return self.__node.short

    # }}}
    def setAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setAsset()")

        assert asset.figi == self.__node.figi
        self.__asset = asset
        self.setText(self.Column.Name, asset.ticker)

    # }}}
    @classmethod  # new
    def new(
        cls,
        group: StrategySetNodeGroup,
        asset: Asset,
        long=False,
        short=False,
    ):
        logger.debug(f"{cls.__name__}.new()")

        node = StrategySetNode(
            strategy=group.strategy,
            version=group.version,
            figi=asset.figi,
            long=long,
            short=short,
        )

        item = cls(node)
        item.setAsset(asset)

        return item


# }}}
class StrategySetNodeGroup(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0
        Count = 1
        Long = 2
        Short = 3

    # }}}
    def __init__(self, strategy: Strategy, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.__strategy = strategy
        self.__count = 0

        self.setFlags(
            Qt.ItemFlag.ItemIsAutoTristate
            | Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(self.Column.Name, f"{strategy.name}-{strategy.version}")
        self.setText(self.Column.Count, str(self.__count))

    # }}}
    def __iter__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__iter__()")

        all_child = list()
        for i in range(self.childCount):
            child = self.child(i)
            all_child.append(child)

        return iter(all_child)

    # }}}
    def __contains__(self, asset: Asset) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.__contains__()")

        for node in self:
            if node.figi == asset.figi:
                return True

        return False

    # }}}
    @property  # strategy  # {{{
    def strategy(self) -> str:
        return self.__strategy.name

    # }}}
    @property  # version  # {{{
    def version(self) -> str:
        return self.__strategy.version

    # }}}
    def addAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.addAsset()")

        if asset in self:
            return

        node_item = StrategySetNode.new(self, asset)
        self.addChild(node_item)

    # }}}
    def removeAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeAsset()")

        if asset not in self:
            return

        for child in self:
            if child.figi == asset.figi:
                self.removeChild(child)
                return

    # }}}
    def clearAssets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearAssets()")

        while self.childCount():
            self.takeChild(0)

    # }}}


# }}}


if __name__ == "__main__":
    ...
