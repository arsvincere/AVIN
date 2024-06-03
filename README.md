# AVIN - Complex system for algo trading

AVIN (лат. Ars Vincere  -  искусство побеждать)  —  это кросплатформенная
трейдинговая система, распостраняющаяся по GNU GPLv3. Написана на Python,
с GUI на PyQt6.

Система предоставляет полный инструментарий для алготрейдера:
- Загрузку исторических данных.
- Слой абстракций для работы с данными на "трейдерском языке".
- Инструменты для анализа и написания стратегий.
- Бэк-тестер.
- Модуль управления роботами.
- Песочница (paper-trading).
- Простой терминал для ручного управления.
- Построение отчетов.
- Уведомления в telegramm/email.

Программа на этапе бетта-тестирования и рефакторинга основных модулей. Модули
будут появляться в репозитарии последовательно, по мере готовности. Плановый
релиз v0.1 намечен на 1 января 2025 г.

Больше информации о проекте смотрите на сайте:
[arsvincere.com](http://arsvincere.com)

![image](https://github.com/arsvincere/AVIN/blob/master/res/screenshot/Screenshot_2024-02-28_13-11-10.png)


## Getting start

1. Clone this repository

```
git clone --depth=1 https://github.com/arsvincere/AVIN.git
```

2. Run
```
cd AVIN
python3 main.py
```

## Requarements

[moexalgo](https://github.com/moexalgo/moexalgo) - оффициальная библиотека Московской биржи для получения данных:

    pip install moexalgo

[tinkoff-investments](https://github.com/Tinkoff/invest-python) - клиент для взаимодействия с торговой платформой Тинькофф Инвестиции на языке Python.

    pip install tinkoff-investments

[pandas](https://github.com/pandas-dev/pandas) - powerful Python data analysis toolkit.

    pip install pandas

[PyQt6](https://pypi.org/project/PyQt6/) - набор расширений графического фреймворка Qt для языка программирования Python:

    pip install pyqt6
	

## Documentation

- [doc-ru](https://github.com/arsvincere/AVIN/tree/master/doc/ru)
- [doc-en](...) - comming soon


## Examples

- [examples](https://github.com/arsvincere/AVIN/tree/master/doc/examples/data)

