#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

import sys
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import pandas as pd
from datetime import datetime
from moexalgo import Market, Ticker
from avin.core import TimeFrame

class MoexDownloader():
    @staticmethod  #get_market_tools
    def get_all_shares() -> pd.DataFrame:
        market_tools = Market("stocks").tickers()
        df = pd.DataFrame(market_tools)
        return df

    def get_first_date(ticker: str) -> datetime:
        """ Receive first 1M candle from MOEX, and return his datetime """
        date_start = datetime(1900, 1, 1)
        share = Ticker(ticker)
        candles = share.candles(
            date=date_start,
            till_date="today",
            period="1m",
            limit=1,  #  candles count
            )
        candle = candles.send(None)
        dt = candle.begin
        return dt

    def get_candles(ticker, timeframe, begin, end="today", limit=5000):
        all_candles = list()
        candles = Ticker(ticker).candles(
            date=       begin,
            till_date=  end,
            period=     MoexDownloader.__convert(timeframe),
            limit=      limit,
        )
        return candles


    def __convert(obj: object):
        if isinstance(obj, TimeFrame):
            period = MoexDownloader.__convertTimeFrame(obj)
            return period

    def __convertTimeFrame(timeframe: TimeFrame):
        moex_period = {
            TimeFrame("1M"): "1m",
            TimeFrame("10M"): "10m",
            TimeFrame("1H"): "1h",
            TimeFrame("D"): "D",
            TimeFrame("W"): "W",
            TimeFrame("M"): "M",
            }
        return moex_period[timeframe]



    @staticmethod  #secid_candles
    def secid_candles(tuple_list, timeframe, period):
        # TODO: разделить на маленькие функции
        """Функция для скачивания исторических данных по акциям"""
        # Количество записей данных, полученных за один раз. Максимум 50000
        limit = 50000  # TODO: вынести в константы класса
        # ===Главный цикл последовательного сбора данных по каждой акции из списка===
        for SECID, FIRST_DATE in tuple_list:
            svech = 0
            date = datetime.strptime(FIRST_DATE, "%Y-%m-%d %H:%M:%S").replace(
                hour=0, minute=0, second=0
            )
            # дата конца диапазона выдачи данных - текущее время, в каждой акции
            # обновляем чтобы максимально свежее данные были, особенно минутки
            till_date = datetime.now().replace(microsecond=0)
            logger.info(f"Занимаемся акцией - '{SECID}'")
            # проверяем есть ли файл с котировками для данной акции, если нет - создаем
            # TODO: сделать подпапки для скачиваемых данных в виде:
            # TODO: <data_dir>/MOEX/SHARE/<ticker>/<timeframe>
            # TODO: файлы разбивать по годам
            filestocks_path = os.path.join(DATA_DIR, f"{SECID}-{period}.txt")
            if os.path.exists(filestocks_path):
                logger.info(
                    f"Файл '{filestocks_path}' для хранениния котировок"
                    f"акций '{SECID}' с таимфреймом {period} уже существует"
                )
                # читаем файл с котировками, смотрим не пустой ли,
                # если нет - вытаскиваем последнюю сохраненную дату
                with open(filestocks_path, "r", encoding="utf-8") as file:
                    reader = csv.reader(file)
                    row_count = sum(1 for row in reader)  # считаем количество строк
                    if row_count > 1:
                        # Перемещаем указатель файла в начало
                        file.seek(
                            0
                        )  # перемещаем указатель в начало иначе след строка вернет пустое значение
                        last_row = file.readlines()[-1]  # считываем последнюю строку
                        last_time = last_row.split("\t")[
                            0
                        ]  # берем первый элемент строки - дату
                        date = datetime.strptime(
                            last_time, "%Y-%m-%d %H:%M:%S"
                        )  # преобразуем str в datetime
                        logger.info(
                            f"Последние сохраненные данные от {date},"
                            f"в файле имеется {row_count} строк"
                        )
                    else:
                        logger.info(f"файл '{filestocks_path}' пустой")
            else:
                logger.info(
                    f"Файл {filestocks_path} для хранениния котировок акций '{SECID}'  с таимфреймом {period} отсутствует и будет создан после сбора данных"
                )
                # создаем пустой файл для котировок с заголовками в первой строке
                # TODO: сделать стандартный формат сохранения данных
                df_load = pd.DataFrame(
                    columns=[
                        "begin",
                        "end",
                        "open",
                        "high",
                        "low",
                        "close",
                        "value",
                        "volume",
                    ]
                )
                df_load.to_csv(
                    filestocks_path, mode="w", sep=";", index=False, header=True
                )
                # берем за начальную дату FIRST_DATE из tuple_list на основе
                # USER_FILE, т.к. ранее скачанных свечей не было
                # с проверкой не является ли FIRST_DATE пустым - последствие
                # обработки ошибки Мосбиржи, в частности для VEON-RX
                if FIRST_DATE != FIRST_DATE:
                    date = datetime.strptime("2020-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
                else:
                    date = datetime.strptime(FIRST_DATE, "%Y-%m-%d %H:%M:%S").replace(
                        hour=0, minute=0, second=0
                    )

            #  =====!качаем свечи!=====
            logger.info(
                f"Качаем свечи для акции '{SECID}' с таймфреймом {period} "
                f"начиная с {date}"
            )
            real_limit = limit
            # цикл до момента когда количество скачанных свечек не будет
            # меньше заданного limit
            while limit == real_limit:
                try:
                    df_load = Ticker(SECID).candles(
                        date=date, till_date=till_date, period=period, limit=limit
                    )
                # обработка ошибки, была на момент написания кода на акции VEON-RX
                except:
                    logger.warning(
                        f"Ошибка от Мосбиржи при получении данных акции {SECID}"
                        f"с таймфреймом {period}. Продолжаем сбор данных."
                    )
                    real_limit = 0
                    continue  # Переход к следующей итерации цикла

                # полученный <class 'generator'> преобразуем в DataFrame
                df_load = pd.DataFrame(
                    df_load,
                    columns=[
                        "begin",
                        "end",
                        "open",
                        "high",
                        "low",
                        "close",
                        "value",
                        "volume",
                    ],
                )
                real_limit = df_load.shape[0]  # кол-во полученных строк
                if not df_load.empty:  # не пустой ли DataFrame
                    svech = (
                        df_load.shape[0] + svech
                    )  # кол-во полученных строк по акции всего
                    # при дневках в колонке "begin" нет %H:%M:%S - исправляем
                    df_load["begin"] = df_load["begin"] + pd.Timedelta(
                        hours=0, minutes=0, seconds=0
                    )
                    df_load["begin"] = df_load["begin"].dt.strftime("%Y-%m-%d %H:%M:%S")
                    # получаем время "begin" у последней свечки
                    date = pd.to_datetime(df_load.iloc[-1]["begin"])
                    # добавляем к дате период таймфрейм для следующей свечи
                    # в следующей итерации цикла
                    date = date + timeframe
                if svech > 1:
                    # записываем скачанные данные в файл, добавление к
                    # существующему в файле содержимому.
                    df_load.to_csv(
                        filestocks_path, mode="a", sep=";", index=False, header=False
                    )
                print(
                    f"получили данные до {date}. Продолжаем качать ⌛.....", end="\r"
                )  # отображаем процесс скачивания
            if svech > 1:
                logger.info(
                    f"скачано {svech} свечей с таймфреймом {period} для акции '{SECID}'"
                )
                logger.info(
                    f"все данные записаны в '{filestocks_path}',"
                    f"размер файла {round(os.path.getsize(filestocks_path)/ (1024 * 1024), 4) } МБ."
                )
            else:
                logger.info(f"Новых данных для акции '{SECID}' не обнаружено")
        return


def main():
    # df = MoexDownloader.get_all_shares()
    # df.to_csv("all_shares.csv", sep=";")

    # for candle in candles:
    #     print(candle)

    dt = MoexDownloader.get_first_date("SBER")
    print(dt)
    MoexDownloader.get_candles("SBER", TimeFrame("D"), begin=dt)




if __name__ == '__main__':
    main()

