#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""The module provides interaction with the postgresql database

It is assumed, that the user does not use this class directly. All other
classes in program turn to the database through the interface of this class
"Keeper". Thus, the entire SQL code is collected inside this class.

But if you really need to make a direct request to the database, you can use
the 'transaction(sql_request)' method.
"""

from __future__ import annotations

import inspect
import json
import os

import asyncpg

from avin.const import Usr
from avin.logger import logger
from avin.utils import askUser

__all__ = ("Keeper",)


class Keeper:
    """const"""  # {{{

    USER = Usr.PG_USER
    DATABASE = Usr.PG_DATABASE
    HOST = Usr.PG_HOST
    # }}}

    @classmethod  # transaction  # {{{
    async def transaction(cls, sql_request: str) -> list[Record]:
        logger.debug(f"{cls.__name__}.transaction()\n{sql_request}")

        try:
            conn = await asyncpg.connect(
                user=cls.USER,
                database=cls.DATABASE,
                host=cls.HOST,
            )
            records = await conn.fetch(sql_request)
            await conn.close()
            return records
        except asyncpg.exceptions.NumericValueOutOfRangeError as err:
            logger.critical(err)
            exit(2)

    # }}}
    @classmethod  # createDataBase  # {{{
    async def createDataBase(cls) -> None:
        logger.debug(f"{cls.__name__}.createDataBase()")

        os.system(f"createdb {cls.DATABASE}")
        await cls.__createEnums()
        await cls.__createCacheTable()
        await cls.__createExchangeTable()
        await cls.__createAssetTable()
        await cls.__createDataTable()
        await cls.__createAccountTable()
        await cls.__createStrategyTable()
        await cls.__createTradeTable()
        await cls.__createOrderTable()
        await cls.__createOperationTable()
        await cls.__createMarketDataScheme()

        logger.info("Database has been created")

    # }}}
    @classmethod  # dropDataBase  # {{{
    async def dropDataBase(cls) -> None:
        logger.debug(f"{cls.__name__}.dropDataBase()")

        if not askUser("Delete database?"):
            return

        if not askUser("Double confirmation. Are you sure?"):
            return

        os.system(f"dropdb {cls.DATABASE}")
        logger.info("Database has been deleted")

    # }}}
    @classmethod  # info  # {{{
    async def info(
        cls, source: DataSource, asset_type: AssetType, **kwargs
    ) -> list[dict]:
        """Looks for information about the asset in the cache.

        Returns a list of dictionaries with information about assets
        suitable for a request 'kwargs'
        """

        logger.debug(f"{cls.__name__}.info()")

        # Create source condition
        pg_source = f"source = '{source.name}'" if source else "TRUE"

        # Create asset_type condition
        pg_asset_type = (
            f"type = '{asset_type.name}'" if asset_type else "TRUE"
        )

        # Remove None values & create kwargs condition
        none_keys = [key for key in kwargs if kwargs[key] is None]
        for i in none_keys:
            kwargs.pop(i)
        if not kwargs:
            pg_kwargs = "TRUE"
        else:
            json_string = json.dumps(kwargs, ensure_ascii=False)
            pg_kwargs = f"info @> '{json_string}'"

        # Request assets info records
        request = f"""
            SELECT
                info
            FROM "Cache"
            WHERE {pg_source} AND {pg_asset_type} AND {pg_kwargs};
            """
        records = await cls.transaction(request)

        # Create info dicts from records
        assets_info = list()
        for record in records:
            json_string = record["info"]
            info_dict = json.loads(json_string)
            assets_info.append(info_dict)

        return assets_info

    # }}}
    @classmethod  # add  # {{{
    async def add(cls, obj: object | class_) -> None:
        logger.debug(f"{cls.__name__}.add()")

        # Get class_name & choose method
        class_name = cls.__getClassName(obj)
        methods = {
            "MOEX": cls.__addExchange,
            "SPB": cls.__addExchange,
            "_TEST_EXCHANGE": cls.__addExchange,
            "InstrumentId": cls.__addAsset,
            "_BarsData": cls.__addBarsData,
            "Asset": cls.__addAsset,
            "Share": cls.__addAsset,
            "Index": cls.__addAsset,
            "Account": cls.__addAccount,
            "Strategy": cls.__addStrategy,
            "Trade": cls.__addTrade,
            "Operation": cls.__addOperation,
            "Order": cls.__addOrder,
            "Market": cls.__addOrder,
            "Limit": cls.__addOrder,
            "Stop": cls.__addOrder,
        }
        add_method = methods[class_name]

        # Add object
        await add_method(obj)

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, obj, **kwargs) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        # Get class_name & choose method
        class_name = cls.__getClassName(obj)
        methods = {
            "_TEST_EXCHANGE": cls.__deleteExchange,
            "MOEX": cls.__deleteExchange,
            "SPB": cls.__deleteExchange,
            "InstrumentId": cls.__deleteAsset,
            "Asset": cls.__deleteAsset,
            "Share": cls.__deleteAsset,
            "Index": cls.__deleteAsset,
            "Account": cls.__deleteAccount,
            "Strategy": cls.__deleteStrategy,
            "Trade": cls.__deleteTrade,
            "Operation": cls.__deleteOperation,
            "Order": cls.__deleteOrder,
            "Market": cls.__deleteOrder,
            "Limit": cls.__deleteOrder,
            "Stop": cls.__deleteOrder,
            "_Bar": cls.__deleteBarsData,
        }
        delete_method = methods[class_name]

        # Delete object
        await delete_method(obj, kwargs)

    # }}}
    @classmethod  # update  # {{{
    async def update(cls, obj: object | class_) -> None:
        logger.debug(f"{cls.__name__}.update()")

        # Get class_name & choose method
        class_name = cls.__getClassName(obj)
        methods = {
            "Trade": cls.__updateTrade,
            "Market": cls.__updateOrder,
            "Limit": cls.__updateOrder,
            "Stop": cls.__updateOrder,
            "_InstrumentInfoCache": cls.__updateCache,
        }

        # Update object
        update_method = methods[class_name]
        await update_method(obj)

    # }}}
    @classmethod  # get  # {{{
    async def get(cls, Class, **kwargs) -> Any:
        logger.debug(f"{cls.__name__}.get()")
        assert inspect.isclass(Class)

        # Get class_name & choose method
        class_name = cls.__getClassName(Class)
        methods = {
            "InstrumentId": cls.__getInstrumentId,
            "Data": cls.__getData,
            "DataSource": cls.__getDataSource,
            "DataType": cls.__getDataType,
            "datetime": cls.__getDateTime,
            "_Bar": cls.__getBarsRecords,
            "Bar": cls.__getBars,
            "Asset": cls.__getAsset,
            "Account": cls.__getAccount,
            "Trade": cls.__getTrades,
            "Operation": cls.__getOperations,
            "Order": cls.__getOrders,
        }
        get_method = methods[class_name]

        # Get object(s)
        result = await get_method(Class, kwargs)
        return result

    # }}}

    @classmethod  # __addExchange  # {{{
    async def __addExchange(cls, exchange: Exchange) -> None:
        logger.debug(f"{cls.__name__}.__addExchange()")

        request = f"""
        INSERT INTO "Exchange"(name)
        VALUES ('{exchange.name}');
        """

        try:
            await cls.transaction(request)
        except asyncpg.UniqueViolationError:
            logger.warning(
                f"Exchange '{exchange.name}' already exist in database"
            )

    # }}}
    @classmethod  # __addAsset  # {{{
    async def __addAsset(cls, asset: Asset | Id) -> None:
        logger.debug(f"{cls.__name__}.__addAsset()")

        request = f"""
        INSERT INTO "Asset" (
            exchange,
            type,
            ticker,
            name,
            figi
            )
        VALUES (
            '{asset.exchange.name}',
            '{asset.type.name}',
            '{asset.ticker}',
            '{asset.name}',
            '{asset.figi}'
            );
        """

        try:
            await cls.transaction(request)
        except asyncpg.UniqueViolationError:
            logger.warning(f"Asset '{asset}' already exist in database")

    # }}}
    @classmethod  # __addBarsData  # {{{
    async def __addBarsData(cls, data: _BarsData) -> None:
        logger.debug(f"{cls.__name__}.__addBarsData()")

        # Create new Asset if not exist
        request = f"""
            SELECT add_asset_if_not_exist(
                '{data.ID.figi}',
                '{data.ID.type.name}',
                '{data.ID.exchange.name}',
                '{data.ID.ticker}',
                '{data.ID.name}'
                )
            ;
            """
        await cls.transaction(request)

        # Create table if not exist
        bars_table_name = cls.__getTableName(data.ID, data.type)
        await cls.__createBarsDataTable(bars_table_name)

        # If exist - delete old data at the same period
        request = f"""
            DELETE FROM {bars_table_name}
            WHERE
                '{data.first_dt}' <= dt AND dt <= '{data.last_dt}'
                ;
            """
        await cls.transaction(request)

        # Format bars data in postges value
        values = ""
        for b in data.bars:
            dt = f"'{b.dt.isoformat()}'"
            val = f"({dt},{b.open},{b.high},{b.low},{b.close},{b.vol}),\n"
            values += val
        values = values[0:-2]  # remove ",\n" after last value

        # Add bars data
        request = f"""
        INSERT INTO {bars_table_name} (dt, open, high, low, close, volume)
        VALUES
            {values}
            ;
        """
        await cls.transaction(request)

        # Update table "Data" - information about availible market data
        request = f"""
            DELETE FROM "Data"
            WHERE
                figi = '{data.ID.figi}' AND
                type = '{data.type.name}'
                ;
            """
        await cls.transaction(request)
        request = f"""
            INSERT INTO "Data"(figi, type, source, first_dt, last_dt)
            VALUES (
                '{data.ID.figi}',
                '{data.type.name}',
                '{data.source.name}',
                (SELECT min(dt) FROM {bars_table_name}),
                (SELECT max(dt) FROM {bars_table_name})
            );
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addAccount  # {{{
    async def __addAccount(cls, account: Account) -> None:
        logger.debug(f"{cls.__name__}.__addAccount()")

        request = f"""
        INSERT INTO "Account" (
            name,
            broker
            )
        VALUES (
            '{account.name}',
            '{account.broker}'
            );
        """

        try:
            await cls.transaction(request)
        except asyncpg.UniqueViolationError:
            logger.warning(
                f"Account '{account.name}-{account.broker}'"
                "already exist in database"
            )

    # }}}
    @classmethod  # __addStrategy  # {{{
    async def __addStrategy(cls, strategy: Strategy) -> None:
        logger.debug(f"{cls.__name__}.__addStrategy()")

        request = f"""
            INSERT INTO "Strategy" (
                name,
                version
            )
            VALUES (
                '{strategy.name}',
                '{strategy.version}'
            );
        """

        try:
            await cls.transaction(request)
        except asyncpg.UniqueViolationError:
            logger.warning(
                f"Strategy '{strategy.name}-{strategy.version}'"
                "already exist in database"
            )

    # }}}
    @classmethod  # __addTrade  # {{{
    async def __addTrade(cls, trade: Trade) -> None:
        logger.debug(f"{cls.__name__}.__addTrade()")

        request = f"""
            INSERT INTO "Trade" (
                trade_id, dt, status, strategy, version, type, figi
                )
            VALUES (
                {trade.trade_id},
                '{trade.dt}',
                '{trade.status.name}',
                '{trade.strategy}',
                '{trade.version}',
                '{trade.type.name}',
                '{trade.figi}'
                );
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addOrder  # {{{
    async def __addOrder(cls, order: Order) -> None:
        logger.debug(f"{cls.__name__}.__addOrder()")
        assert order.trade_id is not None
        assert order.account_name is not None

        # Используется проверка типа ордера через строки...
        # логично было бы использовать enum Order.Type, например:
        # if order.type == Order.Type.LIMIT
        # но для этого нужно импортировать модуль order, а тогда модуль order
        # не сможет импортировать модуль keeper (circular import)
        # хз как лучше, пока пусть типо по имени проверяет
        if order.type.name == "MARKET":
            price = "NULL"
            stop_price = "NULL"
            exec_price = "NULL"
        elif order.type.name == "LIMIT":
            price = order.price
            stop_price = "NULL"
            exec_price = "NULL"
        elif order.type.name == "STOP":
            price = "NULL"
            stop_price = order.stop_price
            exec_price = order.exec_price
        else:
            assert False, f"Что за новый тип ордера='{order.type}'"

        if order.meta is None:
            meta = "NULL"
        else:
            logger.warning("Напиши как правильно meta сохранять")
            logger.info(order.meta)
            assert False

        request = f"""
            INSERT INTO "Order" (
                order_id,
                account,
                type,
                status,
                direction,
                figi,
                lots,
                quantity,
                price,
                stop_price,
                exec_price,
                trade_id,
                meta
                )
            VALUES (
                {order.order_id},
                '{order.account_name}',
                '{order.type.name}',
                '{order.status.name}',
                '{order.direction.name}',
                '{order.figi}',
                {order.lots},
                {order.quantity},
                {price},
                {stop_price},
                {exec_price},
                {order.trade_id},
                {meta}
                );
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addOperation  # {{{
    async def __addOperation(cls, operation: Operation) -> None:
        logger.debug(f"{cls.__name__}.__addOperation()")
        assert operation.trade_id is not None
        assert operation.order_id is not None

        if operation.meta is None:
            meta = "NULL"
        else:
            logger.warning("Напиши как правильно meta сохранять")
            logger.info(operation.meta)
            assert False
            # что то типо такого
            meta = f"'{meta}'"

        request = f"""
            INSERT INTO "Operation" (
                operation_id,
                account,
                dt,
                direction,
                figi,
                lots,
                quantity,
                price,
                amount,
                commission,
                trade_id,
                order_id,
                meta
            )
            VALUES (
                {operation.operation_id},
                '{operation.account_name}',
                '{operation.dt}',
                '{operation.direction.name}',
                '{operation.figi}',
                {operation.lots},
                {operation.quantity},
                {operation.price},
                {operation.amount},
                {operation.commission},
                {operation.trade_id},
                {operation.order_id},
                {meta}
            );
        """
        await cls.transaction(request)

    # }}}

    @classmethod  # __deleteExchange  # {{{
    async def __deleteExchange(cls, exchange: Exchange, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteExchange()")

        request = f"""
        DELETE FROM "Exchange" WHERE name = '{exchange.name}';
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteAsset  # {{{
    async def __deleteAsset(cls, asset: Asset, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteAsset()")

        request = f"""
        DELETE FROM "Asset" WHERE figi = '{asset.figi}';
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteBarsData  # {{{
    async def __deleteBarsData(cls, _Bar: class_, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteBarsData()")

        ID = kwargs["ID"]
        data_type = kwargs["data_type"]
        begin = kwargs.get("begin")
        end = kwargs.get("end")

        # Create condition for begin-end:
        if begin and end:
            pg_period = f"'{begin}' <= dt AND dt < '{end}'"
        else:
            pg_period = "TRUE"

        # Delete bars
        bars_table_name = cls.__getTableName(ID, data_type)
        request = f"""
            DELETE FROM {bars_table_name}
            WHERE
                {pg_period}
            """
        await cls.transaction(request)

        # Update table "Data" - information about availible market data
        request = f"""
            UPDATE "Data"
            SET
                first_dt = (SELECT min(dt) FROM {bars_table_name}),
                last_dt = (SELECT max(dt) FROM {bars_table_name})
			WHERE
                figi = '{ID.figi}' AND
                type = '{data_type.name}'
            ;
            """
        await cls.transaction(request)

        # Delete table & info if its empty
        request = f"""
            SELECT * FROM {bars_table_name}
            """
        records = await cls.transaction(request)
        if not records:
            request = f"""
                DROP TABLE {bars_table_name};
                """
            await cls.transaction(request)
            request = f"""
                DELETE FROM "Data"
                WHERE
                    figi = '{ID.figi}' AND
                    type = '{data_type.name}'
                """
            await cls.transaction(request)

        # Delete asset if its not have market data?
        # NOTE:
        # если у этого ассета уже есть трейды, его не получится удалить.
        # Получается тогда удалять ассет из таблицы ассетов вообще
        # не имеет смысла, один раз добавили сюда актив - и все, он тут
        # навсегда. Хотя попытаться удалить его можно, но он удалится
        # только если по нему нет трейдов нигде в базе. Ок.
        # NOTE:
        # тут программа будет падать, когда до этого дойдет, когда
        # в гуи буду делать виджет, где будет удаление, там и посмотрю
        # стоит ли вообще этот кусок кода оставлять
        request = f"""
            SELECT * FROM "Data"
            WHERE
                figi = '{ID.figi}'
            """
        records = await cls.transaction(request)
        if not records:
            request = f"""
                DELETE FROM "Asset"
                WHERE
                    figi = '{ID.figi}'
                """
            await cls.transaction(request)

    # }}}
    @classmethod  # __deleteAccount  # {{{
    async def __deleteAccount(cls, account: Account, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteAccount()")

        request = f"""
        DELETE FROM "Account" WHERE name = '{account.name}';
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteStrategy  # {{{
    async def __deleteStrategy(cls, strategy: Strategy, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteStrategy()")

        request = f"""
            DELETE FROM "Strategy"
            WHERE
                name = '{strategy.name}' AND version = '{strategy.version}';
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteTrade  # {{{
    async def __deleteTrade(cls, trade: Trade, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteTrade()")

        request = f"""
            DELETE FROM "Trade"
            WHERE trade_id = '{trade.trade_id}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteOrder  # {{{
    async def __deleteOrder(cls, order: Order, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteOrder()")

        request = f"""
            DELETE FROM "Order"
            WHERE order_id = '{order.order_id}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteOperation  # {{{
    async def __deleteOperation(
        cls, operation: Operation, kwargs: dict
    ) -> None:
        logger.debug(f"{cls.__name__}.__deleteOperation()")

        request = f"""
            DELETE FROM "Operation"
            WHERE
                operation_id = '{operation.operation_id}';
        """
        await cls.transaction(request)

    # }}}

    @classmethod  # __updateTrade  # {{{
    async def __updateTrade(cls, trade: Trade) -> None:
        logger.debug(f"{cls.__name__}.__updateTrade()")

        request = f"""
            UPDATE "Trade"
            SET
                dt = '{trade.dt}',
                status = '{trade.status.name}',
                strategy = '{trade.strategy}',
                version = '{trade.version}',
                type = '{trade.type.name}',
                figi = '{trade.figi}'
            WHERE
                trade_id = '{trade.trade_id}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __updateOrder  # {{{
    async def __updateOrder(cls, order: Order) -> None:
        logger.debug(f"{cls.__name__}.__updateOrder()")

        request = f"""
            UPDATE "Order"
            SET
                status = '{order.status.name}'
            WHERE
                order_id = '{order.ID}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __updateCache  # {{{
    async def __updateCache(cls, cache: _InstrumentInfoCache) -> None:
        logger.debug(f"{cls.__name__}.__updateCache()")

        # delete old cache
        request = f"""
            DELETE FROM "Cache"
            WHERE
                source = '{cache.source.name}' AND
                type = '{cache.asset_type.name}'
                ;
            """
        await cls.transaction(request)

        # format cache into postgres values
        def formatCache(cache: _InstrumentInfoCache) -> str:
            values = ""
            for i in cache.assets_info:
                pg_source = f"'{cache.source.name}'"
                pg_asset_type = f"'{cache.asset_type.name}'"
                json_string = json.dumps(
                    i, ensure_ascii=False, default=cache.encoderJson
                )
                pg_asset_info = f"'{json_string}'"

                val = f"({pg_source}, {pg_asset_type}, {pg_asset_info}),\n"
                values += val

            values = values[0:-2]  # remove ",\n" after last value
            return values

        # save new cache
        values = formatCache(cache)
        request = f"""
            INSERT INTO "Cache" (
                source,
                type,
                info
                )
            VALUES
                {values}
                ;
        """
        await cls.transaction(request)

        # NOTE:
        # update "last_update" datetime....
        # Сейчас это хранится в файле ./res/cache/moex/last_update
        # хотя потом можно будет создать отдельную таблицу и в нее свести
        # даты всех возможных апдейтов, когдда обновляли последний раз
        # кэш, исторические данные, когда строили отчеты... когда там еще
        # что нибудь. Пока это рано. Пока пусть в файлах - это более гибко.
        # когда выработается понимание какие даты будут храниться, тогда
        # и делать таблицу

    # }}}

    @classmethod  # __getClassName  # {{{
    def __getClassName(cls, obj: object | class_) -> str:
        logger.debug(f"{cls.__name__}.__getClassName()")

        # Get object class name, 'obj' may be a class, when its Exchange
        # like class: Exchange.MOEX
        if inspect.isclass(obj):
            class_name = obj.__name__
        else:
            class_name = obj.__class__.__name__

        return class_name

    # }}}
    @classmethod  # __getTableName  # {{{
    def __getTableName(
        cls,
        ID: InstrumentId,
        data_type: DataType,
    ) -> str:
        # table name looks like: "data.MOEX_SHARE_SBER_1M"
        logger.debug(f"{cls.__name__}.__getTableName()")

        bars_table_name = (
            f'"data.{ID.exchange.name}_{ID.type.name}_{ID.ticker}_'
            f'{data_type}"'
        )
        return bars_table_name

    # }}}
    @classmethod  # __getInstrumentId  # {{{
    async def __getInstrumentId(
        cls,
        InstrumentId,
        kwargs: dict,
    ) -> list[InstrumentId]:
        """Search InstrumentId

        Unlike the function Keeper.info(...), this method called from
        Keeper.get(InstrumentId, kwargs) looks for assets not in cache, but
        only among those for which exchange data are loaded. They are stored
        in table public."Asset"

        See also: __getAsset

        Args:
            InstrumentId (class InstrumentId): reference to class, to provide
                access to the method InstrumentId.fromRecord(...). It is need
                for return object of class Asset, instead asyncpg.Record.
                The title letter in the name of the argument recalls that
                this is the class.
            kwargs (str): for example: figi="BBG004730N88"

        Returns:
            InstrumentId
        """
        logger.debug(f"{cls.__name__}.__getInstrumentId()")

        figi = kwargs.get("figi")

        # Create figi condition
        pg_figi = f"figi = '{figi}'" if figi else "TRUE"

        # Request instrument IDs
        request = f"""
            SELECT
                exchange,
                type,
                ticker,
                name,
                figi
            FROM "Asset"
            WHERE
                {pg_figi}
            ;
            """
        records = await cls.transaction(request)

        # Create 'list' of 'InstrumentId' from records
        id_list = list()
        for i in records:
            ID = InstrumentId.fromRecord(i)
            id_list.append(ID)
        return id_list

    # }}}
    @classmethod  # __getData  # {{{
    async def __getData(cls, Data, kwargs: dict) -> list[Record]:
        logger.debug(f"{cls.__name__}.__getData()")

        ID = kwargs.get("ID")
        data_type = kwargs.get("data_type")

        # Create figi condition
        pg_id = f"figi = '{ID.figi}'" if ID else "TRUE"

        # Create figi condition
        pg_data_type = f"type = '{data_type.name}'" if data_type else "TRUE"

        # Request data info
        request = f"""
            SELECT * FROM "Data"
            WHERE
                {pg_id} AND {pg_data_type};
            """
        records = await cls.transaction(request)
        return records

    # }}}
    @classmethod  # __getDataSource  # {{{
    async def __getDataSource(
        cls, DataSource, kwargs: dict
    ) -> list[DataType]:
        logger.debug(f"{cls.__name__}.__getDataType()")

        ID = kwargs["ID"]
        data_type = kwargs["data_type"]

        request = f"""
            SELECT (source) FROM "Data"
            WHERE
                figi = '{ID.figi}' AND type = '{data_type.name}'
                ;
            """
        records = await cls.transaction(request)
        assert len(records) == 1

        source = DataSource.fromRecord(records[0])
        return source

    # }}}
    @classmethod  # __getDataType  # {{{
    async def __getDataType(cls, DataType, kwargs: dict) -> list[DataType]:
        logger.debug(f"{cls.__name__}.__getDataType()")

        ID = kwargs["ID"]

        request = f"""
            SELECT (type) FROM "Data"
            WHERE
                figi = '{ID.figi}';
            """
        records = await cls.transaction(request)

        data_types = list()
        for i in records:
            typ = DataType.fromStr(i["type"])
            data_types.append(typ)

        return data_types

    # }}}
    @classmethod  # __getDateTime  # {{{
    async def __getDateTime(cls, datetime, kwargs: dict) -> list[Record]:
        logger.debug(f"{cls.__name__}.__getData()")

        ID = kwargs["ID"]
        data_type = kwargs["data_type"]

        # Create figi condition
        pg_id = f"figi = '{ID.figi}'"

        # Create figi condition
        pg_data_type = f"type = '{data_type.name}'"

        # Request data info
        request = f"""
            SELECT * FROM "Data"
            WHERE
                {pg_id} AND {pg_data_type};
            """
        records = await cls.transaction(request)
        assert len(records) == 1
        record = records[0]
        return record["first_dt"], record["last_dt"]

    # }}}
    @classmethod  # __getBarsRecords  # {{{
    async def __getBarsRecords(cls, _Bar, kwargs: dict) -> list[Record]:
        logger.debug(f"{cls.__name__}.__getBars()")

        ID = kwargs["ID"]
        data_type = kwargs.get("data_type")
        begin: datatime = kwargs.get("begin")
        end: datetime = kwargs.get("end")

        # create table name
        bars_table_name = cls.__getTableName(ID, data_type=data_type)

        # create condition for begin-end:
        if begin is None and end is None:
            pg_period = "TRUE"
        else:
            pg_period = f"'{begin}' <= dt AND dt < '{end}'"

        # request bars records
        request = f"""
            SELECT dt, open, high, low, close, volume
            FROM {bars_table_name}
            WHERE
                {pg_period}
            ORDER BY dt
            ;
            """
        records = await cls.transaction(request)

        return records

    # }}}
    @classmethod  # __getBars  # {{{
    async def __getBars(cls, Bar, kwargs: dict) -> list[Bar]:
        logger.debug(f"{cls.__name__}.__getBars()")

        # timeframe -> data_type, and add it to kwargs
        kwargs.setdefault("data_type", kwargs["timeframe"].toDataType())

        # request bars records
        records = await cls.__getBarsRecords(Bar, kwargs)

        # create bars
        bars = list()
        for record in records:
            bar = Bar.fromRecord(record)
            bars.append(bar)

        return bars

    # }}}
    @classmethod  # __getAsset  # {{{
    async def __getAsset(cls, Asset, kwargs: dict) -> Asset:
        """Search asset

        Unlike the function Keeper.info(...), this method called from
        Keeper.get(Asset, kwargs) looks for assets not in cache, but
        only among those for which exchange data are loaded. They are stored
        in table public."Asset"

        See also: __getInstrumentId

        Args:
            Asset (class Asset): reference to class, to provide access to the
                method Asset.fromRecord(...). It is need for return object of
                class Asset, instead asyncpg.Record.
                The title letter in the name of the argument recalls that
                this is the class.
            kwargs (str): for example: figi="BBG004730N88"

        Returns:
            Asset
        """

        logger.debug(f"{cls.__name__}.__getAsset()")

        asset_type = kwargs.get("asset_type")
        exchange = kwargs.get("exchange")
        ticker = kwargs.get("ticker")
        figi = kwargs.get("figi")

        # create condition
        if figi:
            pg_condition = f"figi = '{figi}'"
        elif asset_type and exchange and ticker:
            pg_condition = (
                f"type = '{asset_type.name}' AND "
                f"exchange = '{exchange.name}' AND "
                f"ticker = '{ticker}'"
            )
        else:
            assert False

        request = f"""
            SELECT
                exchange,
                type,
                ticker,
                name,
                figi
            FROM "Asset"
            WHERE
                {pg_condition}
            ;
            """
        asset_records = await cls.transaction(request)

        assert len(asset_records) == 1
        asset = Asset.fromRecord(asset_records[0])
        return asset

    # }}}
    @classmethod  # __getAccount  # {{{
    async def __getAccount(cls, Account, kwargs: dict) -> list[Account]:
        logger.debug(f"{cls.__name__}.__getAccount()")

        name = kwargs.get("name")

        # Create condition for name
        pg_name = f"name = '{name}'" if name else "TRUE"

        # Request accounts
        request = f"""
            SELECT name, broker FROM "Account"
            WHERE
                {pg_name}
            ;
            """
        records = await cls.transaction(request)

        # Create 'list' of 'Account' from 'Records'
        accounts = list()
        for i in records:
            acc = Account.fromRecord(i)
            accounts.append(acc)
        return accounts

    # }}}
    @classmethod  # __getTrades  # {{{
    async def __getTrades(cls, Trade, kwargs: dict) -> list[Trades]:
        logger.debug(f"{cls.__name__}.__getTrades()")

        strategy = kwargs.get("strategy")
        statuses = kwargs.get("status")
        begin = kwargs.get("begin")
        end = kwargs.get("end")

        # Create condition for strategy
        if strategy is None:
            pg_strategy = "TRUE"
        else:
            pg_strategy = (
                f"(strategy = '{strategy.name}' AND "
                f"version = '{strategy.version}')"
            )

        # Create condition for statuses, like this:
        # (status = 'INITIAL' OR status = 'NEW' OR status = 'OPEN')
        if statuses is None:
            pg_statuses = "TRUE"
        else:
            pg_statuses = f"(status = '{statuses[0].name}'"
            i = 1
            while i < len(statuses):
                pg_statuses += f" OR status = '{statuses[i].name}'"
                i += 1
            pg_statuses += ")"

        # Create condition for begin datetime
        pg_begin = f"dt >= '{begin}'" if begin else "TRUE"

        # Create condition for end datetime
        pg_end = f"dt < '{end}'" if end else "TRUE"

        # Request trades
        request = f"""
            SELECT trade_id, dt, status, strategy, version, type, figi
            FROM "Trade"
            WHERE {pg_strategy} AND {pg_statuses} AND {pg_begin} AND {pg_end}
            ORDER BY dt
            ;
            """
        trade_records = await cls.transaction(request)

        # Create 'list' of 'Trade' objects from 'Records'
        tlist = list()
        for i in trade_records:
            trade = await Trade.fromRecord(i)
            tlist.append(trade)

        return tlist

    # }}}
    @classmethod  # __getOperations  # {{{
    async def __getOperations(
        cls, Operation, kwargs: dict
    ) -> list[Operation]:
        logger.debug(f"{cls.__name__}.__getOperations()")

        trade_id = kwargs.get("trade_id")
        request = f"""
            SELECT
                operation_id,
                account,
                dt,
                direction,
                figi,
                lots,
                quantity,
                price,
                amount,
                commission,
                trade_id,
                order_id,
                meta
            FROM "Operation"
            WHERE trade_id = {trade_id}
            ORDER BY dt
            ;
            """
        op_records = await cls.transaction(request)

        # Create 'list' of 'Operation' objects from 'Records'
        op_list = list()
        for i in op_records:
            op = Operation.fromRecord(i)
            op_list.append(op)

        return op_list

    # }}}
    @classmethod  # __getOrders  # {{{
    async def __getOrders(cls, Order, kwargs: dict) -> list[Order]:
        logger.debug(f"{cls.__name__}.__getOrders()")

        trade_id = kwargs.get("trade_id")
        request = f"""
            SELECT
                order_id,
                account,
                type,
                status,
                direction,
                figi,
                lots,
                quantity,
                price,
                stop_price,
                exec_price,
                trade_id,
                meta
            FROM "Order"
            WHERE trade_id = {trade_id}
            ;
            """
        order_records = await cls.transaction(request)

        # Create 'list' of 'Order' objects from 'Records'
        order_list = list()
        for i in order_records:
            order = Order.fromRecord(i)
            order_list.append(order)

        return order_list

    # }}}

    @classmethod  # __createEnums  # {{{
    async def __createEnums(cls) -> None:
        logger.debug(f"{cls.__name__}.__createEnums()")

        requests = [  # {{{
            """DROP TYPE IF EXISTS public."DataSource";""",
            """ CREATE TYPE "DataSource" AS ENUM (
                'MOEX',
                'TINKOFF'
                );""",
            """DROP TYPE IF EXISTS public."AssetType";""",
            """ CREATE TYPE "AssetType" AS ENUM (
                'CASH',
                'INDEX',
                'SHARE',
                'BOND',
                'FUTURE',
                'OPTION',
                'CURRENCY',
                'ETF'
                );""",
            """DROP TYPE IF EXISTS public."DataType";""",
            """ CREATE TYPE "DataType" AS ENUM (
                'BAR_1M',
                'BAR_5M',
                'BAR_10M',
                'BAR_1H',
                'BAR_D',
                'BAR_W',
                'BAR_M',
                'BAR_Q',
                'BAR_Y'
                );""",
            """DROP TYPE IF EXISTS public."TimeFrame";""",
            """ CREATE TYPE "TimeFrame" AS ENUM (
                '1M',
                '5M',
                '10M',
                '1H',
                'D',
                'W',
                'M',
                'Q',
                'Y'
                );""",
            """DROP TYPE IF EXISTS public."Order.Type";""",
            """ CREATE TYPE "Order.Type" AS ENUM (
                'MARKET',
                'LIMIT',
                'STOP',
                'STOP_LOSS',
                'TAKE_PROFIT',
                'WAIT',
                'TRAILING'
                );""",
            """DROP TYPE IF EXISTS public."Order.Direction";""",
            """ CREATE TYPE "Order.Direction" AS ENUM (
                'BUY',
                'SELL'
                );""",
            """DROP TYPE IF EXISTS public."Order.Status";""",
            """ CREATE TYPE "Order.Status" AS ENUM (
                'NEW',
                'POST',
                'PARTIAL',
                'EXECUTED',
                'OFF',
                'CANCEL',
                'REJECT',
                'WAIT'
                );""",
            """DROP TYPE IF EXISTS public."Operation.Direction";""",
            """ CREATE TYPE "Operation.Direction" AS ENUM (
                'BUY',
                'SELL'
                );""",
            """DROP TYPE IF EXISTS public."Trade.Type";""",
            """ CREATE TYPE "Trade.Type" AS ENUM (
                'LONG',
                'SHORT'
                );""",
            """DROP TYPE IF EXISTS public."Trade.Status";""",
            """ CREATE TYPE "Trade.Status" AS ENUM (
                'INITIAL',
                'NEW',
                'OPEN',
                'CLOSE',
                'CANCELED'
                );""",
        ]  # }}}

        for i in requests:
            await cls.transaction(i)

    # }}}
    @classmethod  # __createCacheTable  # {{{
    async def __createCacheTable(cls) -> None:
        logger.debug(f"{cls.__name__}.__createCacheTable()")

        request = """
        CREATE TABLE IF NOT EXISTS "Cache" (
            source "DataSource",
            type "AssetType",
            info jsonb
            );
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __createExchangeTable  # {{{
    async def __createExchangeTable(cls) -> None:
        logger.debug(f"{cls.__name__}.__createExchangeTable()")

        request = """
        CREATE TABLE IF NOT EXISTS "Exchange" (
            name text PRIMARY KEY
            );
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __createAssetTable  # {{{
    async def __createAssetTable(cls) -> None:
        logger.debug(f"{cls.__name__}.__createAssetTable()")

        # Create asset table
        request = """
        CREATE TABLE IF NOT EXISTS "Asset" (
            figi text PRIMARY KEY,
            type "AssetType",
            exchange text REFERENCES "Exchange"(name),
            ticker text,
            name text
            );
        """
        await cls.transaction(request)

        # Create function for add asset if it is not exist
        request = """
        CREATE OR REPLACE FUNCTION add_asset_if_not_exist(
            a_figi text,
            a_type "AssetType",
            a_exchange text,
            a_ticker text,
            a_name text
            )
        RETURNS void
        LANGUAGE plpgsql
        AS $$
            BEGIN
                IF NOT EXISTS (SELECT figi FROM "Asset" WHERE figi = a_figi)
                THEN
                    INSERT INTO "Asset" (figi, type, exchange, ticker, name)
                    VALUES
                        (a_figi, a_type, a_exchange, a_ticker, a_name);
                END IF;
            END;
        $$;
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __createDataTable  # {{{
    async def __createDataTable(cls) -> None:
        logger.debug(f"{cls.__name__}.__createDataTable()")

        request = """
        CREATE TABLE IF NOT EXISTS "Data" (
            figi text REFERENCES "Asset"(figi),
            type "DataType",
            source "DataSource",
            first_dt TIMESTAMP WITH TIME ZONE,
            last_dt TIMESTAMP WITH TIME ZONE
            );
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __createBarsDataTable  # {{{
    async def __createBarsDataTable(cls, bars_table_name: str) -> None:
        """Create a separate table for bars

        Every asset have market data candles in different timeframes.
        I'm create a table for each. For example asset 'SBER' has some tables:
            - data."MOEX_SHARE_SBER_1M"
            - data."MOEX_SHARE_SBER_10M"
            - data."MOEX_SHARE_SBER_1H"
            - data."MOEX_SHARE_SBER_D"
            - ...
        """
        logger.debug(f"{cls.__name__}.__createBarsDataTable()")

        request = f"""
        CREATE TABLE IF NOT EXISTS {bars_table_name} (
            dt TIMESTAMP WITH TIME ZONE PRIMARY KEY,
            open float,
            high float,
            low float,
            close float,
            volume bigint
            );
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __createAccountTable  # {{{
    async def __createAccountTable(cls) -> None:
        logger.debug(f"{cls.__name__}.__createAccountTable()")

        # Create account table
        request = """
        CREATE TABLE IF NOT EXISTS "Account" (
            name text PRIMARY KEY,
            broker text
            );
        """
        await cls.transaction(request)

        # If not exist, create system account for back-tester
        request = """
        SELECT name FROM "Account"
        WHERE name = '_backtest'
        """
        records = await cls.transaction(request)
        if not records:
            request = """
            INSERT INTO "Account" (
                name,
                broker
                )
            VALUES
                ('_backtest', 'ArsVincere')
                ;
            """
            await cls.transaction(request)

        # If not exist, create system account for unit-tests
        request = """
        SELECT name FROM "Account"
        WHERE name = '_unittest'
        """
        records = await cls.transaction(request)
        if not records:
            request = """
            INSERT INTO "Account" (
                name,
                broker
                )
            VALUES
                ('_unittest', 'ArsVincere')
                ;
            """
            await cls.transaction(request)

    # }}}
    @classmethod  # __createStrategyTable  # {{{
    async def __createStrategyTable(cls) -> None:
        logger.debug(f"{cls.__name__}.__createStrategyTable()")

        request = """
        CREATE TABLE IF NOT EXISTS "Strategy" (
            name text,
            version text,
            CONSTRAINT strategy_pkey PRIMARY KEY (name, version)
            );
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __createTradeTable  # {{{
    async def __createTradeTable(cls) -> None:
        logger.debug(f"{cls.__name__}.__createTradeTable()")

        request = """
        CREATE TABLE IF NOT EXISTS "Trade" (
            trade_id    float PRIMARY KEY,
            dt          TIMESTAMP WITH TIME ZONE,
            status      "Trade.Status",
            strategy    text,
            version     text,
            type        "Trade.Type",
            figi        text REFERENCES "Asset"(figi),

			FOREIGN KEY (strategy, version)
                REFERENCES "Strategy" (name, version)
			);
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __createOrderTable  # {{{
    async def __createOrderTable(cls) -> None:
        logger.debug(f"{cls.__name__}.__createOrderTable()")

        # TODO: добавить частично исполненный - сколько там уже исполнено
        request = """
        CREATE TABLE IF NOT EXISTS "Order" (
            order_id        float PRIMARY KEY,
            account         text REFERENCES "Account"(name),
            type            "Order.Type",
            status          "Order.Status",
            direction       "Order.Direction",
            figi            text REFERENCES "Asset"(figi),
            lots            integer,
            quantity        integer,
            price           float,
            stop_price      float,
            exec_price      float,

            trade_id        float REFERENCES "Trade"(trade_id),
			meta            text
			);
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __createOperationTable  # {{{
    async def __createOperationTable(cls) -> None:
        logger.debug(f"{cls.__name__}.__createOperationTable()")

        request = """
        CREATE TABLE IF NOT EXISTS "Operation" (
            operation_id    float PRIMARY KEY,
            account         text REFERENCES "Account"(name),
            dt              TIMESTAMP WITH TIME ZONE,
            direction       "Operation.Direction",
            figi            text REFERENCES "Asset"(figi),
            lots            integer,
            quantity        integer,
            price           float,
            amount          float,
            commission      float,
            trade_id        float REFERENCES "Trade"(trade_id),
            order_id        float REFERENCES "Order"(order_id),
			meta            text
			);
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __createMarketDataScheme  # {{{
    async def __createMarketDataScheme(cls) -> None:
        logger.debug(f"{cls.__name__}.__createMarketDataScheme()")

        request = """
        CREATE SCHEMA IF NOT EXISTS data
        """
        await cls.transaction(request)

    # }}}
