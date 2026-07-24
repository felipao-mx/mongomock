"""Checks that the mongomock async facades match pymongo's asynchronous API.

For every public member of pymongo's async classes, the mongomock facade must expose the
same attribute with the same nature: coroutine methods stay coroutines and synchronous
methods (e.g. cursor chaining methods) stay synchronous. The installed pymongo is the
ground truth.
"""

import inspect
import unittest
from unittest import TestCase

from packaging import version

from mongomock import helpers
from mongomock.asynchronous import AsyncCollection
from mongomock.asynchronous import AsyncCommandCursor
from mongomock.asynchronous import AsyncCursor
from mongomock.asynchronous import AsyncDatabase
from mongomock.asynchronous import AsyncMongoClient


try:
    from pymongo.asynchronous.collection import AsyncCollection as PymongoAsyncCollection
    from pymongo.asynchronous.command_cursor import AsyncCommandCursor as PymongoAsyncCommandCursor
    from pymongo.asynchronous.cursor import AsyncCursor as PymongoAsyncCursor
    from pymongo.asynchronous.database import AsyncDatabase as PymongoAsyncDatabase
    from pymongo.asynchronous.mongo_client import AsyncMongoClient as PymongoAsyncMongoClient

    _HAVE_PYMONGO_ASYNC = True
except ImportError:
    _HAVE_PYMONGO_ASYNC = False


# Public pymongo members that mongomock does not expose yet. On the client, the database and
# collection, missing names still resolve through __getattr__ as database/collection access,
# the same way sync mongomock behaves.
_KNOWN_MISSING = {
    ('AsyncMongoClient', 'append_metadata'),
    ('AsyncMongoClient', 'arbiters'),
    ('AsyncMongoClient', 'eq_props'),
    ('AsyncMongoClient', 'next'),
    ('AsyncMongoClient', 'nodes'),
    ('AsyncMongoClient', 'options'),
    ('AsyncMongoClient', 'primary'),
    ('AsyncMongoClient', 'read_concern'),
    ('AsyncMongoClient', 'secondaries'),
    ('AsyncMongoClient', 'topology_description'),
    ('AsyncMongoClient', 'write_concern'),
    ('AsyncDatabase', 'next'),
    ('AsyncCollection', 'create_search_index'),
    ('AsyncCollection', 'create_search_indexes'),
    ('AsyncCollection', 'drop_search_index'),
    ('AsyncCollection', 'list_search_indexes'),
    ('AsyncCollection', 'next'),
    ('AsyncCollection', 'update_search_index'),
    ('AsyncCursor', 'add_option'),
    ('AsyncCursor', 'address'),
    ('AsyncCursor', 'cursor_id'),
    ('AsyncCursor', 'max'),
    ('AsyncCursor', 'max_await_time_ms'),
    ('AsyncCursor', 'max_scan'),
    ('AsyncCursor', 'min'),
    ('AsyncCursor', 'remove_option'),
    ('AsyncCursor', 'retrieved'),
    ('AsyncCommandCursor', 'cursor_id'),
    ('AsyncCommandCursor', 'session'),
}


@unittest.skipIf(not helpers.HAVE_PYMONGO, 'pymongo not installed')
@unittest.skipIf(not _HAVE_PYMONGO_ASYNC, 'pymongo has no asynchronous API')
@unittest.skipIf(
    version.parse('4.9') > helpers.PYMONGO_VERSION, 'pymongo async API requires pymongo>=4.9'
)
class AsyncApiParityTest(TestCase):
    def _assert_parity(self, pymongo_class, mongomock_class):
        for name in dir(pymongo_class):
            if name.startswith('_'):
                continue
            if (pymongo_class.__name__, name) in _KNOWN_MISSING:
                continue
            pymongo_attr = inspect.getattr_static(pymongo_class, name)
            self.assertTrue(
                hasattr(mongomock_class, name),
                f'{mongomock_class.__name__} is missing {name!r}',
            )
            if isinstance(pymongo_attr, property) or not callable(pymongo_attr):
                continue
            pymongo_is_coroutine = inspect.iscoroutinefunction(inspect.unwrap(pymongo_attr))
            mongomock_attr = inspect.getattr_static(mongomock_class, name)
            mongomock_is_coroutine = inspect.iscoroutinefunction(inspect.unwrap(mongomock_attr))
            self.assertEqual(
                pymongo_is_coroutine,
                mongomock_is_coroutine,
                f'{mongomock_class.__name__}.{name} should be '
                f'{"a coroutine" if pymongo_is_coroutine else "synchronous"} to match pymongo',
            )

    def test__mongo_client(self):
        self._assert_parity(PymongoAsyncMongoClient, AsyncMongoClient)

    def test__database(self):
        self._assert_parity(PymongoAsyncDatabase, AsyncDatabase)

    def test__collection(self):
        self._assert_parity(PymongoAsyncCollection, AsyncCollection)

    def test__cursor(self):
        self._assert_parity(PymongoAsyncCursor, AsyncCursor)

    def test__command_cursor(self):
        self._assert_parity(PymongoAsyncCommandCursor, AsyncCommandCursor)
