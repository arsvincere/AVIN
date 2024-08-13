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

import asyncpg

from avin.const import Usr
from avin.logger import logger

__all__ = ("Keeper",)


class Keeper:
    USER = Usr.PG_USER
    DATABASE = Usr.PG_DATABASE
    HOST = Usr.PG_HOST

    @classmethod  # transaction# {{{
    async def transaction(cls, sql_request: str):
        try:
            conn = await asyncpg.connect(
                user=cls.USER, database=cls.DATABASE, host=cls.HOST
            )
            values = await conn.fetch(sql_request)
            await conn.close()
            return values
        except asyncpg.exceptions.NumericValueOutOfRangeError as err:
            logger.error(err)
            logger.error(f"Request:\n{sql_request}")

    # }}}
    @classmethod  # createDataBase# {{{
    async def createDataBase(cls):
        # await cls.__createEnums()
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

    # }}}
    @classmethod  # info# {{{
    async def info(cls, source: Source, asset_type: AssetType, **kwargs):
        """Looks for information about the asset in the cache.

        Returns a list of dictionaries with information about assets
        suitable for a request 'kwargs'

        """

        # remove None values
        none_keys = [key for key in kwargs if kwargs[key] is None]
        for i in none_keys:
            kwargs.pop(i)

        # create source condition
        if source is None:
            pg_source = "TRUE"
        else:
            pg_source = f"source = '{source.name}'"

        # create asset_type condition
        if asset_type is None:
            pg_asset_type = "TRUE"
        else:
            pg_asset_type = f"type = '{asset_type.name}'"

        # create kwarg condition
        if not kwargs:
            pg_kwargs = "TRUE"
        else:
            json_string = json.dumps(kwargs, ensure_ascii=False)
            pg_kwargs = f"info @> '{json_string}'"

        # request assets info records
        request = f"""
            SELECT
                info
            FROM "Cache"
            WHERE {pg_source} AND {pg_asset_type} AND {pg_kwargs};
            """
        res = await cls.transaction(request)

        # extract info dicts from records
        assets_info = list()
        for record in res:
            json_string = record["info"]
            info_dict = json.loads(json_string)
            assets_info.append(info_dict)

        return assets_info

    # }}}
    @classmethod  # add# {{{
    async def add(cls, obj):
        if inspect.isclass(obj):
            class_name = obj.__name__
        else:
            class_name = obj.__class__.__name__

        methods = {
            "MOEX": cls.__addExchange,
            "SPB": cls.__addExchange,
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
            "_BarsData": cls.__addBarsData,
        }
        method = methods[class_name]
        await method(obj)

    # }}}
    @classmethod  # delete# {{{
    async def delete(cls, obj, **kwargs):
        if inspect.isclass(obj):
            class_name = obj.__name__
        else:
            class_name = obj.__class__.__name__

        methods = {
            "MOEX": cls.__deleteExchange,
            "SPB": cls.__deleteExchange,
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
        method = methods[class_name]
        await method(obj, kwargs)

    # }}}
    @classmethod  # update# {{{
    async def update(cls, obj):
        if inspect.isclass(obj):
            class_name = obj.__name__
        else:
            class_name = obj.__class__.__name__

        methods = {
            "Trade": cls.__updateTrade,
            "Market": cls.__updateOrder,
            "Limit": cls.__updateOrder,
            "Stop": cls.__updateOrder,
            "_InstrumentInfoCache": cls.__updateCache,
        }
        method = methods[class_name]
        await method(obj)

    # }}}
    @classmethod  # get# {{{
    async def get(cls, what: Class, **kwargs):
        assert inspect.isclass(what)

        methods = {
            "InstrumentId": cls.__getInstrumentId,
            "Asset": cls.__getAsset,
            "Trade": cls.__getTrades,
            "Operation": cls.__getOperations,
            "Order": cls.__getOrders,
            "_Bar": cls.__getBars,
        }
        method = methods[what.__name__]
        result = await method(what, kwargs)
        return result

    # }}}

    @classmethod  # __addExchange# {{{
    async def __addExchange(cls, exchange: Exchange):
        request = f"""
        INSERT INTO "Exchange"(name)
        VALUES ('{exchange.name}');
        """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __addAsset# {{{
    async def __addAsset(cls, asset: Asset | Id):
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
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __addBarsData# {{{
    async def __addBarsData(cls, data: _BarsData):
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
        res = await cls.transaction(request)

        # Create table if not exist
        table_name = cls.__getTableName(data.ID, data.data_type)
        await cls.__createBarsDataTable(table_name)

        # If exist - delete old data at the same period
        request = f"""
            DELETE FROM data."{table_name}"
            WHERE
                '{data.first_dt}' <= dt AND dt <= '{data.last_dt}'
                ;
            """
        res = await cls.transaction(request)

        # Format bars data in postges value
        values = ""
        for b in data.bars:
            dt = f"'{b.dt.isoformat()}'"
            val = f"({dt},{b.open},{b.high},{b.low},{b.close},{b.vol}),\n"
            values += val
        values = values[0:-2]  # remove ",\n" after last value

        # Add bars data
        request = f"""
        INSERT INTO data."{table_name}" (dt, open, high, low, close, volume)
        VALUES
            {values}
            ;
        """
        res = await cls.transaction(request)

        # Update table "Data" - information about availible market data
        request = f"""
            DELETE FROM "Data"
            WHERE
                figi = '{data.ID.figi}' AND
                type = '{data.data_type.name}'
                ;
            """
        res = await cls.transaction(request)
        request = f"""
            INSERT INTO "Data"(figi, type, source, first_dt, last_dt)
            VALUES (
                '{data.ID.figi}',
                '{data.data_type.name}',
                '{data.source.name}',
                (SELECT min(dt) FROM data."{table_name}"),
                (SELECT max(dt) FROM data."{table_name}")
            );
            """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __addAccount# {{{
    async def __addAccount(cls, account: Account):
        request = f"""
        INSERT INTO "Account" (
            name,
            broker
            )
        VALUES (
            '{account.name}',
            '{account.broker.name}'
            );
        """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __addStrategy# {{{
    async def __addStrategy(cls, strategy: Strategy):
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
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __addTrade# {{{
    async def __addTrade(cls, trade: Trade):
        request = f"""
            INSERT INTO "Trade" (
                trade_id, dt, status, strategy, version, type, figi
                )
            VALUES (
                {trade.ID},
                '{trade.dt}',
                '{trade.status.name}',
                '{trade.strategy}',
                '{trade.version}',
                '{trade.type.name}',
                '{trade.asset.figi}'
                );
            """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __addOrder# {{{
    async def __addOrder(cls, order: Order):
        assert order.trade_ID is not None
        assert order.account_name is not None

        # Используется проверка типа ордера через строки...
        # Логично было бы использовать enum Type из класса Order, например так:
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
                {order.ID},
                '{order.account_name}',
                '{order.type.name}',
                '{order.status.name}',
                '{order.direction.name}',
                '{order.asset.figi}',
                {order.lots},
                {order.quantity},
                {price},
                {stop_price},
                {exec_price},
                {order.trade_ID},
                {meta}
                );
            """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __addOperation# {{{
    async def __addOperation(cls, operation: Operation):
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
                {operation.ID},
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

        res = await cls.transaction(request)
        return res

    # }}}

    @classmethod  # __deleteExchange# {{{
    async def __deleteExchange(cls, exchange: Exchange):
        request = f"""
        DELETE FROM "Exchange" WHERE name = '{exchange.name}';
        """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __deleteAsset# {{{
    async def __deleteAsset(cls, asset: Asset):
        request = f"""
        DELETE FROM "Asset" WHERE figi = '{asset.figi}';
        """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __deleteBarsData# {{{
    async def __deleteBarsData(cls, _Bar: class_, kwargs):
        ID = kwargs["ID"]
        data_type = kwargs["data_type"]
        begin = kwargs.get("begin")
        end = kwargs.get("end")

        if begin and end:
            pg_period = "'{begin}' <= dt AND dt < '{end}'"
        else:
            pg_period = "TRUE"

        # Delete bars
        table_name = cls.__getTableName(ID, data_type)
        request = f"""
            DELETE FROM data."{table_name}"
            WHERE
                {pg_period}
            """
        res = await cls.transaction(request)

        # Delete table & info if its empty
        request = f"""
            SELECT * FROM data."{table_name}"
            """
        res = await cls.transaction(request)
        if not res:
            request = f"""
                DROP TABLE data."{table_name}";
                """
            res = await cls.transaction(request)
            request = f"""
                DELETE FROM "Data"
                WHERE
                    figi = '{ID.figi}' AND
                    type = '{data_type.name}'
                """
            res = await cls.transaction(request)

        # Delete asset if its not have market data
        request = f"""
            SELECT * FROM "Data"
            WHERE
                figi = '{ID.figi}'
            """
        res = await cls.transaction(request)
        if not res:
            request = f"""
                DELETE FROM "Asset"
                WHERE
                    figi = '{ID.figi}'
                """
            res = await cls.transaction(request)

    # }}}
    @classmethod  # __deleteAccount# {{{
    async def __deleteAccount(cls, account: Account):
        request = f"""
        DELETE FROM "Account" WHERE name = '{account.name}';
        """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __deleteStrategy# {{{
    async def __deleteStrategy(cls, strategy: Strategy):
        request = f"""
        DELETE FROM "Strategy"
        WHERE name = '{strategy.name}' AND version = '{strategy.version}';
        """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __deleteTrade# {{{
    async def __deleteTrade(cls, trade: Trade):
        request = f"""
            DELETE FROM "Trade"
            WHERE trade_id = '{trade.ID}';
            """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __deleteOrder# {{{
    async def __deleteOrder(cls, order: Order):
        request = f"""
            DELETE FROM "Order"
            WHERE order_id = '{order.ID}';
            """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __deleteOperation# {{{
    async def __deleteOperation(cls, operation: Operation):
        request = f"""
            DELETE FROM "Operation"
            WHERE operation_id = '{operation.ID}';
            """
        res = await cls.transaction(request)
        return res

    # }}}

    @classmethod  # __updateTrade# {{{
    async def __updateTrade(cls, trade: Trade):
        request = f"""
            UPDATE "Trade"
            SET
                dt = '{trade.dt}',
                status = '{trade.status.name}',
                strategy = '{trade.strategy}',
                version = '{trade.version}',
                type = '{trade.type.name}',
                figi = '{trade.asset.figi}'
            WHERE
                trade_id = '{trade.ID}';
            """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __updateOrder# {{{
    async def __updateOrder(cls, order: Order):
        request = f"""
            UPDATE "Order"
            SET
                status = '{order.status.name}'
            WHERE
                order_id = '{order.ID}';
            """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __updateCache# {{{
    async def __updateCache(cls, cache: _InstrumentInfoCache):
        # delete old cache
        request = f"""
            DELETE FROM "Cache"
            WHERE
                source = '{cache.source.name}' AND
                type = '{cache.asset_type.name}'
                ;
            """
        res = await cls.transaction(request)

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
        res = await cls.transaction(request)

        # update "last_update" datetime
        return res

    # }}}

    @classmethod  # __getInstrumentId # {{{
    async def __getInstrumentId(cls, InstrumentId, kwargs: dict):
        figi = kwargs.get("figi")

        if figi:
            pg_figi = "figi = {figi}"
        else:
            pg_figi = "TRUE"

        request = f"""
            SELECT
                exchange,
                type,
                ticker,
                name,
                figi
            FROM "Asset"
            WHERE {pg_figi}
            ;
            """
        asset_records = await cls.transaction(request)
        id_list = list()
        for i in asset_records:
            ID = InstrumentId.fromRecord(i)
            id_list.append(ID)
        return id_list

    # }}}
    @classmethod  # __getDataType # {{{
    async def __getDataType(cls, DataType, kwargs: dict):
        ID = kwargs["ID"]

        request = """
            SELECT table_name FROM information_schema.tables
            WHERE
                table_schema='data';
            """
        asset_record = await cls.transaction(request)

        if figi:
            pg_figi = "figi = {figi}"
        else:
            pg_figi = "TRUE"

        request = """
            SELECT
                exchange,
                type,
                ticker,
                name,
                figi
            FROM "Asset"
            WHERE pg_figi
            ;
            """
        asset_record = await cls.transaction(request)

        ID = InstrumentId.fromRecord(asset_record)
        return ID

    # }}}
    @classmethod  # __getAsset # {{{
    async def __getAsset(cls, asset_class, kwargs: dict):
        """Search asset

        Looks for assets only among those for which exchange data are loaded.
        Returns the asset.
        """
        # TODO добавить поиск по тикеру типу и бирже
        figi = kwargs.get("figi")

        request = f"""
            SELECT
                exchange,
                type,
                ticker,
                name,
                figi
            FROM "Asset"
            WHERE figi = {figi}
            ;
            """
        asset_record = await cls.transaction(request)

        asset = asset_class.fromRecord(asset_record)
        return asset

    # }}}
    @classmethod  # __getBars # {{{
    async def __getBars(cls, bar_class, kwargs):
        ID = kwargs["ID"]
        data_type = kwargs["data_type"]
        begin = kwargs.get("begin")
        end = kwargs.get("end")

        # create condition for begin-end:
        if begin is None and end is None:
            pg_period = "TRUE"
        else:
            pg_period = f"'{begin}' <= dt AND dt < '{end}'"

        # request
        table_name = cls.__getTableName(ID, data_type)
        request = f"""
            SELECT dt, open, high, low, close, volume
            FROM data."{table_name}"
            WHERE {pg_period}
            ORDER BY dt
            ;
            """
        res = await cls.transaction(request)

        # create bars from records
        bars = list()
        for i in res:
            bar = bar_class.fromRecord(i)
            bars.append(bar)
        return bars

    # }}}
    @classmethod  # __getTrades # {{{
    async def __getTrades(cls, trade_class, kwargs: dict):
        strategy = kwargs.get("strategy")
        statuses = kwargs.get("status")
        begin = kwargs.get("begin")
        end = kwargs.get("end")

        # create condition for strategy:
        if strategy is None:
            pg_strategy = "TRUE"
        else:
            pg_strategy = f"(strategy = '{strategy.name}' AND version = '{strategy.version}')"

        # create condition for statuses, like this:
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

        # create condition for begin datetime:
        if begin is None:
            pg_begin = "TRUE"
        else:
            pg_begin = f"dt >= '{begin}'"

        # create condition for end datetime:
        if end is None:
            pg_end = "TRUE"
        else:
            pg_end = f"dt < '{end}'"

        request = f"""
            SELECT trade_id, dt, status, strategy, version, type, figi
            FROM "Trade"
            WHERE {pg_strategy} AND {pg_statuses} AND {pg_begin} AND {pg_end}
            ORDER BY dt
            ;
            """
        trade_records = await cls.transaction(request)

        # create Trade objects
        tlist = list()
        for i in trade_records:
            trade = await trade_class.fromRecord(i)
            tlist.append(trade)

        return tlist

    # }}}
    @classmethod  # __getOperations # {{{
    async def __getOperations(cls, operation_class, kwargs):
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

        # create operation objects
        op_list = list()
        for i in op_records:
            op = operation_class.fromRecord(i)
            op_list.append(op)

        return op_list

    # }}}
    @classmethod  # __getOrders # {{{
    async def __getOrders(cls, order_class, kwargs):
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

        # create order objects
        order_list = list()
        for i in order_records:
            order = order_class.fromRecord(i)
            order_list.append(order)

        return order_list

    # }}}

    @classmethod  # __createEnums# {{{
    async def __createEnums(cls):
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
    @classmethod  # __createCacheTable# {{{
    async def __createCacheTable(cls):
        request = """
        CREATE TABLE IF NOT EXISTS "Cache" (
            source "DataSource",
            type "AssetType",
            info jsonb
            );
        """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __createExchangeTable# {{{
    async def __createExchangeTable(cls):
        request = """
        CREATE TABLE IF NOT EXISTS "Exchange" (
            name text PRIMARY KEY
            );
        """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __createAssetTable# {{{
    async def __createAssetTable(cls):
        request = """
        CREATE TABLE IF NOT EXISTS "Asset" (
            figi text PRIMARY KEY,
            type "AssetType",
            exchange text REFERENCES "Exchange"(name),
            ticker text,
            name text
            );
        """
        res = await cls.transaction(request)

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
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __createDataTable# {{{
    async def __createDataTable(cls):
        request = """
        CREATE TABLE IF NOT EXISTS "Data" (
            figi text REFERENCES "Asset"(figi),
            type "DataType",
            source "DataSource",
            first_dt TIMESTAMP WITH TIME ZONE,
            last_dt TIMESTAMP WITH TIME ZONE
            );
        """
        res = await cls.transaction(request)

        return res

    # }}}
    @classmethod  # __createBarsDataTable# {{{
    async def __createBarsDataTable(cls, table_name: str):
        request = f"""
        CREATE TABLE IF NOT EXISTS data."{table_name}" (
            dt TIMESTAMP WITH TIME ZONE PRIMARY KEY,
            open float,
            high float,
            low float,
            close float,
            volume bigint
            );
            """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __createAccountTable# {{{
    async def __createAccountTable(cls):
        request = """
        CREATE TABLE IF NOT EXISTS "Account" (
            name text PRIMARY KEY,
            broker text
            );
        """
        res = await cls.transaction(request)

        # if not exist, create system account for back-tester
        request = """
        SELECT name FROM "Account"
        WHERE name = '_backtest'
        """
        res = await cls.transaction(request)
        if not res:
            request = """
            INSERT INTO "Account" (
                name,
                broker
                )
            VALUES
                ('_backtest', 'ArsVincere')
                ;
            """
            res = await cls.transaction(request)

        # if not exist, create system account for unit-tests
        request = """
        SELECT name FROM "Account"
        WHERE name = '_unittest'
        """
        res = await cls.transaction(request)
        if not res:
            request = """
            INSERT INTO "Account" (
                name,
                broker
                )
            VALUES
                ('_unittest', 'ArsVincere')
                ;
            """
            res = await cls.transaction(request)

        return res

    # }}}
    @classmethod  # __createStrategyTable# {{{
    async def __createStrategyTable(cls):
        request = """
        CREATE TABLE IF NOT EXISTS "Strategy" (
            name text,
            version text,
            CONSTRAINT strategy_pkey PRIMARY KEY (name, version)
            );
        """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __createTradeTable# {{{
    async def __createTradeTable(cls):
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
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __createOrderTable# {{{
    async def __createOrderTable(cls):
        # TODO добавить частично исполненный - сколько там уже исполнено
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
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __createOperationTable# {{{
    async def __createOperationTable(cls):
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
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __createMarketDataScheme# {{{
    async def __createMarketDataScheme(cls):
        request = """
        CREATE SCHEMA IF NOT EXISTS data
        """
        res = await cls.transaction(request)
        return res

    # }}}
    @classmethod  # __getTableName# {{{
    def __getTableName(cls, ID: InstrumentId, data_type):
        # table_name = f"{asset.figi}_{data_type.name}"
        table_name = (
            f"{ID.exchange.name}_{ID.type.name}_{ID.ticker}_{data_type.value}"
        )
        return table_name

    # }}}
