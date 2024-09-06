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
the 'Keeper.transaction(sql_request)' method.
"""

from __future__ import annotations

import inspect
import json
import os
from typing import Any

import asyncpg

from avin.config import Usr
from avin.const import Dir
from avin.utils import Cmd, askUser, logger

__all__ = ("Keeper",)


class Keeper:
    """const"""  # {{{

    USER = Usr.PG_USER
    DATABASE = Usr.PG_DATABASE
    HOST = Usr.PG_HOST

    _DATA_SCHEME = Cmd.path(Dir.LIB, "keeper", "data_scheme.sql")
    _ENUMS = Cmd.path(Dir.LIB, "keeper", "enums.sql")
    _FUNCTIONS = Cmd.path(Dir.LIB, "keeper", "functions.sql")
    _PUBLIC_SCHEME = Cmd.path(Dir.LIB, "keeper", "public_scheme.sql")
    _TESTER_SCHEME = Cmd.path(Dir.LIB, "keeper", "tester_scheme.sql")
    # }}}

    @classmethod  # createDataBase  # {{{
    async def createDataBase(cls) -> None:
        logger.debug(f"{cls.__name__}.createDataBase()")

        os.system(f"createdb {cls.DATABASE}")
        os.system(f"psql -d {cls.DATABASE} < {cls._ENUMS}")
        os.system(f"psql -d {cls.DATABASE} < {cls._DATA_SCHEME}")
        os.system(f"psql -d {cls.DATABASE} < {cls._PUBLIC_SCHEME}")
        os.system(f"psql -d {cls.DATABASE} < {cls._TESTER_SCHEME}")
        os.system(f"psql -d {cls.DATABASE} < {cls._FUNCTIONS}")

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
    async def add(cls, obj: object | Class) -> None:
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
            "AssetList": cls.__addAssetList,
            "Account": cls.__addAccount,
            "Strategy": cls.__addStrategy,
            "UStrategy": cls.__addStrategy,
            "Trade": cls.__addTrade,
            "TradeList": cls.__addTradeList,
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
            "AssetList": cls.__deleteAssetList,
            "Account": cls.__deleteAccount,
            "Strategy": cls.__deleteStrategy,
            "Trade": cls.__deleteTrade,
            "TradeList": cls.__deleteTradeList,
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
    async def update(cls, obj: object | Class) -> None:
        logger.debug(f"{cls.__name__}.update()")

        # Get class_name & choose method
        class_name = cls.__getClassName(obj)
        methods = {
            "TradeList": cls.__updateTradeList,
            "Trade": cls.__updateTrade,
            "Market": cls.__updateOrder,
            "Limit": cls.__updateOrder,
            "Stop": cls.__updateOrder,
            "Operation": cls.__updateOperation,
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
            "AssetList": cls.__getAssetList,
            "Account": cls.__getAccount,
            "Trade": cls.__getTrade,
            "TradeList": cls.__getTradeList,
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
    @classmethod  # __addAssetList  # {{{
    async def __addAssetList(cls, alist: AssetList) -> None:
        logger.debug(f"{cls.__name__}.__addAssetList()")

        # Format assets in postges value - ARRAY[figi]
        if alist.count > 0:
            pg_array = "ARRAY["
            for asset in alist:
                figi = f"'{asset.figi}', "
                pg_array += figi
            pg_array = pg_array[0:-2]  # remove ", " after last value
            pg_array += "]"
        else:
            pg_array = "'{}'::text[]"

        # If alist.name is exist - delete
        request = f"""
            DELETE FROM "AssetList"
            WHERE
                name = '{alist.name}';
            """
        await cls.transaction(request)

        # Add asset list
        request = f"""
        INSERT INTO "AssetList" (
            name,
            assets
            )
        VALUES (
            '{alist.name}',
            {pg_array}
        );
        """
        await cls.transaction(request)

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
    @classmethod  # __addTradeList  # {{{
    async def __addTradeList(cls, tlist: TradeList) -> None:
        logger.debug(f"{cls.__name__}.__addTradeList()")

        # Format trades in postges array
        if tlist.count > 0:
            pg_array = "ARRAY["
            for trade in tlist:
                t_id = f"'{trade.trade_id}', "
                pg_array += t_id
            pg_array = pg_array[0:-2]  # remove ", " after last value
            pg_array += "]"
        else:
            pg_array = "'{}'::float[]"

        # If tlist.name is exist - delete
        request = f"""
            DELETE FROM "TradeList"
            WHERE
                name = '{tlist.name}';
            """
        await cls.transaction(request)

        # Add trade list
        request = f"""
            INSERT INTO "TradeList" (
                name, trades
                )
            VALUES
                ( '{tlist.name}', {pg_array} )
                ;
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addTrade  # {{{
    async def __addTrade(cls, trade: Trade) -> None:
        logger.debug(f"{cls.__name__}.__addTrade()")

        # Add trade
        request = f"""
            INSERT INTO "Trade" (
                trade_id, dt, status, strategy, version, type, figi
                )
            VALUES (
                '{trade.trade_id}',
                '{trade.dt}',
                '{trade.status.name}',
                '{trade.strategy}',
                '{trade.version}',
                '{trade.type.name}',
                '{trade.asset_id.figi}'
                );
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addOrder  # {{{
    async def __addOrder(cls, order: Order) -> None:
        # TODO: broker_id и тому подобные поля, где возможен NULL,
        # можно упростить код, если буду использовать для них не None
        # а пустую строку "" на своей стороне.
        # и над прайсами тоже подумать, на будущее - тоже если текстом
        # то будет проще, а всю работу по переводу из текста в флоат
        # или куда там надо можно переложить на класс Price
        logger.debug(f"{cls.__name__}.__addOrder()")

        # format prices
        if order.type.name == "MARKET":
            price, s_price, e_price = "NULL", "NULL", "NULL"
        elif order.type.name == "LIMIT":
            price, s_price, e_price = order.price, "NULL", "NULL"
        elif order.type.name == "STOP":
            price, s_price, e_price = (
                "NULL",
                order.stop_price,
                order.exec_price,
            )
        else:
            assert False, f"WTF??? Order type='{order.type}'"

        # format meta
        if order.meta is None:
            meta = "NULL"
        else:
            meta = f"$${order.meta}$$"

        # format trade_id
        trade_id = f"'{order.trade_id}'" if order.trade_id else "NULL"

        # format broker_id
        broker_id = f"'{order.broker_id}'" if order.broker_id else "NULL"

        # add
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
                exec_lots,
                exec_quantity,
                meta,
                broker_id
                )
            VALUES (
                '{order.order_id}',
                '{order.account_name}',
                '{order.type.name}',
                '{order.status.name}',
                '{order.direction.name}',
                '{order.asset_id.figi}',
                {order.lots},
                {order.quantity},
                {price},
                {s_price},
                {e_price},
                {trade_id},
                {order.exec_lots},
                {order.exec_quantity},
                {meta},
                {broker_id}
                );
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addOperation  # {{{
    async def __addOperation(cls, operation: Operation) -> None:
        logger.debug(f"{cls.__name__}.__addOperation()")

        if operation.meta is None:
            meta = "NULL"
        else:
            meta = f"$${meta}$$"

        request = f"""
            INSERT INTO "Operation" (
                operation_id,
                order_id,
                trade_id,
                account,
                dt,
                direction,
                figi,
                lots,
                quantity,
                price,
                amount,
                commission,
                meta
            )
            VALUES (
                '{operation.operation_id}',
                '{operation.order_id}',
                '{operation.trade_id}',
                '{operation.account_name}',
                '{operation.dt}',
                '{operation.direction.name}',
                '{operation.asset_id.figi}',
                {operation.lots},
                {operation.quantity},
                {operation.price},
                {operation.amount},
                {operation.commission},
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
    @classmethod  # __deleteAssetList  # {{{
    async def __deleteAssetList(cls, alist: AssetList, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteAssetList()")

        request = f"""
        DELETE FROM "AssetList" WHERE name = '{alist.name}';
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteBarsData  # {{{
    async def __deleteBarsData(cls, _Bar, kwargs: dict) -> None:
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
    @classmethod  # __deleteTradeList  # {{{
    async def __deleteTradeList(cls, tlist: TradeList, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteTradeList()")

        request = f"""
        DELETE FROM "TradeList" WHERE name = '{tlist.name}';
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

    @classmethod  # __updateTradeList  # {{{
    async def __updateTradeList(cls, tlist: TradeList) -> None:
        logger.debug(f"{cls.__name__}.__updateTradeList()")

        # Format trades in postges array
        # TODO: remove duplacate code below and in func __addTradeList
        # use cls.__format, и остальные преобразования туда перетащи.
        if tlist.count > 0:
            pg_array = "ARRAY["
            for trade in tlist:
                t_id = f"'{trade.trade_id}', "
                pg_array += t_id
            pg_array = pg_array[0:-2]  # remove ", " after last value
            pg_array += "]"
        else:
            pg_array = "'{}'::text[]"

        request = f"""
            UPDATE "TradeList"
            SET
                trades = {pg_array}
            WHERE
                name = '{tlist.name}';
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
                figi = '{trade.asset_id.figi}'
            WHERE
                trade_id = '{trade.trade_id}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __updateOrder  # {{{
    async def __updateOrder(cls, order: Order) -> None:
        logger.debug(f"{cls.__name__}.__updateOrder()")

        # format meta
        if order.meta is None:
            meta = "NULL"
        else:
            meta = f"$${order.meta}$$"

        # format trade_id
        trade_id = f"'{order.trade_id}'" if order.trade_id else "NULL"

        # format broker_id
        broker_id = f"'{order.broker_id}'" if order.broker_id else "NULL"

        request = f"""
            UPDATE "Order"
            SET
                trade_id = {trade_id},
                status = '{order.status.name}',
                exec_lots = {order.exec_lots},
                exec_quantity = {order.exec_quantity},
                meta = {meta},
                broker_id = {broker_id}
            WHERE
                order_id = '{order.order_id}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __updateOperation  # {{{
    async def __updateOperation(cls, operation: Operation) -> None:
        logger.debug(f"{cls.__name__}.__updateOperation()")
        request = f"""
            UPDATE "Operation"
            SET
                trade_id = '{operation.trade_id}',
                commission = {operation.commission}
            WHERE
                operation_id = '{operation.operation_id}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __updateCache  # {{{
    async def __updateCache(cls, cache: _InstrumentInfoCache) -> None:
        logger.debug(f"{cls.__name__}.__updateCache()")

        # Delete old cache
        request = f"""
            DELETE FROM "Cache"
            WHERE
                source = '{cache.source.name}' AND
                type = '{cache.asset_type.name}'
                ;
            """
        await cls.transaction(request)

        # Format cache into postgres values
        def formatCache(cache: _InstrumentInfoCache) -> str:
            values = ""
            for i in cache.assets_info:
                pg_source = f"'{cache.source.name}'"
                pg_asset_type = f"'{cache.asset_type.name}'"
                # TODO: encoderJson наверное надо сюда втащить из класса
                # _InstrumentInfoCache, там он вообще нигде никак не
                # используется? или? а нет.. пока кэш в джсон тоже
                # дублируется на винт, но потом, когда просмотрщик
                # гуи будет для кэша, тогда этот метод можно будет
                # сюда втащить?
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
    def __getClassName(cls, obj: object | Class) -> str:
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
        # table name looks like: data."MOEX_SHARE_SBER_1M"
        logger.debug(f"{cls.__name__}.__getTableName()")

        bars_table_name = (
            f'data."{ID.exchange.name}_{ID.type.name}_{ID.ticker}_'
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
                {pg_condition}
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
        pg_figi = f"figi = '{ID.figi}'" if ID else "TRUE"

        # Create figi condition
        pg_data_type = f"type = '{data_type.name}'" if data_type else "TRUE"

        # Request data info
        request = f"""
            SELECT * FROM "Data"
            WHERE
                {pg_figi} AND {pg_data_type};
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
        pg_figi = f"figi = '{ID.figi}'"

        # Create figi condition
        pg_data_type = f"type = '{data_type.name}'"

        # Request data info
        request = f"""
            SELECT * FROM "Data"
            WHERE
                {pg_figi} AND {pg_data_type};
            """
        records = await cls.transaction(request)
        assert len(records) == 1
        record = records[0]
        return [record["first_dt"], record["last_dt"]]

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
    @classmethod  # __getAssetList  # {{{
    async def __getAssetList(cls, AssetList, kwargs: dict) -> Asset:
        logger.debug(f"{cls.__name__}.__getAssetList()")

        name = kwargs.get("name")
        get_only_names = kwargs.get("get_only_names")

        # create condition
        pg_condition = f"name = '{name}'" if name else "TRUE"

        # request
        request = f"""
            SELECT
                name,
                assets
            FROM "AssetList"
            WHERE
                {pg_condition}
            ;
            """
        records = await cls.transaction(request)

        # return list[str_names] if flag 'get_only_names'
        if get_only_names:
            all_names = list()
            for i in records:
                name = i["name"]
                all_names.append(name)
            return all_names

        # return list[AssetList] if no flag 'get_only_names'
        all_list = list()
        for record in records:
            alist = await AssetList.fromRecord(record)
            all_list.append(alist)

        return all_list

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
    @classmethod  # __getTradeList  # {{{
    async def __getTradeList(cls, TradeList, kwargs: dict) -> list[TradeList]:
        logger.debug(f"{cls.__name__}.__getTradeList()")

        name = kwargs["name"]
        request = f"""
            SELECT name, trades
            FROM "TradeList"
            WHERE name = '{name}'
            ;
            """
        records = await cls.transaction(request)

        all_trade_lists = list()
        for i in records:
            tlist = await TradeList.fromRecord(i)
            all_trade_lists.append(tlist)

        return all_trade_lists

    # }}}
    @classmethod  # __getTrade  # {{{
    async def __getTrade(cls, Trade, kwargs: dict) -> list[Trades]:
        logger.debug(f"{cls.__name__}.__getTrade()")

        trade_id = kwargs.get("trade_id")
        strategy = kwargs.get("strategy")
        statuses = kwargs.get("status")
        begin = kwargs.get("begin")
        end = kwargs.get("end")

        def condition(strategy, statuses, begin, end) -> str:  # {{{
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

            pg_condition = (
                f"{pg_strategy} AND {pg_statuses} AND "
                f"{pg_begin} AND {pg_end}"
            )
            return pg_condition

        # }}}

        # Create condition
        if trade_id:
            pg_condition = f"trade_id = '{trade_id}'"
        else:
            pg_condition = condition(strategy, statuses, begin, end)

        # Request trades
        request = f"""
            SELECT trade_id, dt, status, strategy, version, type, figi
            FROM "Trade"
            WHERE {pg_condition}
            ORDER BY dt
            ;
            """
        trade_records = await cls.transaction(request)

        # Create 'list' of 'Trade' objects from 'Records'
        all_trades = list()
        for i in trade_records:
            trade = await Trade.fromRecord(i)
            all_trades.append(trade)

        return all_trades

    # }}}
    @classmethod  # __getOperations  # {{{
    async def __getOperations(
        cls, Operation, kwargs: dict
    ) -> list[Operation]:
        logger.debug(f"{cls.__name__}.__getOperations()")

        trade_id = kwargs.get("trade_id")
        operation_id = kwargs.get("operation_id")

        if trade_id:
            pg_condition = f"trade_id = '{trade_id}'"
        elif operation_id:
            pg_condition = f"operation_id = '{operation_id}'"
        else:
            pg_condition = "TRUE"  # return all operations

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
            WHERE {pg_condition}
            ORDER BY dt
            ;
            """
        op_records = await cls.transaction(request)

        # Create 'list' of 'Operation' objects from 'Records'
        op_list = list()
        for i in op_records:
            op = await Operation.fromRecord(i)
            op_list.append(op)

        return op_list

    # }}}
    @classmethod  # __getOrders  # {{{
    async def __getOrders(cls, Order, kwargs: dict) -> list[Order]:
        logger.debug(f"{cls.__name__}.__getOrders()")

        trade_id = kwargs.get("trade_id")
        order_id = kwargs.get("order_id")

        # create condition
        if trade_id:
            pg_condition = f"trade_id = '{trade_id}'"
        elif order_id:
            pg_condition = f"order_id = '{order_id}'"
        else:
            pg_condition = "TRUE"  # return all orders

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
                exec_lots,
                exec_quantity,
                meta,
                broker_id
            FROM "Order"
            WHERE {pg_condition}
            ;
            """
        order_records = await cls.transaction(request)

        # Create 'list' of 'Order' objects from 'Records'
        order_list = list()
        for i in order_records:
            order = await Order.fromRecord(i)
            order_list.append(order)

        return order_list

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
