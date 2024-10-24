# AVIN - Open source cross-platform trading system

AVIN (лат. Ars Vincere  -  искусство побеждать)  —  это кросплатформенная
трейдинговая система, распостраняющаяся по GNU GPLv3. Написана на Python,
с GUI на PyQt6.

Система предоставляет полный инструментарий для алготрейдера.

## Modules and features:

- **data:** Загрузка и просмотр исторических данных. Пока только с Московской
  биржи.
- **core:** Python API для написания стратегий - слой абстракций для
  высокоуровневой работы с данными на "трейдерском языке". Интуитивно
  понятные интерфейсы.
- **tester:** Простой бэк-тестер.
- **trader:** Модуль управления роботами. Пока доступно подключение
  только к Тинькофф брокеру (Т-банк).
- **analytic:** Продвинутые инструменты анализа исторических данных.
  Сохранение результатов в базу данных. Загрузка и использование результатов
  анализа в работе стратегий. Возможность добавления своих модулей и функций
  анализа, через стандартизированный интерфейс, c последующим использованием
  в работе стратегий.
- **keeper:** Модуль взаимодействия с базой данных PostgesQL.
- **terminal:** Простой терминал для ручного управления на всякий случай.
- **report**: Построение отчетов.
- **informer:** Уведомления в telegram.
- **gui:** Графический интерфейс для управления всеми функциями системы.

Программа на этапе альфа-тестирования и рефакторинга основных модулей.
Модули будут появляться в репозитарии последовательно, по мере готовности.
Плановый релиз v0.1 betta намечен на 1 января 2025 г.

Больше информации о проекте смотрите на сайте:
[arsvincere.com](http://arsvincere.com)

![image](https://github.com/arsvincere/AVIN/blob/master/res/screenshot/Screenshot_2024-02-28_13-11-10.png)


## Getting start

1. Clone this repository

```
git clone --depth=1 https://github.com/arsvincere/AVIN.git
```

2. Create venv

```
cd AVIN
python -m venv env
```

3. Activate venv

```
source env/bin/activate
```

4. Install requirements:
```
pip install -r requirements.txt
```

5. Run
```
python3 main.py
```


## Requirements

[moexalgo](https://github.com/moexalgo/moexalgo) - оффициальная библиотека Московской биржи для получения данных:

    pip install moexalgo

[tinkoff-investments](https://github.com/Tinkoff/invest-python) - клиент для взаимодействия с торговой платформой Тинькофф Инвестиции на языке Python.

    pip install tinkoff-investments

[pandas](https://github.com/pandas-dev/pandas) - powerful Python data analysis toolkit.

    pip install pandas

[PyQt6](https://pypi.org/project/PyQt6/) - набор расширений графического фреймворка Qt для языка программирования Python:

    pip install pyqt6


## Documentation

- [doc-ru](https://github.com/arsvincere/AVIN/tree/master/doc/ru) - в процессе написания, но уже читабельно
- [doc-en]() - comming soon


## Examples

- [examples](https://github.com/arsvincere/AVIN/tree/master/doc/examples/data)

