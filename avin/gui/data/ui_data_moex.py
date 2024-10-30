#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
import enum
import logging
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
from datetime import date, time, timedelta, datetime
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from avin.const import RES_DIR, MSK_TIME_DIF, DOWNLOAD_DIR
from avin.core import MoexData, TimeFrame, Data, Share
from avin.utils import Cmd, now
from avin.gui.custom import (
    Font, Icon, Palette, Dialog, HLine, ToolButton, Spacer
    )
logger = logging.getLogger("LOGGER")

class TGetFirsDate(QtCore.QThread):
    def __init__(self, md, tree, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.moex = md
        self.tree = tree

    def run(self):
        logger.info(f":: Receiving first date")
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
        logger.info(f"Receive complete!")


class TGetLastDate(QtCore.QThread):
    def __init__(self, md, tree, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.moex = md
        self.tree = tree

    def run(self):
        logger.info(f":: Checkin last date")
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
        logger.info(f"Chekin complete!")


class TDownload(QtCore.QThread):
    def __init__(self, md, shares, timeframe_list, begin, end, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.moex = md
        self.shares = shares
        self.timeframe_list = timeframe_list
        self.begin = begin
        self.end = end

    def run(self):
        logger.info(f":: Start download data")
        for i in self.shares:
            for timeframe in self.timeframe_list:
                ticker = i.ticker
                if self.begin is None:
                    self.begin = self.moex.getFirstDatetime(ticker).year
                year = self.begin
                while year <= self.end:
                    self.moex.download(ticker, timeframe, year)
                    year += 1
        logger.info(f"Download complete!")


class TConvert(QtCore.QThread):
    def __init__(self, md, timeframe_list, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.timeframe_list = timeframe_list
        self.moex = md

    def run(self):
        logger.info(f":: Start convert data")
        path = Cmd.join(DOWNLOAD_DIR, MoexData.DIR_NAME)
        asset_dirs = Cmd.getDirs(path, full_path=True)
        for dir_path in asset_dirs:
            for timeframe in self.timeframe_list:
                self.moex.export(dir_path, timeframe)
        logger.info("Convert complete!")


class TDelete(QtCore.QThread):
    def __init__(self, md, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.moex = md

    def run(self):
        logger.info(f":: Delete moex data")
        self.moex.deleteMoexData()
        logger.info(f"Delete complete!")



class IShare(QtWidgets.QTreeWidgetItem):
    def __init__(self, dct, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable |
            # Qt.ItemFlag.ItemIsAutoTristate |
            # Qt.ItemFlag.ItemIsDragEnabled |
            # Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setCheckState(0, Qt.CheckState.Unchecked)
        self.setText(Tree.Column.SECID,     str(dct["SECID"]))
        self.setText(Tree.Column.SECNAME,   str(dct["SECNAME"]))

    @property  #ticker
    def ticker(self):
        logger.debug(f"{self.__class__.__name__}.ticker")
        return self.text(Tree.Column.SECID)

    def updateFirstDate(self):
        logger.debug(f"{self.__class__.__name__}.updateFirstDate()")
        dt = MoexData.get_first_date(self.ticker)
        if dt is not None:
            self.setText(Tree.Column.FIRST_DATE, dt.isoformat())
            logger.info(f"  - received first date for {self.ticker} -> {dt}")
        else:
            self.setText(Tree.Column.FIRST_DATE, "None")

    def updateLastDate(self):
        logger.debug(f"{self.__class__.__name__}.updateFirstDate()")
        assert False
        asset = Share(self.ticker)
        data = Data.loadLastData(asset, TimeFrame("1M"))
        dt = data.last_dt
        self.setText(Tree.Column.FIRST_DATE, str(dt))


class Tree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        SECID =                 enum.auto(0),
        SECNAME =               enum.auto(),
        FIRST_DATE =            enum.auto(),
        LAST_DATE =             enum.auto(),

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__connect()

    def __iter__(self):
        logger.debug(f"{self.__class__.__name__}.__iter__()")
        all_items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            all_items.append(item)
        return iter(all_items)

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(Tree.Column.SECID, Qt.SortOrder.AscendingOrder)
        self.setFont(Font.MONO)
        self.setColumnWidth(Tree.Column.SECID, 100)
        self.setColumnWidth(Tree.Column.SECNAME, 250)
        self.setColumnWidth(Tree.Column.FIRST_DATE, 150)
        self.setColumnWidth(Tree.Column.LAST_DATE, 150)
        self.setMinimumWidth(700)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")

    def getSelected(self):
        logger.debug(f"{self.__class__.__name__}.getSelected()")
        selected = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.checkState(Tree.Column.SECID) == Qt.CheckState.Checked:
                selected.append(item)
        return selected

    def setSharesList(self, slist):
        logger.debug(f"{self.__class__.__name__}.setSharesList()")
        for i in slist:
            item = IShare(i)
            self.addTopLevelItem(item)



class DialogDataDownload(QtWidgets.QDialog):
    def __init__(self, parent=None):
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

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __createWidgets(self):
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

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox_top_btn = QtWidgets.QHBoxLayout()
        hbox_top_btn.addStretch()
        hbox_top_btn.addWidget(self.btn_help)
        hbox_top_btn.addWidget(self.btn_cancel)
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.checkbox_1M,    0, 0)
        grid.addWidget(self.checkbox_10M,   1, 0)
        grid.addWidget(self.checkbox_1H,    2, 0)
        grid.addWidget(self.checkbox_D,     0, 1)
        grid.addWidget(self.checkbox_W,     1, 1)
        grid.addWidget(self.checkbox_M,     2, 1)
        timeframes = QtWidgets.QGroupBox("Timeframe:")
        timeframes.setLayout(grid)
        form = QtWidgets.QFormLayout()
        form.addRow(                    hbox_top_btn)
        form.addRow(                    HLine(self))
        form.addRow(" ",                QtWidgets.QLabel(" "))
        form.addRow("Asset list",       self.combobox_list)
        form.addRow("First date",       self.btn_first)
        form.addRow("Last date",        self.btn_last)
        form.addRow(                    self.first_availible)
        form.addRow("Begin",            self.begin_year)
        form.addRow("End",              self.end_year)
        form.addRow(                    timeframes)
        form.addRow(                    self.btn_download)
        form.addRow(                    self.info_label)
        form.addRow(                    self.btn_update)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.tree)
        hbox.addLayout(form)
        self.setLayout(hbox)

    def __configSpinBox(self):
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

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_first.clicked.connect(self.__refreshFirstDate)
        self.btn_last.clicked.connect(self.__refreshLastDate)
        self.btn_download.clicked.connect(self.__onDownload)
        self.combobox_list.currentTextChanged.connect(self.__updateTree)
        self.first_availible.clicked.connect(self.__onFirstAvalible)

    def __loadAssetLists(self):
        logger.debug(f"{self.__class__.__name__}.__loadAssetLists()")
        path = Cmd.join(RES_DIR, MoexData.DIR_NAME)
        files = Cmd.getFiles(path, full_path=False)
        for file in files:
            name = Cmd.name(file)
            self.combobox_list.addItem(name)

    def __initUI(self):
        logger.debug(f"{self.__class__.__name__}.__initUI()")
        self.first_availible.setChecked(True)
        self.begin_year.setEnabled(False)

    def __getSelectedShares(self):
        logger.debug(f"{self.__class__.__name__}.__getSelectedShares()")
        shares_items = self.tree.getSelected()
        return shares_items

    def __getSelectedTimeframes(self):
        logger.debug(f"{self.__class__.__name__}.__getSelectedTimeframes()")
        tf_list = list()
        if self.checkbox_1M.isChecked(): tf_list.append(TimeFrame("1M"))
        if self.checkbox_10M.isChecked(): tf_list.append(TimeFrame("10M"))
        if self.checkbox_1H.isChecked(): tf_list.append(TimeFrame("1H"))
        if self.checkbox_D.isChecked(): tf_list.append(TimeFrame("D"))
        if self.checkbox_W.isChecked(): tf_list.append(TimeFrame("W"))
        if self.checkbox_M.isChecked(): tf_list.append(TimeFrame("M"))
        if len(tf_list) == 0:
            logger.warning(f"No selected timeframes")
        return tf_list

    def __getBeginYear(self):
        logger.debug(f"{self.__class__.__name__}.__getBeginYear()")
        if self.first_availible.isChecked():
            return None
        else:
            return self.begin_year.value()

    def __getEndYear(self):
        logger.debug(f"{self.__class__.__name__}.__getEndYear()")
        return self.end_year.value()

    @QtCore.pyqtSlot()  #__threadFinished
    def __threadFinished(self):
        logger.debug(f"{self.__class__.__name__}.__threadFinished()")
        self.thread = None
        self.btn_download.setEnabled(True)

    @QtCore.pyqtSlot()  #__updateTree
    def __updateTree(self):
        logger.debug(f"{self.__class__.__name__}.__updateTree()")
        self.tree.clear()
        list_name = self.combobox_list.currentText()
        list_path = Cmd.join(RES_DIR, MoexData.DIR_NAME, f"{list_name}.json")
        slist = MoexData.loadSharesList(list_path)
        self.tree.setSharesList(slist)

    @QtCore.pyqtSlot()  #__onFirstAvalible
    def __onFirstAvalible(self):
        logger.debug(f"{self.__class__.__name__}.__onFirstAvalible()")
        if self.first_availible.isChecked():
            self.begin_year.setEnabled(False)
        else:
            self.begin_year.setEnabled(True)

    @QtCore.pyqtSlot()  #__refreshFirstDate
    def __refreshFirstDate(self):
        logger.debug(f"{self.__class__.__name__}.__refreshFirstDate()")
        if self.thread is not None:
            Dialog.info(f"Data manager is busy now, wait for complete task")
            return
        md = MoexData()
        self.thread = TGetFirsDate(md, self.tree)
        self.thread.finished.connect(self.__threadFinished)
        self.thread.start()

    @QtCore.pyqtSlot()  #__refreshLastDate
    def __refreshLastDate(self):
        logger.debug(f"{self.__class__.__name__}.__refreshLastDate()")
        if self.thread is not None:
            Dialog.info(f"Data manager is busy now, wait for complete task")
            return
        md = MoexData()
        self.thread = TGetLastDate(md, self.tree)
        self.thread.finished.connect(self.__threadFinished)
        self.thread.start()

    @QtCore.pyqtSlot()  #__onDownload
    def __onDownload(self):
        logger.debug(f"{self.__class__.__name__}.__onDownload()")
        shares = self.__getSelectedShares()
        if len(shares) == 0:
            Dialog.info("No selected shares! Check share for download")
            return
        timeframe_list = self.__getSelectedTimeframes()
        begin = self.__getBeginYear()
        end = self.__getEndYear()
        md = MoexData()
        self.thread = TDownload(md, shares, timeframe_list, begin, end)
        self.thread.finished.connect(self.__threadFinished)
        self.thread.start()
        self.btn_download.setEnabled(False)



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
        self.btn_delete = QtWidgets.QPushButton("Delete")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    def __createLayots(self):
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_delete)
        h_btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
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
            return True
        else:
            logger.info(f"Cancel delete")
            return False



class MoexMenu(QtWidgets.QMenu):
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
        self.convert = QtGui.QAction(Icon.CONVERT, "Convert", self)
        self.delete = QtGui.QAction(Icon.THRASH, "Delete", self)
        self.update = QtGui.QAction(Icon.UPDATE, "Update", self)
        self.addAction(self.download)
        self.addAction(self.convert)
        self.addAction(self.delete)
        self.addAction(self.update)

    def __createDialogs(self):
        logger.debug(f"{self.__class__.__name__}.__createDialogs()")
        self.download_dialog = DialogDataDownload()
        self.convert_dialog = DialogDataConvert()
        self.delete_dialog = DialogDataDelete()
        self.download_dialog.hide()
        self.convert_dialog.hide()
        self.delete_dialog.hide()

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.download.triggered.connect(self.__onDownload)
        self.convert.triggered.connect(self.__onConvert)
        self.delete.triggered.connect(self.__onDelete)
        self.update.triggered.connect(self.__onUpdate)

    @QtCore.pyqtSlot()  #__threadFinished
    def __threadFinished(self):
        self.thread = None

    @QtCore.pyqtSlot()  #__onDownload
    def __onDownload(self):
        logger.debug(f"{self.__class__.__name__}.download")
        self.download_dialog.exec()

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
            md = MoexData()
            self.thread = TConvert(md, timeframe_list)
            self.thread.finished.connect(self.__threadFinished)
            self.thread.start()

    @QtCore.pyqtSlot()  #__onDelete
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.delete")
        result = self.delete_dialog.exec()
        if not result:
            return
        elif self.thread is not None:
            self.info_dialog.info(
                f"Data manager is busy now, wait for complete task"
                )
        else:
            md = MoexData()
            self.thread = TDelete(md)
            self.thread.finished.connect(self.__threadFinished)
            self.thread.start()

    @QtCore.pyqtSlot()  #__onUpdate
    def __onUpdate(self):
        logger.debug(f"{self.__class__.__name__}.update")
        logger.info(f"Update from MOEX not availible now. Cancel update.")
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

