#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio
import enum
import sys
from datetime import date, datetime

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.const import Res
from avin.core import TimeFrame, TimeFrameList
from avin.data import Data, DataSource, DataType, Instrument
from avin.data._moex import _MoexData
from avin.utils import Cmd, logger
from gui.custom import (
    Css,
    Dialog,
    Icon,
    Label,
    Menu,
    PushButton,
    Spacer,
    SubTitle,
    TimeFrameBar,
    ToolButton,
    YearWidget,
)


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

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.toolbar.typeChanged.connect(self.__updateTree)
        self.toolbar.sourceChanged.connect(self.__updateTree)
        self.right_panel.request_date.clicked.connect(self.__onFirstDate)
        self.right_panel.download_btn.clicked.connect(self.__onDownload)
        self.right_panel.cancel_btn.clicked.connect(self.__onCancel)

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

        if self.__isBusy():
            return

        # find instruments
        source = self.toolbar.currentSource()
        itype = self.toolbar.currentType()
        self.__thread = _TFind(source, itype, parent=self)
        self.__thread.finded.connect(self.__onFinded)
        self.__thread.finished.connect(self.__onThreadFinished)
        self.__thread.start()
        #

    # }}}
    @QtCore.pyqtSlot(list)  # __onFinded  # {{{
    def __onFinded(self, instruments: list[Instrument]):
        logger.debug(f"{self.__class__.__name__}.__onFinded()")

        self.tree.setInstrumentsList(instruments)

    # }}}
    @QtCore.pyqtSlot()  # __onFirstDate  # {{{
    def __onFirstDate(self):
        logger.debug(f"{self.__class__.__name__}.__onFirstDate()")

        if self.__isBusy():
            return

        # receive first datetime
        source = self.toolbar.currentSource()
        self.__thread = _TFirstDate(source, self.tree, parent=self)
        self.__thread.finished.connect(self.__onThreadFinished)
        self.__thread.start()

    # }}}
    @QtCore.pyqtSlot()  # __onDownload  # {{{
    def __onDownload(self):
        logger.debug(f"{self.__class__.__name__}.__onDownload()")

        if self.__isBusy():
            return

        source = self.toolbar.currentSource()
        instruments = self.tree.selectedInstruments()
        timeframes = self.right_panel.selectedTimeframes()
        begin = self.right_panel.begin()
        end = self.right_panel.end()

        self.__thread = _TDownload(
            source, instruments, timeframes, begin, end, parent=self
        )
        self.__thread.finished.connect(self.__onThreadFinished)
        self.__thread.start()
        # self.download_btn.setEnabled(False)

    # }}}
    @QtCore.pyqtSlot()  # __onCancel  # {{{
    def __onCancel(self):
        logger.debug(f"{self.__class__.__name__}.__onCancel()")

        self.reject()

    # }}}
    @QtCore.pyqtSlot()  # __onThreadFinished  # {{{
    def __onThreadFinished(self):
        logger.debug(f"{self.__class__.__name__}.__onThreadFinished()")

        del self.__thread
        self.__thread = None

    # }}}


# }}}


class _TFind(QtCore.QThread):  # {{{
    finded = QtCore.pyqtSignal(list)

    def __init__(  # {{{
        self, source, itype, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__source = source
        self.__itype = itype

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__afind())

    # }}}
    async def __afind(self):  # {{{
        logger.info(f":: Find instruments {self.__source} {self.__itype}")

        instruments = await Data.find(
            source=self.__source, itype=self.__itype
        )
        self.finded.emit(instruments)
        logger.info(f"Finded {len(instruments)} instruments!")

    # }}}


