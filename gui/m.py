#!/usr/bin/env  python3

import asyncio
import sys

import PyQt6
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from qasync import QApplication, QEventLoop, asyncClose, asyncSlot

from gui.data.ui_data_widget import DataWidget


class MainWindow(QWidget):  # {{{
    def __init__(self):
        super().__init__()

        self.setLayout(QVBoxLayout())
        self.lbl_status = QLabel("Idle", self)
        self.layout().addWidget(self.lbl_status)

    @asyncClose
    async def closeEvent(self, event):
        pass

    @asyncSlot()
    async def onMyEvent(self):
        pass


# }}}


def main():
    app = QApplication(sys.argv)

    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    w = DataWidget()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(PyQt6.QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()

    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())


if __name__ == "__main__":
    main()
