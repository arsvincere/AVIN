#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys
from datetime import date

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.core import TimeFrame, TimeFrameList
from avin.data import DataSource, Instrument
from avin.utils import logger
from gui.custom import (
    Css,
    Dialog,
    Label,
    Menu,
    PushButton,
    Spacer,
    SubTitleLabel,
    TimeFrameBar,
    ToolButton,
    YearWidget,
)
from gui.data.item import DownloadItem
from gui.data.thread import Thread


class DataDownloadDialog(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)

        self.__thread = None

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()
        self.__initUI()

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.toolbar = _ToolBar(self)
        self.tree = _Tree(self)
        self.right_panel = _RightPanel(self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.tree)
        hbox.addWidget(self.right_panel)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.toolbar)
        vbox.addLayout(hbox)

        vbox.setContentsMargins(8, 4, 8, 8)
        self.setLayout(vbox)

    # }}}
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.DIALOG)
        self.setWindowTitle("AVIN")

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.toolbar.typeChanged.connect(self.__updateTree)
        self.toolbar.sourceChanged.connect(self.__updateTree)
        self.right_panel.request_date.clicked.connect(self.__onFirstDate)
        self.right_panel.download_btn.clicked.connect(self.__onDownload)
        self.right_panel.cancel_btn.clicked.connect(self.reject)

    # }}}
    def __initUI(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        self.__updateTree()

    # }}}
    def __isBusy(self) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.__isBusy()")

        if self.__thread is not None:
            Dialog.info("Data manager is busy now, wait for complete task")
            return True

        return False

    # }}}
    @QtCore.pyqtSlot()  # __updateTree  # {{{
    def __updateTree(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__updateTree()")

        source = self.toolbar.currentSource()
        itype = self.toolbar.currentType()

        instruments = Thread.find(source, itype)

        self.tree.setInstrumentsList(instruments)

    # }}}
    @QtCore.pyqtSlot()  # __onFirstDate  # {{{
    def __onFirstDate(self):
        logger.debug(f"{self.__class__.__name__}.__onFirstDate()")

        source = self.toolbar.currentSource()

        # receive first datetime & update tree
        Thread.firstDateTime(source, self.tree)

    # }}}
    @QtCore.pyqtSlot()  # __onDownload  # {{{
    def __onDownload(self):
        logger.debug(f"{self.__class__.__name__}.__onDownload()")

        source = self.toolbar.currentSource()
        instruments = self.tree.selectedInstruments()
        timeframes = self.right_panel.selectedTimeframes()
        begin = self.right_panel.begin()
        end = self.right_panel.end()

        Thread.download(source, instruments, timeframes, begin, end)

    # }}}


# }}}


class _SourceMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        Menu.__init__(self, parent=parent)
        self.__createActions()

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.moex = QtGui.QAction("MOEX", self)
        self.moex.setData(DataSource.MOEX)
        self.tinkoff = QtGui.QAction("TINKOFF", self)
        self.tinkoff.setData(DataSource.TINKOFF)

        self.addAction(self.moex)
        self.addAction(self.tinkoff)

    # }}}


# }}}
class _InstrumentTypeMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        Menu.__init__(self, parent=parent)
        self.__createActions()

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.index = QtGui.QAction("INDEX", self)
        self.share = QtGui.QAction("SHARE", self)
        self.bond = QtGui.QAction("BOND", self)
        self.future = QtGui.QAction("FUTURE", self)
        self.currency = QtGui.QAction("CURRENCY", self)

        self.index.setData(Instrument.Type.INDEX)
        self.share.setData(Instrument.Type.SHARE)
        self.bond.setData(Instrument.Type.BOND)
        self.future.setData(Instrument.Type.FUTURE)
        self.currency.setData(Instrument.Type.CURRENCY)

        self.addAction(self.index)
        self.addAction(self.share)
        self.addAction(self.bond)
        self.addAction(self.future)
        self.addAction(self.currency)

    # }}}


# }}}
class _ToolBar(QtWidgets.QToolBar):  # {{{
    typeChanged = QtCore.pyqtSignal()
    sourceChanged = QtCore.pyqtSignal()
    __ICON_SIZE = QtCore.QSize(32, 32)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__createButtons()
        self.__createMenus()
        self.__config()
        self.__connect()

    # }}}
    def currentSource(self) -> DataSource:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentSource()")

        return self.__current_source

    # }}}
    def currentType(self) -> Instrument.Type:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentSource()")

        return self.__current_instrument_type

    # }}}
    def __createButtons(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.source_btn = ToolButton(width=64, parent=self)
        self.source_btn.setText("MOEX")
        self.__current_source = DataSource.MOEX

        self.instrument_type_btn = ToolButton(width=96, parent=self)
        self.instrument_type_btn.setText("SHARE")
        self.__current_instrument_type = Instrument.Type.SHARE
        self.addWidget(self.source_btn)
        self.addWidget(self.instrument_type_btn)

    # }}}
    def __createMenus(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.source_menu = _SourceMenu(parent=self)
        self.source_btn.setMenu(self.source_menu)
        self.source_btn.setPopupMode(
            QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
        )

        self.instrument_type_menu = _InstrumentTypeMenu(self)
        self.instrument_type_btn.setMenu(self.instrument_type_menu)
        self.instrument_type_btn.setPopupMode(
            QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
        )

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setIconSize(self.__ICON_SIZE)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.STYLE)

        self.setToolTipDuration

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.source_menu.triggered.connect(self.__onSourceTriggered)
        self.instrument_type_menu.triggered.connect(self.__onTypeTriggered)

    # }}}
    @QtCore.pyqtSlot(QtGui.QAction)  # __onSourceTriggered{{{
    def __onSourceTriggered(self, action: QtGui.QAction):
        logger.debug(f"{self.__class__.__name__}.__onSourceTriggered()")

        source = action.data()
        if self.__current_source != source:
            self.__current_source = source
            self.source_btn.setText(source.name)
            self.sourceChanged.emit()

    # }}}
    @QtCore.pyqtSlot(QtGui.QAction)  # __onTypeTriggered{{{
    def __onTypeTriggered(self, action: QtGui.QAction):
        logger.debug(f"{self.__class__.__name__}.__onSourceTriggered()")

        typ = action.data()
        if self.__current_instrument_type != typ:
            self.__current_instrument_type = typ
            self.instrument_type_btn.setText(typ.name)
            self.typeChanged.emit()

    # }}}


# }}}
class _Tree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__connect()

    # }}}
    def __iter__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__iter__()")
        all_items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            all_items.append(item)
        return iter(all_items)

    # }}}
    def setInstrumentsList(self, instr_list: list[Instrument]) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setInstrumentsList()")

        self.clear()
        for i in instr_list:
            item = DownloadItem(i, parent=self)
            self.addTopLevelItem(item)

    # }}}
    def selectedInstruments(self) -> list[Instrument]:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectedInstruments()")

        selected = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if (
                item.checkState(DownloadItem.Column.Ticker)
                == Qt.CheckState.Checked
            ):
                selected.append(item.instrument)
        return selected

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # set header labels
        labels = list()
        for l in DownloadItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)

        # set sizes
        self.setColumnWidth(DownloadItem.Column.Ticker, 100)
        self.setColumnWidth(DownloadItem.Column.Name, 300)
        self.setColumnWidth(DownloadItem.Column.First_1M, 100)
        self.setColumnWidth(DownloadItem.Column.First_D, 100)
        self.setMinimumWidth(620)
        self.setMinimumHeight(400)

        # other options
        self.setSortingEnabled(True)
        self.sortByColumn(
            DownloadItem.Column.Ticker, Qt.SortOrder.AscendingOrder
        )

        # size policy
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

    # }}}


# }}}
class _RightPanel(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__config()

    # }}}
    def selectedTimeframes(self) -> TimeFrameList:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectedTimeframes()")

        return self.__timeframes_bar.selected()

    # }}}
    def begin(self) -> int:  # {{{
        logger.debug(f"{self.__class__.__name__}.begin()")

        return self.__begin_year.value()

    # }}}
    def end(self) -> int:  # {{{
        logger.debug(f"{self.__class__.__name__}.end()")

        return self.__end_year.value()

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        # request date
        self.request_date = PushButton("Get date")

        # timeframes
        self.__timeframes_bar = TimeFrameBar(self)
        self.__timeframes_bar.add(TimeFrame("1M"))
        self.__timeframes_bar.add(TimeFrame("10M"))
        self.__timeframes_bar.add(TimeFrame("1H"))
        self.__timeframes_bar.add(TimeFrame("D"))
        self.__timeframes_bar.add(TimeFrame("W"))
        self.__timeframes_bar.add(TimeFrame("M"))
        self.__timeframes_bar.setSelected(TimeFrame("1M"))
        self.__timeframes_bar.setSelected(TimeFrame("D"))

        # period
        now_year = date.today().year
        self.__begin_year = YearWidget("Begin year:", year=1997, parent=self)
        self.__end_year = YearWidget("End year:", year=now_year, parent=self)

        # buttons
        self.download_btn = PushButton("Download")
        self.cancel_btn = PushButton("Cancel")

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        # buttons
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.download_btn)
        hbox.addWidget(self.cancel_btn)

        # panel
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(SubTitleLabel("Request first date", self))
        text = (
            "Candles '1M' and 'D' timeframes<br>"
            "are available from different dates,<br>"
            "select the tools of interest and<br>"
            "push get date"
        )
        vbox.addWidget(Label(text, self))
        vbox.addWidget(Spacer(height=8))
        vbox.addWidget(self.request_date)

        vbox.addWidget(Spacer(height=16))
        vbox.addWidget(SubTitleLabel("Select timeframes", self))
        vbox.addWidget(self.__timeframes_bar)

        vbox.addWidget(Spacer(height=16))
        vbox.addWidget(SubTitleLabel("Select period", self))
        vbox.addWidget(self.__begin_year)
        vbox.addWidget(self.__end_year)

        vbox.addStretch()
        vbox.addLayout(hbox)

        vbox.setContentsMargins(8, 0, 8, 8)
        self.setLayout(vbox)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.STYLE)

        # size policy
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = DialogDataDownload()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
