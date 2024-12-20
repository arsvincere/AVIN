#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import logging
from datetime import datetime, date, time
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
logger = logging.getLogger("LOGGER")


"""
Надо подумать как мою позицию отображать.
Где граница -
    брокер
        - ордеры
        - операции
        - позиции
        - детайлед портфолио
    авин
        ордеры
        операции
        позиции

- [ ] возможное решение: моя логика работает и создает свои объекты
    после взаимодействия с брокером получает брокерский респонс
    и сохраняет его в мета информацию к себе и все...
    нет..

    брокер у меня уже возвращает мои объекты.
    Надо просто к ним прикрепить мета.

    Виджеты операции ордера и портфолио - которые сейчас строятся
    из информации от брокера - пусть так и остаются - это в сумме
    виджет АККАУНТ
        - ордера
        - операции
        - портфолио
        - детайлед портфолио


"""




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = UOrderType()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.showMaximized()
    w.show()
    sys.exit(app.exec())

