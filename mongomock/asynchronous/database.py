from mongomock.asynchronous.collection import AsyncCollection


class AsyncDatabase:
    """Mirrors pymongo's AsyncDatabase API on top of a mongomock Database."""

    def __init__(self, client, delegate):
        self._client = client
        self._delegate = delegate

    def __getitem__(self, coll_name):
        return self.get_collection(coll_name)

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError(
                f"AsyncDatabase has no attribute '{attr}'. To access the {attr} collection, "
                f"use database['{attr}']."
            )
        return self[attr]

    def __repr__(self):
        return f"AsyncDatabase({self._client!r}, '{self._delegate.name}')"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._delegate == other._delegate
        return NotImplemented

    def __hash__(self):
        return hash(self._delegate)

    @property
    def client(self):
        return self._client

    @property
    def name(self):
        return self._delegate.name

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

    def get_collection(self, *args, **kwargs):
        return AsyncCollection(self, self._delegate.get_collection(*args, **kwargs))

    def with_options(self, *args, **kwargs):
        return AsyncDatabase(self._client, self._delegate.with_options(*args, **kwargs))

    async def aggregate(self, *args, **kwargs):
        raise NotImplementedError('Mongomock does not support database-level aggregate yet')

    async def command(self, *args, **kwargs):
        return self._delegate.command(*args, **kwargs)

    async def create_collection(self, *args, **kwargs):
        return AsyncCollection(self, self._delegate.create_collection(*args, **kwargs))

    async def cursor_command(self, *args, **kwargs):
        raise NotImplementedError('Mongomock does not support cursor_command yet')

    async def dereference(self, *args, **kwargs):
        return self._delegate.dereference(*args, **kwargs)

    async def drop_collection(self, name_or_collection, *args, **kwargs):
        if isinstance(name_or_collection, AsyncCollection):
            name_or_collection = name_or_collection._delegate
        return self._delegate.drop_collection(name_or_collection, *args, **kwargs)

    async def list_collection_names(self, *args, **kwargs):
        return self._delegate.list_collection_names(*args, **kwargs)

    async def list_collections(self, *args, **kwargs):
        return self._delegate.list_collections(*args, **kwargs)

    async def validate_collection(self, *args, **kwargs):
        raise NotImplementedError('Mongomock does not support validate_collection yet')

    async def watch(self, *args, **kwargs):
        raise NotImplementedError('Mongomock does not support watch yet')
