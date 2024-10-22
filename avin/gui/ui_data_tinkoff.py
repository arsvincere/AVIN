#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import os
import enum
import asyncio
import logging
import time as timer
from datetime import date, time, timedelta, datetime
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from avin.const import DATA_DIR, DOWNLOAD_DIR
from avin.core import TinkoffData, Data, TimeFrame
from avin.company import Scout
from avin.utils import Cmd
from avin.gui.custom import Font, Icon, Palette, Dialog
from avin.gui.asset import AssetWidget
logger = logging.getLogger("LOGGER")

class TDownload(QtCore.QThread):
    def __init__(self, tinkoff, alist, from_year, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.alist = alist
        self.from_year = from_year
        self.tinkoff = tinkoff

    def run(self):
        logger.info(f":: Start download data")
        for asset in self.alist:
            self.tinkoff.download(asset, self.from_year)
        logger.info("Download complete!")


class TExtract(QtCore.QThread):
    def __init__(self, tinkoff, dir_path, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.dir_path = dir_path
        self.tinkoff = tinkoff

    def run(self):
        logger.info(f":: Start extract archives")
        files = sorted(Cmd.getFiles(self.dir_path, full_path=True))
        files = Cmd.select(files, ".zip")
        for file in files:
            self.tinkoff.extractArchive(file)
        logger.info("Extract complete!")


class TConvert(QtCore.QThread):
    def __init__(self, tinkoff, timeframe_list, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.timeframe_list = timeframe_list
        self.tinkoff = tinkoff

    def __export(self, dir_path):
        for timeframe in self.timeframe_list:
            self.tinkoff.exportData(dir_path, timeframe)

    def run(self):
        logger.info(f":: Start convert data")
        path = Cmd.join(DOWNLOAD_DIR, TinkoffData.DIR_NAME)
        dirs = Cmd.getDirs(path, full_path=True)
        for i in dirs:
            self.__export(i)
        logger.info("Convert complete!")


class TDelete(QtCore.QThread):
    def __init__(self, td, tinkoff_archives, tinkoff_data, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.td = td
        self.tinkoff_archives = tinkoff_archives
        self.tinkoff_data = tinkoff_data

    def run(self):
        if self.tinkoff_archives:
            logger.info(f":: Delete tinkoff archives")
            self.td.deleteArchives()
            logger.info(f"Delete complete!")
        if self.tinkoff_data:
            logger.info(f":: Delete tinkoff data")
            self.td.deleteTinkoffData()
            logger.info(f"Delete complete!")


class TUpdate(QtCore.QThread):
    def __init__(self, scout, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.scout = scout

    def run(self):
        logger.info(f":: Start update data")
        dirs = Data.getAllDataDirs()
        for dir_path in dirs:
            asset_path = Cmd.join(dir_path, "asset")
            timeframe_path = Cmd.join(dir_path, "timeframe")
            if Cmd.isExist(asset_path) and Cmd.isExist(timeframe_path):
                asset = Data.loadAsset(asset_path)
                timeframe = Data.loadTimeFrame(timeframe_path)
                self.scout.updateData(asset, timeframe)
        logger.info("Update complete!")



class DialogDataDownload(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.widget_asset = AssetWidget(self)
        self.spinbox_begin = QtWidgets.QSpinBox(self)
        self.spinbox_end = QtWidgets.QSpinBox(self)
        self.btn_download = QtWidgets.QPushButton("Download")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    def __createLayots(self):
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_download)
        h_btn_box.addWidget(self.btn_cancel)
        form = QtWidgets.QFormLayout()
        form.addRow("Begin year",       self.spinbox_begin)
        form.addRow("End year",         self.spinbox_end)
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.widget_asset, 0, 0, 2, 1)
        grid.addLayout(form, 0, 1)
        grid.addLayout(h_btn_box, 1, 1)
        self.setLayout(grid)

    def __config(self):
        self.setWindowTitle("Download Tinkoff data")
        year = date.today().year
        self.spinbox_begin.setMinimum(2017)
        self.spinbox_begin.setMaximum(year)
        self.spinbox_begin.setValue(2017)
        self.spinbox_end.setMinimum(2017)
        self.spinbox_end.setMaximum(year)
        self.spinbox_end.setValue(year)
        self.spinbox_end.setEnabled(False)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_download.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def exec(self):
        result = super().exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            alist = self.widget_asset.currentList()
            from_year = self.spinbox_begin.value()
            return alist, from_year
        else:
            logger.info(f"Cancel download")
            return False, False


class DialogDataExtract(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.btn_extract = QtWidgets.QPushButton("Extract")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    def __createLayots(self):
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_extract)
        h_btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(h_btn_box)
        self.setLayout(vbox)

    def __config(self):
        self.setWindowTitle("Extract archives")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_extract.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def exec(self):
        result = super().exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            return True
        else:
            logger.info(f"Cancel extract")
            return False


class DialogDataConvert(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.groupbox_timeframe = QtWidgets.QGroupBox("TimeFrame")
        self.checkbox_1M = QtWidgets.QCheckBox("1M")
        self.checkbox_5M = QtWidgets.QCheckBox("5M")
        self.checkbox_1H = QtWidgets.QCheckBox("1H")
        self.checkbox_D = QtWidgets.QCheckBox("D")
        self.btn_convert = QtWidgets.QPushButton("Convert")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    def __createLayots(self):
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

    def __config(self):
        self.setWindowTitle("Convert data")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_convert.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def exec(self):
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
            logger.info(f"Cancel convert")
            return False


class DialogDataDelete(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.checkbox_archive = QtWidgets.QCheckBox("Archives")
        self.checkbox_tinkoff = QtWidgets.QCheckBox("Tinkoff data")
        self.btn_delete = QtWidgets.QPushButton("Delete")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    def __createLayots(self):
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_delete)
        h_btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.checkbox_archive)
        vbox.addWidget(self.checkbox_tinkoff)
        vbox.addLayout(h_btn_box)
        self.setLayout(vbox)

    def __config(self):
        self.setWindowTitle("Delete data")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_delete.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def exec(self):
        result = super().exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            archives =  self.checkbox_archive.isChecked()
            tinkoff =   self.checkbox_tinkoff.isChecked()
            return archives, tinkoff
        else:
            logger.info(f"Cancel delete")
            return False, False


class DialogDataUpdate(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.btn_extract = QtWidgets.QPushButton("Update")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    def __createLayots(self):
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_extract)
        h_btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(h_btn_box)
        self.setLayout(vbox)

    def __config(self):
        self.setWindowTitle("Update user data")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_extract.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def __selectUserData(self, item):
        logger.debug(f"{self.__class__.__name__}.__selectUserData()")
        for i in range(item.childCount()):
            child = item.child(i)
            if child.type == Tree.Type.DIR:
                self.__selectUserData(child)
            if child.type == Tree.Type.DATA:
                self.selected.append(child)

    def exec(self):
        result = super().exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            return True
        else:
            logger.info(f"Cancel update")
            return False



class TinkoffMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init()")
        QtWidgets.QMenu.__init__(self, parent)
        self.__createActions()
        self.__createDialogs()
        self.__connect()
        self.thread = None

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.download = QtGui.QAction(Icon.DOWNLOAD, "Download", self)
        self.extract = QtGui.QAction(Icon.EXTRACT, "Extract", self)
        self.convert = QtGui.QAction(Icon.CONVERT, "Convert", self)
        self.delete = QtGui.QAction(Icon.THRASH, "Delete", self)
        self.update = QtGui.QAction(Icon.UPDATE, "Update", self)
        self.addAction(self.download)
        self.addAction(self.extract)
        self.addAction(self.convert)
        self.addAction(self.delete)
        self.addAction(self.update)

    def __createDialogs(self):
        logger.debug(f"{self.__class__.__name__}.__createDialogs()")
        self.download_dialog = DialogDataDownload()
        self.extract_dialog = DialogDataExtract()
        self.convert_dialog = DialogDataConvert()
        self.delete_dialog = DialogDataDelete()
        self.update_dialog = DialogDataUpdate()
        self.download_dialog.hide()
        self.extract_dialog.hide()
        self.convert_dialog.hide()
        self.delete_dialog.hide()
        self.update_dialog.hide()

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.download.triggered.connect(self.__onDownload)
        self.extract.triggered.connect(self.__onExtract)
        self.convert.triggered.connect(self.__onConvert)
        self.delete.triggered.connect(self.__onDelete)
        self.update.triggered.connect(self.__onUpdate)

    @QtCore.pyqtSlot()  #__threadFinished
    def __threadFinished(self):
        self.thread = None

    @QtCore.pyqtSlot()  #__onDownload
    def __onDownload(self):
        logger.debug(f"{self.__class__.__name__}.download")
        alist, year = self.download_dialog.exec()
        if not alist:
            return
        elif self.thread is not None:
            Dialog.info(f"Data manager is busy now, wait for complete task")
        else:
            tinkoff = TinkoffData()
            self.thread = TDownload(tinkoff, alist, year)
            self.thread.finished.connect(self.__threadFinished)
            self.thread.start()

    @QtCore.pyqtSlot()  #__onExtract
    def __onExtract(self):
        logger.debug(f"{self.__class__.__name__}.extract")
        if not self.extract_dialog.exec():
            return
        elif self.thread is not None:
            self.info_dialog.info(
                f"Data manager is busy now, wait for complete task"
                )
        else:
            td = TinkoffData()
            dir_path = Cmd.join(DOWNLOAD_DIR, TinkoffData.DIR_NAME)
            self.thread = TExtract(td, dir_path)
            self.thread.finished.connect(self.__threadFinished)
            self.thread.start()

    @QtCore.pyqtSlot()  #__onConvert
    def __onConvert(self):
        logger.debug(f"{self.__class__.__name__}.__convert")
        timeframe_list = self.convert_dialog.exec()
        if not timeframe_list:
            return
        elif self.thread is not None:
            self.info_dialog.info(
                f"Data manager is busy now, wait for complete task"
                )
        else:
            td = TinkoffData()
            self.thread = TConvert(td, timeframe_list)
            self.thread.finished.connect(self.__threadFinished)
            self.thread.start()

    @QtCore.pyqtSlot()  #__onDelete
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.delete")
        archives, tinkoff = self.delete_dialog.exec()
        if not (archives or tinkoff):
            return
        elif self.thread is not None:
            self.info_dialog.info(
                f"Data manager is busy now, wait for complete task"
                )
        else:
            td = TinkoffData()
            self.thread = TDelete(td, archives, tinkoff)
            self.thread.finished.connect(self.__threadFinished)
            self.thread.start()

    @QtCore.pyqtSlot()  #__onUpdate
    def __onUpdate(self):
        logger.debug(f"{self.__class__.__name__}.update")
        if not self.update_dialog.exec():
            return
        elif self.thread is not None:
            self.info_dialog.info(
                f"Data manager is busy now, wait for complete task"
                )
        else:
            self.scout = Scout()
            self.thread = TUpdate(self.scout)
            self.thread.finished.connect(self.__threadFinished)
            self.thread.start()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = DataWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())

