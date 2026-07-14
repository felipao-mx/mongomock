class AsyncCommandCursor:
    """Mirrors pymongo's AsyncCommandCursor API on top of a mongomock CommandCursor."""

    def __init__(self, delegate):
        self._delegate = delegate

    @property
    def address(self):
        return self._delegate.address

    @property
    def alive(self):
        return self._delegate.alive

    def batch_size(self, batch_size):
        self._delegate.batch_size(batch_size)
        return self

    async def close(self):
        self._delegate.close()

    async def next(self):
        try:
            return next(self._delegate)
        except StopIteration:
            # PEP 479: a StopIteration escaping a coroutine would become a RuntimeError.
            raise StopAsyncIteration from None

    __anext__ = next

    async def try_next(self):
        return self._delegate.try_next()

    async def to_list(self, length=None):
        return self._delegate.to_list(length)

    def __aiter__(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._delegate.close()
