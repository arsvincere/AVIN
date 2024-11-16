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

        cfg_path = Strategy.config(self.name)
        item = ConfigItem(cfg_path)
        self.addChild(item)

    # }}}
    def __loadVersions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadVersions()")

        self.versions = Strategy.versions(self.name)
        for ver in self.versions:
            strategy = Thread.load(self.name, ver)
            item = VersionItem(strategy)
            self.addChild(item)

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
