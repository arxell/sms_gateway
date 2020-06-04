# type: ignore
import copy
from contextlib import asynccontextmanager
from contextvars import ContextVar
from functools import wraps
from logging import getLogger
from typing import Tuple

from aiopg.sa import Engine, SAConnection, create_engine
from psycopg2.extensions import adapt as sqlescape
from sqlalchemy import alias, func, orm, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.base import DEFAULT_STATE_ATTR, _generative
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import ClauseElement

from app.conf.settings import settings

logger = getLogger(__name__)
__db_pool: Engine = None
context_conn: ContextVar = ContextVar('async_connection')


class BaseModelClass:
    def _get_pk_field(self):
        for field_name, field in self.__mapper__.columns.items():
            if field.primary_key:
                return field_name, field

    @property
    def _pk(self):
        key, _ = self._get_pk_field()
        return getattr(self, key)

    @_pk.setter
    def _pk(self, value):
        key, _ = self._get_pk_field()
        setattr(self, key, value)

    def to_dict(self):
        values = copy.deepcopy(self.__dict__)
        if DEFAULT_STATE_ATTR in values:
            del values[DEFAULT_STATE_ATTR]
        return values

    @hybrid_property
    def query(self):
        return AsyncQuery(self)

    @classmethod
    async def bulk_insert(cls, connection, values_list):

        result = await connection.execute(cls.__table__.insert().values(values_list))
        try:

            return result.rowcount
        finally:
            result.close()

    def _prepare_saving(self, only_fields=None, exclude_fields=None, force_insert=False):
        """
        Returns primary key field and values, which need to be saved
        """
        values = self.to_dict()
        if only_fields:
            only_fields = [k.key if isinstance(k, InstrumentedAttribute) else k for k in only_fields]
            values = {k: v for k, v in values.items() if k in only_fields}
        if exclude_fields:
            exclude_fields = [k.key if isinstance(k, InstrumentedAttribute) else k for k in exclude_fields]
            values = {k: v for k, v in values.items() if k not in exclude_fields}

        pk_field_name, pk_field = self._get_pk_field()
        if pk_field_name in values:
            if force_insert is False:
                values.pop(pk_field_name)
        return pk_field, values

    def delete_sync(self, connection):
        _, pk_field = self._get_pk_field()
        connection.execute(self.__table__.delete().where(pk_field == self._pk))

    async def delete(self, connection):
        _, pk_field = self._get_pk_field()
        cursor = await connection.execute(self.__table__.delete().where(pk_field == self._pk))
        cursor.close()

    def save_sync(self, connection, only_fields=None, exclude_fields=None, force_insert=False):
        pk_field, values = self._prepare_saving(
            only_fields=only_fields, exclude_fields=exclude_fields, force_insert=force_insert
        )

        def _execute(query, values):
            result = connection.execute(query.values(**values).returning(pk_field))
            if result.returns_rows:
                _id = result.scalar()
                if _id:
                    self._pk = _id
                    return True
            else:
                return result.rowcount > 0

        if not self._pk or (force_insert is True):
            # INSERT flow
            result = _execute(self.__table__.insert(), values)

        else:
            # Update flow
            result = _execute(self.__table__.update().where(pk_field == self._pk), values)
        return result

    async def refresh(self, connection):
        _, pk_field = self._get_pk_field()
        res = dict(await fetchone(connection, self.__table__.select().where(pk_field == self._pk).limit(1)))
        for key, value in res.items():
            setattr(self, key, value)

    def refresh_sync(self, connection):
        _, pk_field = self._get_pk_field()
        res = dict(connection.execute(self.__table__.select().where(pk_field == self._pk).limit(1)).fetchone())
        for key, value in res.items():
            setattr(self, key, value)

    async def save(self, connection, only_fields=None, exclude_fields=None, force_insert=False):
        pk_field, values = self._prepare_saving(
            only_fields=only_fields, exclude_fields=exclude_fields, force_insert=force_insert
        )

        async def _execute(query, values):
            cursor = await connection.execute(query.values(**values).returning(pk_field))
            try:
                if cursor.returns_rows:
                    _id = await cursor.scalar()
                    if _id:
                        self._pk = _id
                        return True
                else:
                    return cursor.rowcount > 0
            finally:
                cursor.close()

        if not self._pk or (force_insert is True):
            # INSERT flow
            return await _execute(self.__table__.insert(), values)

        else:
            cursor = await connection.execute(self.__table__.update().where(pk_field == self._pk).values(**values))
            try:
                if cursor.rowcount:
                    return True
            finally:
                cursor.close()
        return False

    async def upsert(self, connection, constraint_column=None):
        if constraint_column not in [column.name for column in self.__table__.c]:
            raise Exception(f'Invalid constraint_column {constraint_column}')

        pk_field, values = self._prepare_saving()

        on_update_fields = {}
        for column in list(self.__table__.c):
            if column.onupdate and not values.get(column.name):
                on_update_fields[column.name] = column.onupdate.arg

        q = postgresql.insert(self.__table__).values(**values)

        values.update(on_update_fields)
        q = q.on_conflict_do_update(index_elements=[constraint_column], set_=values)

        cursor = await connection.execute(q.returning(pk_field))
        try:
            if cursor.returns_rows:
                _id = await cursor.scalar()
                if _id:
                    self._pk = _id
                    return True
            else:
                return cursor.rowcount > 0
        finally:
            cursor.close()


