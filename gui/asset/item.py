#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from avin.company import Tinkoff
from avin.const import ASSET_DIR
from avin.core import AssetList, Exchange, Share, Type
from avin.utils import Cmd


class IShare(Share, QtWidgets.QTreeWidgetItem):
    def __init__(self, ticker, exchange=Exchange.MOEX, parent=None):  # {{{
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Share.__init__(self, ticker, exchange, parent)
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(Tree.Column.Ticker, self.ticker)
        self.setText(Tree.Column.Name, self.name)
        self.setText(Tree.Column.Type, self.type.name)
        self.setText(Tree.Column.Exchange, self.exchange.name)

    # }}}
    @property  # {{{
    def last_price(self):
        price = Tinkoff.getLastPrice(self)
        return price


# }}}


class IAssetList(AssetList, QtWidgets.QTreeWidgetItem):
    def __init__(self, name="unnamed", parent=None):  # {{{
        logger.debug("IAssetList.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        AssetList.__init__(self, name, parent)
        self.__parent = parent
        self.setFlags(
            Qt.ItemFlag.ItemIsAutoTristate
            | Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.__updateText()

    # }}}
    def __updateText(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__updateText()")
        self.setText(Tree.Column.ListName, self.name)
        self.setText(Tree.Column.ListCount, str(self.count))

    # }}}
    @staticmethod  # load{{{
    def load(path=None, name=None, parent=None):
        logger.debug("IAssetList.load()")
        if path:
            assert name is None
            name = Cmd.name(path, extension=False)
        elif name:
            assert path is None
            path = Cmd.join(ASSET_DIR, f"{name}.al")
        ialist = IAssetList(name, parent=parent)
        obj = Cmd.loadJSON(path)
        for ID in obj:
            assert eval(ID["type"]) == Type.SHARE
            ishare = IShare(ID["ticker"])
            ialist.add(ishare)
        return ialist

    # }}}
    def parent(self):  # {{{
        logger.debug("IAssetList.parent()")
        return self.__parent

    # }}}
    def add(self, iasset: IShare):  # {{{
        logger.debug("IAssetList.add()")
        assert isinstance(iasset, IShare)
        AssetList.add(self, iasset)
        self.__updateText()

    # }}}
    def remove(self, iasset):  # {{{
        logger.debug("IAssetList.remove()")
        AssetList.remove(self, iasset)
        self.removeChild(iasset)
        self.__updateText()

    # }}}
    def clear(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")
        AssetList.clear(self)
        while self.takeChild(0):
            pass
        self.__updateText()


# }}}

if __name__ == "__main__":
    ...
