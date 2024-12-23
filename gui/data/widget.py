#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin import ONE_DAY, UTC, DateTime, Usr
from avin.utils import Cmd, logger
from gui.custom import Css, Dialog
from gui.data.download_dialog import DataDownloadDialog
from gui.data.item import DataInfoItem, InstrumentItem
from gui.data.thread import TConvert, TDelete, TDownload, Thread, TUpdate
from gui.data.toolbar import BarViewToolBar, DataToolBar
from gui.data.tree import BarViewTree, DataInfoTree


class DataDockWidget(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QDockWidget.__init__(self, "Data", parent)

        data_widget = DataWidget(self)
        self.setWidget(data_widget)
        self.setStyleSheet(Css.DOCK_WIDGET)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        feat = QtWidgets.QDockWidget.DockWidgetFeature
        self.setFeatures(
            feat.DockWidgetMovable
            | feat.DockWidgetClosable
            | feat.DockWidgetFloatable
        )

        # }}}


# }}}
class DataWidget(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__thread = None

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()
        self.__initUI()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.data_bar = DataToolBar(self)
        self.data_tree = DataInfoTree(self)

        self.view_bar = BarViewToolBar(self)
        self.view_tree = BarViewTree(self)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.data_bar)
        vbox.addWidget(self.data_tree)
        vbox.addWidget(self.view_bar)
        vbox.addWidget(self.view_tree)
        self.setLayout(vbox)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setStyleSheet(Css.STYLE)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.data_bar.download.triggered.connect(self.__onDownload)
        self.data_bar.convert.triggered.connect(self.__onConvert)
        self.data_bar.delete.triggered.connect(self.__onDelete)
        self.data_bar.update.triggered.connect(self.__onUpdate)
        self.data_tree.itemClicked.connect(self.__onItemClicked)

    # }}}
    def __initUI(self):  # {{{
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
    @QtCore.pyqtSlot()  # __onThreadFinish  # {{{
    def __onThreadFinish(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onThreadFinish()")

        logger.info(f"{self.__thread.name} complete!")
        self.__thread = None
        self.__updateTree()

    # }}}
    @QtCore.pyqtSlot()  # __updateTree  # {{{
    def __updateTree(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__updateTree()")

        data_info = Thread.info()
        self.data_tree.clear()
        if data_info is not None:
            self.data_tree.add(data_info)

    # }}}
    @QtCore.pyqtSlot()  # __onDownload  # {{{
    def __onDownload(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onDownload()")

        if self.__isBusy():
            return

        dialog = DataDownloadDialog()
        result = dialog.exec()

        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return

        source = dialog.currentSource()
        instruments = dialog.selectedInstruments()
        if not instruments:
            Dialog.error("No selected instruments, download canceled.")

        timeframes = dialog.selectedTimeframes()
        if not timeframes:
            Dialog.error("No selected timeframes, download canceled.")

        begin = dialog.beginYear()
        end = dialog.endYear()

        self.__thread = TDownload(source, instruments, timeframes, begin, end)
        self.__thread.finished.connect(self.__onThreadFinish)
        self.__thread.start()

    # }}}
    @QtCore.pyqtSlot()  # __onConvert  # {{{
    def __onConvert(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onConvert()")

        if self.__isBusy():
            return

        # TODO: convert dialog, item, tree...
        # а пока просто сам .csv файл открываю напрямую на редактирование
        file_path = Cmd.path(Usr.DATA, "convert_list.csv")
        command = (
            Usr.TERMINAL,
            *Usr.OPT,
            Usr.EXEC,
            Usr.EDITOR,
            file_path,
        )
        Cmd.subprocess(command)

        # TODO:
        # do convert only when
        # result = dialog_convert.exec()
        if not Dialog.confirm("Execute all convertion task?"):
            return

        # converting all task from "usr/data/convert_list.csv"
        self.__thread = TConvert("convert_list")
        self.__thread.finished.connect(self.__onThreadFinish)
        self.__thread.start()

    # }}}
    @QtCore.pyqtSlot()  # __onDelete  # {{{
    def __onDelete(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onDelete()")

        if self.__isBusy():
            return

        data_info = self.data_tree.selectedData()

        self.__thread = TDelete(data_info)
        self.__thread.finished.connect(self.__onThreadFinish)
        self.__thread.start()

    # }}}
    @QtCore.pyqtSlot()  # __onUpdate  # {{{
    def __onUpdate(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onUpdate()")

        if self.__isBusy():
            return

        data_info = self.data_tree.selectedData()

        self.__thread = TUpdate(data_info)
        self.__thread.finished.connect(self.__onThreadFinish)
        self.__thread.start()

    # }}}

    @QtCore.pyqtSlot()  # __onItemClicked  # {{{
    def __onItemClicked(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onItemClicked()")

        item = self.data_tree.currentItem()
        if isinstance(item, InstrumentItem):
            return

        if not isinstance(item, DataInfoItem):
            assert False, "WTF, жизнь меня к этому не готовила"

        # for DataInfoItem
        instrument = item.info.instrument
        data_type = item.info.data_type

        if data_type.toTimeDelta() < ONE_DAY:
            self.view_bar.showMonthSelector()
            year = self.view_bar.currentYear()
            month = self.view_bar.currentMonth()
            begin = DateTime(year, month, 1, tzinfo=UTC)
            end = DateTime(year, month + 1, 1, tzinfo=UTC)
            records = Thread.requestData(instrument, data_type, begin, end)
        else:
            self.view_bar.hideMonthSelector()
            year = self.view_bar.currentYear()
            begin = DateTime(year, 1, 1, tzinfo=UTC)
            end = DateTime(year + 1, 1, 1, tzinfo=UTC)
            records = Thread.requestData(instrument, data_type, begin, end)

        self.view_tree.setData(records)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = DataWidget()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