def _check_conn(meth):
    @wraps(meth)
    async def wrapper(self, *args, **kwargs):
        if self._async_conn is None and self._sync_conn is None and not self._auto_connection:
            raise ValueError('connection for query not specified')
        elif self._auto_connection:

            @asynccontextmanager
            async def context():
                async with connection_context() as conn:
                    self._async_conn = conn
                    yield
                self._async_conn = None

        else:

            @asynccontextmanager
            async def context():  # dummy context
                yield

        async with context():
            return await meth(self, *args, **kwargs)

    return wrapper


class AsyncQuery(orm.Query):
    def __init__(self, entities, session=None):
        self._sync_conn = self._async_conn = None
        self._auto_connection = False
        super().__init__(entities, session)

    @_generative()
    def with_async_conn(self, conn):
        self._async_conn = conn
        self._sync_conn = None

    @_generative()
    def with_sync_conn(self, conn):
        self._sync_conn = conn
        self._async_conn = None

    @_generative()
    def auto_connection(self):
        """
        Allows not to specify connection manually.
        If uses in `app.models.bases.connection_context`, connection from that context will be used
        (see its documentation for details)
        """
        self._auto_connection = True

    @_check_conn
    async def all(self):
        if self._async_conn is not None:
            raw_result = await fetchall(self._async_conn, self.statement)
        elif self._sync_conn is not None:
            raw_result = self._sync_conn.execute(self.statement)
        cls_ = self._entity_zero().class_
        return [cls_(**row) for row in raw_result]

    @_check_conn
    async def scalar(self):
        if self._async_conn is not None:
            return await scalar(self._async_conn, self.statement)
        elif self._sync_conn is not None:
            return self._sync_conn.scalar(self.statement)

    @_check_conn
    async def count(self):
        query = select([func.count('*')]).select_from(alias(self.statement))
        if self._async_conn is not None:
            return await scalar(self._async_conn, query)
        elif self._sync_conn is not None:
            return self._sync_conn.scalar(query)

    @_check_conn
    async def first(self):
        if self._async_conn is not None:
            raw_result = await first(self._async_conn, self.statement)
        elif self._sync_conn is not None:
            raw_result = list(self._sync_conn.execute(self.statement.limit(1)))[0]
        if raw_result is not None:
            return self._entity_zero().class_(**raw_result)

    @_check_conn
    async def update(self, values):
        if len(self._entities) != 1 and len(self._entities[0].entities) != 1:
            raise ValueError('only one model supported')
        table = self._entities[0].entities[0].__table__
        query = table.update().where(self.statement._whereclause).values(values)
        if self._async_conn:
            res = await self._async_conn.execute(query)
            res.close()
        elif self._sync_conn:
            res = self._sync_conn.execute(query)
        return res.rowcount

    @_check_conn
    async def get(self, obj_id):
        obj_class = self._entity_zero().class_
        obj = await self.filter(obj_class.id == obj_id).first()
        if obj is None:
            raise ValueError(f'object {obj_class} with id={obj_id} not found')
        return obj

    @_check_conn
    async def one(self):
        result = await self.first()
        if result is None:
            raise NoResultFound("No row was found for one()")
        return result

    @_check_conn
    async def delete(self):
        if len(self._entities) != 1 and len(self._entities[0].entities) != 1:
            raise ValueError('only one model supported')
        table = self._entities[0].entities[0].__table__
        query = table.delete().where(self.statement._whereclause)
        if self._async_conn:
            res = await self._async_conn.execute(query)
            res.close()
        elif self._sync_conn:
            res = self._sync_conn.execute(query)
        return res.rowcount


