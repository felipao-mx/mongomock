class CommandCursor:
    def __init__(self, collection, curser_info=None, address=None, retrieved=0):
        self._collection = iter(collection)
        self._id = None
        self._address = address
        self._data = {}
        self._retrieved = retrieved
        self._batch_size = 0
        self._killed = self._id == 0

    @property
    def address(self):
        return self._address

    def close(self):
        pass

    def batch_size(self, batch_size):
        return self

    @property
    def alive(self):
        return True

    def __iter__(self):
        return self

    def next(self):
        return next(self._collection)

    __next__ = next

    def try_next(self):
        try:
            return next(self._collection)
        except StopIteration:
            return None

    def to_list(self, length=None):
        if isinstance(length, int) and length < 1:
            raise ValueError('to_list() length must be greater than 0')
        docs = []
        for doc in self:
            docs.append(doc)
            if length is not None and len(docs) == length:
                break
        return docs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return
