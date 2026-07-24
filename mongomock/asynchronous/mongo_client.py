from mongomock.asynchronous.command_cursor import AsyncCommandCursor
from mongomock.asynchronous.database import AsyncDatabase
from mongomock.mongo_client import MongoClient


class AsyncMongoClient:
    """Mirrors pymongo's AsyncMongoClient API on top of a mongomock MongoClient."""

    HOST = MongoClient.HOST
    PORT = MongoClient.PORT

    def __init__(
        self,
        host=None,
        port=None,
        document_class=dict,
        tz_aware=False,
        connect=True,
        _store=None,
        read_preference=None,
        type_registry=None,
        **kwargs,
    ):
        self._delegate = MongoClient(
            host=host,
            port=port,
            document_class=document_class,
            tz_aware=tz_aware,
            connect=connect,
            _store=_store,
            read_preference=read_preference,
            type_registry=type_registry,
            **kwargs,
        )

    def __getitem__(self, db_name):
        return self.get_database(db_name)

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError(
                f"AsyncMongoClient has no attribute '{attr}'. To access the {attr} database, "
                f"use client['{attr}']."
            )
        return self[attr]

    def __repr__(self):
        return f"mongomock.AsyncMongoClient('{self._delegate.host}', {self._delegate.port})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._delegate == other._delegate
        return NotImplemented

    def __hash__(self):
        return hash(self._delegate)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @property
    def address(self):
        return self._delegate.address

    @property
    def codec_options(self):
        return self._delegate.codec_options

    @property
    def is_mongos(self):
        return self._delegate.is_mongos

    @property
    def is_primary(self):
        return self._delegate.is_primary

    @property
    def read_preference(self):
        return self._delegate.read_preference

    def get_database(self, *args, **kwargs):
        return AsyncDatabase(self, self._delegate.get_database(*args, **kwargs))

    def get_default_database(self, *args, **kwargs):
        return AsyncDatabase(self, self._delegate.get_default_database(*args, **kwargs))

    def start_session(self, *args, **kwargs):
        return self._delegate.start_session(*args, **kwargs)

    async def aconnect(self):
        pass

    async def aclose(self):
        pass

    async def close(self):
        pass

    async def bulk_write(self, *args, **kwargs):
        raise NotImplementedError('Mongomock does not support client-level bulk_write yet')

    async def drop_database(self, name_or_db):
        if isinstance(name_or_db, AsyncDatabase):
            name_or_db = name_or_db._delegate
        return self._delegate.drop_database(name_or_db)

    async def list_database_names(self):
        return self._delegate.list_database_names()

    async def list_databases(self, *args, **kwargs):
        return AsyncCommandCursor(self._delegate.list_databases(*args, **kwargs))

    async def server_info(self, *args, **kwargs):
        return self._delegate.server_info()

    async def watch(self, *args, **kwargs):
        raise NotImplementedError('Mongomock does not support watch yet')
