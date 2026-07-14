from mongomock.asynchronous.command_cursor import AsyncCommandCursor
from mongomock.asynchronous.cursor import AsyncCursor


class AsyncCollection:
    """Mirrors pymongo's AsyncCollection API on top of a mongomock Collection."""

    def __init__(self, database, delegate):
        self._database = database
        self._delegate = delegate

    def __getitem__(self, name):
        return AsyncCollection(self._database, self._delegate[name])

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError(f"AsyncCollection has no attribute '{attr}'.")
        return self[attr]

    def __repr__(self):
        return f"AsyncCollection({self._database!r}, '{self._delegate.name}')"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._delegate == other._delegate
        return NotImplemented

    def __hash__(self):
        return hash(self._delegate)

    @property
    def database(self):
        return self._database

    @property
    def name(self):
        return self._delegate.name

    @property
    def full_name(self):
        return self._delegate.full_name

    @property
    def codec_options(self):
        return self._delegate.codec_options

    @property
    def read_preference(self):
        return self._delegate.read_preference

    @property
    def read_concern(self):
        return self._delegate.read_concern

    @property
    def write_concern(self):
        return self._delegate.write_concern

    def find(self, *args, **kwargs):
        return AsyncCursor(self._delegate.find(*args, **kwargs), self)

    def find_raw_batches(self, *args, **kwargs):
        return self._delegate.find_raw_batches(*args, **kwargs)

    def with_options(self, *args, **kwargs):
        return AsyncCollection(self._database, self._delegate.with_options(*args, **kwargs))

    async def aggregate(self, *args, **kwargs):
        return AsyncCommandCursor(self._delegate.aggregate(*args, **kwargs))

    async def aggregate_raw_batches(self, *args, **kwargs):
        return self._delegate.aggregate_raw_batches(*args, **kwargs)

    async def bulk_write(self, *args, **kwargs):
        return self._delegate.bulk_write(*args, **kwargs)

    async def count_documents(self, *args, **kwargs):
        return self._delegate.count_documents(*args, **kwargs)

    async def create_index(self, *args, **kwargs):
        return self._delegate.create_index(*args, **kwargs)

    async def create_indexes(self, *args, **kwargs):
        return self._delegate.create_indexes(*args, **kwargs)

    async def delete_many(self, *args, **kwargs):
        return self._delegate.delete_many(*args, **kwargs)

    async def delete_one(self, *args, **kwargs):
        return self._delegate.delete_one(*args, **kwargs)

    async def distinct(self, *args, **kwargs):
        return self._delegate.distinct(*args, **kwargs)

    async def drop(self, *args, **kwargs):
        return self._delegate.drop(*args, **kwargs)

    async def drop_index(self, *args, **kwargs):
        return self._delegate.drop_index(*args, **kwargs)

    async def drop_indexes(self, *args, **kwargs):
        return self._delegate.drop_indexes(*args, **kwargs)

    async def estimated_document_count(self, *args, **kwargs):
        return self._delegate.estimated_document_count(*args, **kwargs)

    async def find_one(self, *args, **kwargs):
        return self._delegate.find_one(*args, **kwargs)

    async def find_one_and_delete(self, *args, **kwargs):
        return self._delegate.find_one_and_delete(*args, **kwargs)

    async def find_one_and_replace(self, *args, **kwargs):
        return self._delegate.find_one_and_replace(*args, **kwargs)

    async def find_one_and_update(self, *args, **kwargs):
        return self._delegate.find_one_and_update(*args, **kwargs)

    async def index_information(self, *args, **kwargs):
        return self._delegate.index_information(*args, **kwargs)

    async def insert_many(self, *args, **kwargs):
        return self._delegate.insert_many(*args, **kwargs)

    async def insert_one(self, *args, **kwargs):
        return self._delegate.insert_one(*args, **kwargs)

    async def list_indexes(self, *args, **kwargs):
        return AsyncCommandCursor(self._delegate.list_indexes(*args, **kwargs))

    async def options(self, *args, **kwargs):
        raise NotImplementedError('Mongomock does not support collection.options yet')

    async def rename(self, *args, **kwargs):
        return self._delegate.rename(*args, **kwargs)

    async def replace_one(self, *args, **kwargs):
        return self._delegate.replace_one(*args, **kwargs)

    async def update_many(self, *args, **kwargs):
        return self._delegate.update_many(*args, **kwargs)

    async def update_one(self, *args, **kwargs):
        return self._delegate.update_one(*args, **kwargs)

    async def watch(self, *args, **kwargs):
        raise NotImplementedError('Mongomock does not support watch yet')
