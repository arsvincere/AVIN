#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets

from avin.company import Tester


class Thread(QtCore.QThread):  # {{{
    def __init__(self, tester: Tester, test: ITest, parent=None):  # {{{
        QtCore.QThread.__init__(self, parent)
        self.tester = tester
        self.test = test
        self.tester.setTest(self.test)

    # }}}
    def run(self):  # {{{
        self.tester.runTest()


# }}}
# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TestWidget()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