# }}}
class _TFirstDate(QtCore.QThread):  # {{{
    def __init__(self, source, tree, parent=None):  # {{{
        QtCore.QThread.__init__(self, parent)
        self.__source = source
        self.__tree = tree

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__afirst())

    # }}}
    async def __afirst(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__afirst()")
        logger.info(":: Receiving first date")

        for i in self.__tree:
            if i.checkState(_Item.Column.Ticker) != Qt.CheckState.Checked:
                continue

            # receive first 1M datetime
            dt = await Data.firstDateTime(
                self.__source, i.instrument, DataType.BAR_1M
            )
            if dt is not None:
                dt = dt.strftime("%Y-%m-%d")
                i.setText(_Item.Column.First_1M, dt)
                logger.info(
                    f"  - received first 1M date for {i.instrument} -> {dt}"
                )

            # receive first D datetime
            dt = await Data.firstDateTime(
                self.__source, i.instrument, DataType.BAR_D
            )
            if dt is not None:
                dt = dt.strftime("%Y-%m-%d")
                i.setText(_Item.Column.First_D, dt)
                logger.info(
                    f"  - received first D date for {i.instrument} -> {dt}"
                )

    # }}}


# }}}
class _TDownload(QtCore.QThread):  # {{{
    def __init__(  # {{{
        self, source, instruments, timeframes, begin, end, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__source = source
        self.__instruments = instruments
        self.__timeframes = timeframes
        self.__begin = begin
        self.__end = end

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__adownload())

    # }}}
    async def __adownload(self):  # {{{
        logger.info(":: Start download data")

        for instrument in self.__instruments:
            for timeframe in self.__timeframes:
                data_type = timeframe.toDataType()
                year = self.__begin
                while year <= self.__end:
                    await Data.download(
                        self.__source, instrument, data_type, year
                    )
                    year += 1

        logger.info("Download complete!")

    # }}}


# }}}


class _SourceMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        Menu.__init__(self, parent)
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
        Menu.__init__(self, parent)
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

        self.source_menu = _SourceMenu(self)
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
class _Item(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Ticker = 0
        Name = 1
        First_1M = 2
        First_D = 3

    # }}}
    def __init__(self, instrument: Instrument, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.instrument = instrument

        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setCheckState(self.Column.Ticker, Qt.CheckState.Unchecked)
        self.setText(self.Column.Ticker, instrument.ticker)
        self.setText(self.Column.Name, instrument.name)

    # }}}

    @QtCore.pyqtSlot(datetime, DataType)  # __onFirstDateTime  # {{{
    def __onFirstDateTime(self, dt: datetime, data_type: DataType) -> None:
        logger.debug(f"{self.__class__.__name__}.__onFirstDateTime()")

        if data_type == DataType.BAR_1M:
            column = self.Column.First_1M
        elif data_type == DataType.BAR_D:
            column = self.Column.First_D
        else:
            assert False, "WTF???"

        if dt is not None:
            self.setText(column, dt.strftime("%Y-%m-%d"))
            logger.info(f"  - received first date for {self} -> {dt}")
        else:
            self.setText(column, "None")

    # }}}
    @QtCore.pyqtSlot()  # __threadFinished{{{
    def __threadFinished(self):
        logger.debug(f"{self.__class__.__name__}.__threadFinished()")
        self.thread = None
        self.btn_download.setEnabled(True)

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
            item = _Item(i, parent=self)
            self.addTopLevelItem(item)

    # }}}
    def selectedInstruments(self) -> list[Instrument]:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectedInstruments()")

        selected = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.checkState(_Item.Column.Ticker) == Qt.CheckState.Checked:
                selected.append(item.instrument)
        return selected

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # set header labels
        labels = list()
        for l in _Item.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)

        # set sizes
        self.setColumnWidth(_Item.Column.Ticker, 100)
        self.setColumnWidth(_Item.Column.Name, 300)
        self.setColumnWidth(_Item.Column.First_1M, 100)
        self.setColumnWidth(_Item.Column.First_D, 100)
        self.setMinimumWidth(620)
        self.setMinimumHeight(400)

        # other options
        self.setSortingEnabled(True)
        self.sortByColumn(_Item.Column.Ticker, Qt.SortOrder.AscendingOrder)

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
        vbox.addWidget(SubTitle("Request first date", self))
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
        vbox.addWidget(SubTitle("Select timeframes", self))
        vbox.addWidget(self.__timeframes_bar)

        vbox.addWidget(Spacer(height=16))
        vbox.addWidget(SubTitle("Select period", self))
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


...
...
...


# old code -------------------------------------------------------------------
class DialogDataDownload(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__configSpinBox()
        self.__connect()
        self.__loadAssetLists()
        self.__initUI()
        self.thread = None

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tree = Tree(self)
        self.btn_help = ToolButton(Icon.HELP)
        self.btn_upd_list = ToolButton(Icon.UPDATE)
        self.btn_cancel = ToolButton(Icon.CANCEL)
        self.combobox_list = QtWidgets.QComboBox(self)
        self.btn_download = QtWidgets.QPushButton("Download")
        self.btn_update = QtWidgets.QPushButton("Update")
        self.btn_first = QtWidgets.QPushButton("Refresh", self)
        self.btn_last = QtWidgets.QPushButton("Refresh", self)
        self.first_availible = QtWidgets.QCheckBox("From first availible")
        self.begin_year = QtWidgets.QSpinBox(self)
        self.end_year = QtWidgets.QSpinBox(self)
        self.checkbox_1M = QtWidgets.QCheckBox("1M", self)
        self.checkbox_10M = QtWidgets.QCheckBox("10M", self)
        self.checkbox_1H = QtWidgets.QCheckBox("1H", self)
        self.checkbox_D = QtWidgets.QCheckBox("D", self)
        self.checkbox_W = QtWidgets.QCheckBox("W", self)
        self.checkbox_M = QtWidgets.QCheckBox("M", self)
        self.info_label = QtWidgets.QLabel(
            "If you have downloaded data\n"
            "and want to get new candles\n"
            "from a previous date, click\n"
            "the 'Update' button"
        )

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox_top_btn = QtWidgets.QHBoxLayout()
        hbox_top_btn.addStretch()
        hbox_top_btn.addWidget(self.btn_help)
        hbox_top_btn.addWidget(self.btn_cancel)
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.checkbox_1M, 0, 0)
        grid.addWidget(self.checkbox_10M, 1, 0)
        grid.addWidget(self.checkbox_1H, 2, 0)
        grid.addWidget(self.checkbox_D, 0, 1)
        grid.addWidget(self.checkbox_W, 1, 1)
        grid.addWidget(self.checkbox_M, 2, 1)
        timeframes = QtWidgets.QGroupBox("Timeframe:")
        timeframes.setLayout(grid)
        form = QtWidgets.QFormLayout()
        form.addRow(hbox_top_btn)
        form.addRow(HLine(self))
        form.addRow(" ", QtWidgets.QLabel(" "))
        form.addRow("Asset list", self.combobox_list)
        form.addRow("First date", self.btn_first)
        form.addRow("Last date", self.btn_last)
        form.addRow(self.first_availible)
        form.addRow("Begin", self.begin_year)
        form.addRow("End", self.end_year)
        form.addRow(timeframes)
        form.addRow(self.btn_download)
        form.addRow(self.info_label)
        form.addRow(self.btn_update)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.tree)
        hbox.addLayout(form)
        self.setLayout(hbox)

    # }}}
    def __configSpinBox(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__configSpinBox()")
        self.setWindowTitle("Download Tinkoff data")
        now_year = date.today().year
        first_year = 1997
        self.begin_year.setMinimum(first_year)
        self.begin_year.setMaximum(now_year)
        self.begin_year.setValue(first_year)
        self.end_year.setMinimum(first_year)
        self.end_year.setMaximum(now_year)
        self.end_year.setValue(now_year)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_first.clicked.connect(self.__refreshFirstDate)
        self.btn_last.clicked.connect(self.__refreshLastDate)
        self.btn_download.clicked.connect(self.__onDownload)
        self.combobox_list.currentTextChanged.connect(self.__updateTree)
        self.first_availible.clicked.connect(self.__onFirstAvalible)

    # }}}
    def __loadAssetLists(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadAssetLists()")
        path = Cmd.join(Res.DATA, _MoexData.DIR_NAME)
        files = Cmd.getFiles(path, full_path=False)
        for file in files:
            name = Cmd.name(file)
            self.combobox_list.addItem(name)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")
        self.first_availible.setChecked(True)
        self.begin_year.setEnabled(False)

    # }}}
    def __getSelectedShares(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__getSelectedShares()")
        shares_items = self.tree.getSelected()
        return shares_items

    # }}}
    def __getSelectedTimeframes(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__getSelectedTimeframes()")
        tf_list = list()
        if self.checkbox_1M.isChecked():
            tf_list.append(TimeFrame("1M"))
        if self.checkbox_10M.isChecked():
            tf_list.append(TimeFrame("10M"))
        if self.checkbox_1H.isChecked():
            tf_list.append(TimeFrame("1H"))
        if self.checkbox_D.isChecked():
            tf_list.append(TimeFrame("D"))
        if self.checkbox_W.isChecked():
            tf_list.append(TimeFrame("W"))
        if self.checkbox_M.isChecked():
            tf_list.append(TimeFrame("M"))
        if len(tf_list) == 0:
            logger.warning("No selected timeframes")
        return tf_list

    # }}}
    def __getBeginYear(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__getBeginYear()")
        if self.first_availible.isChecked():
            return None
        else:
            return self.begin_year.value()

    # }}}
    def __getEndYear(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__getEndYear()")
        return self.end_year.value()

    # }}}
    @QtCore.pyqtSlot()  # __threadFinished{{{
    def __threadFinished(self):
        logger.debug(f"{self.__class__.__name__}.__threadFinished()")
        self.thread = None
        self.btn_download.setEnabled(True)

    # }}}
    @QtCore.pyqtSlot()  # __updateTree{{{
    def __updateTree(self):
        logger.debug(f"{self.__class__.__name__}.__updateTree()")
        self.tree.clear()
        list_name = self.combobox_list.currentText()
        list_path = Cmd.join(
            Res.DATA, _MoexData.DIR_NAME, f"{list_name}.json"
        )
        slist = _MoexData.loadSharesList(list_path)
        self.tree.setSharesList(slist)

    # }}}
    @QtCore.pyqtSlot()  # __onFirstAvalible{{{
    def __onFirstAvalible(self):
        logger.debug(f"{self.__class__.__name__}.__onFirstAvalible()")
        if self.first_availible.isChecked():
            self.begin_year.setEnabled(False)
        else:
            self.begin_year.setEnabled(True)

    # }}}
    @QtCore.pyqtSlot()  # __refreshFirstDate{{{
    def __refreshFirstDate(self):
        logger.debug(f"{self.__class__.__name__}.__refreshFirstDate()")
        if self.thread is not None:
            Dialog.info("Data manager is busy now, wait for complete task")
            return
        md = _MoexData()
        self.thread = TGetFirsDate(md, self.tree)
        self.thread.finished.connect(self.__threadFinished)
        self.thread.start()

    # }}}
    @QtCore.pyqtSlot()  # __refreshLastDate{{{
    def __refreshLastDate(self):
        logger.debug(f"{self.__class__.__name__}.__refreshLastDate()")
        if self.thread is not None:
            Dialog.info("Data manager is busy now, wait for complete task")
            return
        md = _MoexData()
        self.thread = TGetLastDate(md, self.tree)
        self.thread.finished.connect(self.__threadFinished)
        self.thread.start()

    # }}}
    @QtCore.pyqtSlot()  # __onDownload{{{
    def __onDownload(self):
        logger.debug(f"{self.__class__.__name__}.__onDownload()")
        shares = self.__getSelectedShares()
        if len(shares) == 0:
            Dialog.info("No selected shares! Check share for download")
            return
        timeframe_list = self.__getSelectedTimeframes()
        begin = self.__getBeginYear()
        end = self.__getEndYear()
        md = _MoexData()
        self.thread = TDownload(md, shares, timeframe_list, begin, end)
        self.thread.finished.connect(self.__threadFinished)
        self.thread.start()
        self.btn_download.setEnabled(False)


# }}}


# }}}
class DialogDataConvert(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}
    def __createWidgets(self):  # {{{
        self.groupbox_timeframe = QtWidgets.QGroupBox("TimeFrame")
        self.checkbox_1M = QtWidgets.QCheckBox("1M")
        self.checkbox_5M = QtWidgets.QCheckBox("5M")
        self.checkbox_1H = QtWidgets.QCheckBox("1H")
        self.checkbox_D = QtWidgets.QCheckBox("D")
        self.btn_convert = QtWidgets.QPushButton("Convert")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    # }}}
    def __createLayots(self):  # {{{
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_convert)
        h_btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.checkbox_1M)
        vbox.addWidget(self.checkbox_5M)
        vbox.addWidget(self.checkbox_1H)
        vbox.addWidget(self.checkbox_D)
        vbox.addLayout(h_btn_box)
        self.setLayout(vbox)

    # }}}
    def __config(self):  # {{{
        self.setWindowTitle("Convert data")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __connect(self):  # {{{
        self.btn_convert.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    # }}}
    def exec(self):  # {{{
        result = super().exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            timeframe_list = list()
            if self.checkbox_1M.isChecked():
                timeframe_list.append(TimeFrame("1M"))
            if self.checkbox_5M.isChecked():
                timeframe_list.append(TimeFrame("5M"))
            if self.checkbox_1H.isChecked():
                timeframe_list.append(TimeFrame("1H"))
            if self.checkbox_D.isChecked():
                timeframe_list.append(TimeFrame("D"))
            return timeframe_list
        else:
            logger.info("Cancel convert")
            return False


# }}}


# }}}
class DialogDataDelete(QtWidgets.QDialog):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}
    def __createWidgets(self):  # {{{
        self.btn_delete = QtWidgets.QPushButton("Delete")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    # }}}
    def __createLayots(self):  # {{{
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_delete)
        h_btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(h_btn_box)
        self.setLayout(vbox)

    # }}}
    def __config(self):  # {{{
        self.setWindowTitle("Delete data")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __connect(self):  # {{{
        self.btn_delete.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    # }}}
    def exec(self):  # {{{
        result = super().exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            return True
        else:
            logger.info("Cancel delete")
            return False


# }}}


# }}}


class TGetFirsDate(QtCore.QThread):  # {{{
    def __init__(self, md, tree, parent=None):  # {{{
        QtCore.QThread.__init__(self, parent)
        self.moex = md
        self.tree = tree

    # }}}
    def run(self):  # {{{
        logger.info(":: Receiving first date")
        for i in self.tree:
            # i.updateFirstDate()
            ticker = i.ticker
            dt = self.moex.getFirstDatetime(ticker)
            if dt is not None:
                dt = dt.strftime("%Y-%m-%d %H:%M")
                i.setText(Tree.Column.FIRST_DATE, dt)
                logger.info(f"  - received first date for {ticker} -> {dt}")
            else:
                i.setText(Tree.Column.FIRST_DATE, "None")
        logger.info("Receive complete!")


# }}}


# }}}
class TGetLastDate(QtCore.QThread):  # {{{
    def __init__(self, md, tree, parent=None):  # {{{
        QtCore.QThread.__init__(self, parent)
        self.moex = md
        self.tree = tree

    # }}}
    def run(self):  # {{{
        logger.info(":: Checkin last date")
        for i in self.tree:
            # i.updateFirstDate()
            ticker = i.ticker
            dt = self.moex.getLastDatetime(ticker)
            if dt is not None:
                dt = dt.strftime("%Y-%m-%d %H:%M")
                i.setText(Tree.Column.LAST_DATE, dt)
                i.setCheckState(Tree.Column.SECID, Qt.CheckState.Checked)
            else:
                i.setText(Tree.Column.LAST_DATE, "None")
        logger.info("Chekin complete!")


# }}}


# }}}
class TDownload(QtCore.QThread):  # {{{
    def __init__(
        self, md, shares, timeframe_list, begin, end, parent=None
    ):  # {{{
        QtCore.QThread.__init__(self, parent)
        self.moex = md
        self.shares = shares
        self.timeframe_list = timeframe_list
        self.begin = begin
        self.end = end

    # }}}
    def run(self):  # {{{
        logger.info(":: Start download data")
        for i in self.shares:
            for timeframe in self.timeframe_list:
                ticker = i.ticker
                if self.begin is None:
                    self.begin = self.moex.getFirstDatetime(ticker).year
                year = self.begin
                while year <= self.end:
                    self.moex.download(ticker, timeframe, year)
                    year += 1
        logger.info("Download complete!")


# }}}


# }}}
class TConvert(QtCore.QThread):  # {{{
    def __init__(self, md, timeframe_list, parent=None):  # {{{
        QtCore.QThread.__init__(self, parent)
        self.timeframe_list = timeframe_list
        self.moex = md

    # }}}
    def run(self):  # {{{
        logger.info(":: Start convert data")
        path = Cmd.join(Res.DOWNLOAD, _MoexData.DIR_NAME)
        asset_dirs = Cmd.getDirs(path, full_path=True)
        for dir_path in asset_dirs:
            for timeframe in self.timeframe_list:
                self.moex.export(dir_path, timeframe)
        logger.info("Convert complete!")


# }}}


# }}}
class TDelete(QtCore.QThread):  # {{{
    def __init__(self, md, parent=None):  # {{{
        QtCore.QThread.__init__(self, parent)
        self.moex = md

    # }}}
    def run(self):  # {{{
        logger.info(":: Delete moex data")
        self.moex.deleteMoexData()
        logger.info("Delete complete!")


# }}}


# }}}


class MoexMenu(QtWidgets.QMenu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        QtWidgets.QMenu.__init__(self, parent)
        self.__createActions()
        self.__createDialogs()
        self.__connect()
        self.thread = None

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.download = QtGui.QAction(Icon.DOWNLOAD, "Download", self)
        self.convert = QtGui.QAction(Icon.CONVERT, "Convert", self)
        self.delete = QtGui.QAction(Icon.THRASH, "Delete", self)
        self.update = QtGui.QAction(Icon.UPDATE, "Update", self)
        self.addAction(self.download)
        self.addAction(self.convert)
        self.addAction(self.delete)
        self.addAction(self.update)

    # }}}
    def __createDialogs(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createDialogs()")
        self.download_dialog = DialogDataDownload()
        self.convert_dialog = DialogDataConvert()
        self.delete_dialog = DialogDataDelete()
        self.download_dialog.hide()
        self.convert_dialog.hide()
        self.delete_dialog.hide()

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.download.triggered.connect(self.__onDownload)
        self.convert.triggered.connect(self.__onConvert)
        self.delete.triggered.connect(self.__onDelete)
        self.update.triggered.connect(self.__onUpdate)

    # }}}
    @QtCore.pyqtSlot()  # __threadFinished{{{
    def __threadFinished(self):
        self.thread = None

    # }}}
    @QtCore.pyqtSlot()  # __onDownload{{{
    def __onDownload(self):
        logger.debug(f"{self.__class__.__name__}.download")
        self.download_dialog.exec()

    # }}}
    @QtCore.pyqtSlot()  # __onConvert{{{
    def __onConvert(self):
        logger.debug(f"{self.__class__.__name__}.__convert")
        timeframe_list = self.convert_dialog.exec()
        if not timeframe_list:
            return
        elif self.thread is not None:
            self.info_dialog.info(
                "Data manager is busy now, wait for complete task"
            )
        else:
            md = _MoexData()
            self.thread = TConvert(md, timeframe_list)
            self.thread.finished.connect(self.__threadFinished)
            self.thread.start()

    # }}}
    @QtCore.pyqtSlot()  # __onDelete{{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.delete")
        result = self.delete_dialog.exec()
        if not result:
            return
        elif self.thread is not None:
            self.info_dialog.info(
                "Data manager is busy now, wait for complete task"
            )
        else:
            md = _MoexData()
            self.thread = TDelete(md)
            self.thread.finished.connect(self.__threadFinished)
            self.thread.start()

    # }}}
    @QtCore.pyqtSlot()  # __onUpdate{{{
    def __onUpdate(self):
        logger.debug(f"{self.__class__.__name__}.update")
        logger.info("Update from MOEX not availible now. Cancel update.")
        return
        # if not self.update_dialog.exec():
        #     return
        # elif self.thread is not None:
        #     self.info_dialog.info(
        #         f"Data manager is busy now, wait for complete task"
        #         )
        # else:
        #     self.scout = Scout()
        #     self.thread = TUpdate(self.scout)
        #     self.thread.finished.connect(self.__threadFinished)
        #     self.thread.start()


# }}}
# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = DialogDataDownload()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())