def compile_query(query):
    dialect = postgresql.dialect()
    compiled_query = query.compile(dialect=dialect)

    params = {}
    for k, v in compiled_query.params.items():
        if isinstance(v, str):
            params[k] = sqlescape(v.encode('utf-8'))
        else:
            params[k] = sqlescape(v)

    return compiled_query.string % params


async def _fetch(conn: SAConnection, query: ClauseElement, meth: str):
    if isinstance(query, AsyncQuery):
        query = query.statement
    res = await conn.execute(query)
    async with res.cursor:
        return await getattr(res, meth)()


async def first(conn: SAConnection, query: ClauseElement):
    return await _fetch(conn, query, 'first')


async def fetchall(conn: SAConnection, query: ClauseElement):
    return await _fetch(conn, query, 'fetchall')


async def fetchone(conn: SAConnection, query: ClauseElement):
    return await _fetch(conn, query, 'fetchone')


async def scalar(conn: SAConnection, query: ClauseElement):
    return await _fetch(conn, query, 'scalar')


@asynccontextmanager
async def connection_context():
    """
    Acquires connection from pool, releases it on exit from context.

    You can use it with `AsyncQuery.auto_connection()` method call:
    >>> async with connection_context():
    >>>     await Model.query.auto_connection().count()
    >>>     await AnotherModel.query.auto_connection().count()

    Each of queries will use the same connection here.
    Also, you can start transaction with this:
    >>> async with connection_context() as connection:
    >>>     await Model.query.auto_connection().count()
    >>>     async with connection.begin():
    >>>         obj = await AnotherModel.query.auto_connection().first()
    >>>         obj.attr = 1
    >>>         await obj.save(connection)
    """
    conn = context_conn.get(None)
    if conn is None:
        async with __db_pool.acquire() as conn:
            context_conn.set(conn)
            yield conn
        context_conn.set(None)
    else:
        yield conn


class PoolAlreadyInitialized(Exception):
    pass


def get_connection_config():
    return dict(
        host=settings.db.host,
        port=settings.db.port,
        username=settings.db.username,
        password=settings.db.password,
        database=settings.db.database,
    )


def get_connection_url() -> URL:
    return URL('postgres', **get_connection_config())


async def init_db():
    global __db_pool
    if __db_pool is not None:
        raise PoolAlreadyInitialized('database already initialized')

    __db_pool = await create_engine(
        **get_connection_url().translate_connect_args(username='user'),
        echo=settings.db.echo,
        minsize=settings.db.pool_min_size,
        maxsize=settings.db.pool_max_size,
        pool_recycle=settings.db.pool_recycle_seconds,
    )
    logger.info('database pool opened')
    return __db_pool


async def close_db():
    global __db_pool
    if __db_pool is not None:
        __db_pool.close()
        await __db_pool.wait_closed()
        logger.info('database pool closed')
        __db_pool = None


async def check_db_connection() -> Tuple[bool, str]:
    global __db_pool
    if __db_pool is None:
        return False, '__db_pool is None'

    try:
        async with connection_context() as conn:
            await conn.execute('select 1;')
    except Exception as exp:
        logger.exception('unknown connection error')
        return False, exp.__str__
    else:
        return True, ''


ModelBase = declarative_base(cls=BaseModelClass)
