class AsyncCursor:
    """Mirrors pymongo's AsyncCursor API on top of a mongomock Cursor.

    Which methods are coroutines and which are synchronous (e.g. chaining methods like
    sort/skip/limit) follows pymongo's asynchronous API exactly.
    """

    def __init__(self, delegate, collection):
        self._delegate = delegate
        self._collection = collection

    @property
    def alive(self):
        return self._delegate.alive

    @property
    def collection(self):
        return self._collection

    @property
    def session(self):
        return self._delegate.session

    def allow_disk_use(self, allow_disk_use=False):
        self._delegate.allow_disk_use(allow_disk_use)
        return self

    def batch_size(self, batch_size):
        self._delegate.batch_size(batch_size)
        return self

    def clone(self):
        return AsyncCursor(self._delegate.clone(), self._collection)

    def collation(self, collation):
        self._delegate._collation = collation
        return self

    def comment(self, comment):
        return self

    def hint(self, index):
        self._delegate.hint(index)
        return self

    def limit(self, limit):
        self._delegate.limit(limit)
        return self

    def max_time_ms(self, max_time_ms):
        self._delegate.max_time_ms(max_time_ms)
        return self

    def skip(self, skip):
        self._delegate.skip(skip)
        return self

    def sort(self, key_or_list, direction=None):
        self._delegate.sort(key_or_list, direction)
        return self

    def where(self, code):
        raise NotImplementedError('Mongomock does not support cursor.where yet')

    def __getitem__(self, index):
        raise IndexError('AsyncCursor does not support indexing')

    async def close(self):
        self._delegate.close()

    async def distinct(self, key):
        return self._delegate.distinct(key)

    async def explain(self):
        raise NotImplementedError('Mongomock does not support explain yet')

    async def next(self):
        try:
            return next(self._delegate)
        except StopIteration:
            # PEP 479: a StopIteration escaping a coroutine would become a RuntimeError.
            raise StopAsyncIteration from None

    __anext__ = next

    async def rewind(self):
        self._delegate.rewind()
        return self

    async def to_list(self, length=None):
        return self._delegate.to_list(length)

    def __aiter__(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._delegate.close()
