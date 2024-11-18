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

from avin.core import Strategy
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
        self.__config()
        self.__loadConfig()
        self.__loadVersions()

    # }}}

    def __config(self):  # {{{
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(self.Column.Name, self.name)
        # self.setCheckState(self.Column.Name, Qt.CheckState.Unchecked)

    # }}}
    def __loadConfig(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadConfig()")

        cfg_path = Strategy.cfgPath(self.name)
        item = ConfigItem(cfg_path)
        self.addChild(item)

    # }}}
    def __loadVersions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadVersions()")

        versions = Strategy.versions(self.name)
        for ver in versions:
            strategy = Thread.load(self.name, ver)
            item = VersionItem(strategy)
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
    def __init__(self, strategy, parent=None):  # {{{
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.strategy = strategy
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(StrategyItem.Column.Name, self.strategy.version)
        # self.setCheckState(StrategyItem.Column.Name, Qt.CheckState.Unchecked)

    # }}}
    @property  # path  # {{{
    def path(self):
        return Strategy.path(self.strategy)

    # }}}
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


class IAssetCfg(QtWidgets.QTreeWidgetItem):  # {{{
    def __init__(self, asset, parent=None):  # {{{
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__config()
        self.__parent = parent
        self.asset = asset

    # }}}
    def __config(self):  # {{{
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(Tree.Column.Name, self.ticker)


# }}}


# }}}
# class IAssetListCfg(AssetList, QtWidgets.QTreeWidgetItem):  # {{{
#     def __init__(self, name, parent=None):  # {{{
#         logger.debug(f"{self.__class__.__name__}.__init__()")
#         QtWidgets.QTreeWidgetItem.__init__(self, parent)
#         AssetList.__init__(self, name)
#         self.__parent = parent
#         self.setFlags(
#             Qt.ItemFlag.ItemIsAutoTristate
#             | Qt.ItemFlag.ItemIsUserCheckable
#             | Qt.ItemFlag.ItemIsDragEnabled
#             | Qt.ItemFlag.ItemIsDropEnabled
#             | Qt.ItemFlag.ItemIsSelectable
#             | Qt.ItemFlag.ItemIsEnabled
#         )
#         self.__updateText()
#
#     # }}}
#     def __updateText(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.__updateText()")
#         self.setText(Tree.Column.Name, self.name)
#
#     # }}}
#     @staticmethod  # load{{{
#     def load(path=None, name=None, parent=None):
#         logger.debug(f"{__class__.__name__}.load()")
#         if path:
#             assert name is None
#             name = Cmd.name(path, extension=False)
#         elif name:
#             assert path is None
#             path = Cmd.join(ASSET_DIR, f"{name}.al")
#         ialist_cfg = IAssetListCfg("assets", parent=parent)
#         obj = Cmd.loadJSON(path)
#         for ID in obj:
#             assert eval(ID["type"]) == Type.SHARE
#             share = Share(ID["ticker"])
#             cfg = IAssetCfg(share)
#             ialist_cfg.add(cfg)
#         return ialist_cfg
#
#     # }}}
#     def parent(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.parent()")
#         return self.__parent
#
#     # }}}
#     def add(self, iasset: IAssetCfg):  # {{{
#         logger.debug(f"{self.__class__.__name__}.add()")
#         AssetList.add(self, iasset)
#         self.addChild(iasset)
#         self.__updateText()
#
#     # }}}
#     def remove(self, iasset):  # {{{
#         logger.debug(f"{self.__class__.__name__}.remove()")
#         AssetList.remove(self, iasset)
#         self.removeChild(iasset)
#         self.__updateText()
#
#     # }}}
#     def clear(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.clear()")
#         AssetList.clear(self)
#         while self.takeChild(0):
#             pass
#         self.__updateText()
#
#
# # }}}
#
#
# # }}}


if __name__ == "__main__":
    ...
