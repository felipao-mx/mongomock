from unittest import IsolatedAsyncioTestCase
from unittest import skipIf

import mongomock
from mongomock import helpers
from mongomock.asynchronous import AsyncCollection
from mongomock.asynchronous import AsyncDatabase


try:
    from bson import DBRef as _DBRef
except ImportError:
    from tests.utils import DBRef as _DBRef


class AsyncDatabaseApiTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = mongomock.AsyncMongoClient()
        self.database = self.client.somedb

    def test__get_collection(self):
        collection = self.database.get_collection('collec')
        self.assertIsInstance(collection, AsyncCollection)
        self.assertEqual('collec', collection.name)
        self.assertEqual(collection, self.database['collec'])
        self.assertEqual(collection, self.database.collec)

    def test__getattr_underscore(self):
        with self.assertRaises(AttributeError) as err_context:
            self.database._users  # noqa: B018

        self.assertIn("AsyncDatabase has no attribute '_users'", str(err_context.exception))

    def test__client(self):
        self.assertIs(self.client, self.database.client)

    def test__properties(self):
        self.assertEqual('somedb', self.database.name)
        self.assertEqual({}, self.database.write_concern.document)
        self.assertIsNotNone(self.database.codec_options)
        self.assertIsNotNone(self.database.read_preference)
        self.assertIsNotNone(self.database.read_concern)

    def test__equality(self):
        self.assertEqual(self.database, self.client.get_database('somedb'))
        self.assertNotEqual(self.database, self.client.get_database('otherdb'))
        self.assertEqual(hash(self.database), hash(self.client.get_database('somedb')))

    def test__repr(self):
        self.assertEqual(
            "AsyncDatabase(mongomock.AsyncMongoClient('localhost', 27017), 'somedb')",
            repr(self.database),
        )

    def test__with_options(self):
        database = self.database.with_options(read_preference=self.database.read_preference)
        self.assertIsInstance(database, AsyncDatabase)
        self.assertEqual(self.database, database)

    async def test__command_ping(self):
        self.assertEqual({'ok': 1.0}, await self.database.command('ping'))

    async def test__command_build_info(self):
        result = await self.database.command('buildInfo')
        self.assertEqual(mongomock.SERVER_VERSION, result['version'])

    async def test__command_hello(self):
        result = await self.database.command('hello')
        self.assertTrue(result['isWritablePrimary'])

    async def test__command_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            await self.database.command({'count': 'user'})

    async def test__create_collection(self):
        collection = await self.database.create_collection('collec')
        self.assertIsInstance(collection, AsyncCollection)
        self.assertEqual(['collec'], await self.database.list_collection_names())

        with self.assertRaises(mongomock.CollectionInvalid):
            await self.database.create_collection('collec')

    async def test__drop_collection_by_name(self):
        await self.database.create_collection('a')
        await self.database.drop_collection('a')
        self.assertEqual([], await self.database.list_collection_names())

    async def test__drop_collection_by_object(self):
        await self.database.create_collection('a')
        await self.database.drop_collection(self.database.a)
        self.assertEqual([], await self.database.list_collection_names())

    async def test__session(self):
        with self.assertRaises(NotImplementedError):
            await self.database.list_collection_names(session=1)
        with self.assertRaises(NotImplementedError):
            await self.database.drop_collection('a', session=1)
        with self.assertRaises(NotImplementedError):
            await self.database.create_collection('a', session=1)

    @skipIf(not helpers.HAVE_PYMONGO, 'pymongo not installed')
    async def test__dereference(self):
        await self.database.collec.insert_one({'_id': 'some_id', 'answer': 42})
        doc = await self.database.dereference(_DBRef('collec', 'some_id'))
        self.assertEqual({'_id': 'some_id', 'answer': 42}, doc)

    async def test__not_implemented(self):
        with self.assertRaises(NotImplementedError):
            await self.database.aggregate([])
        with self.assertRaises(NotImplementedError):
            await self.database.watch()
        with self.assertRaises(NotImplementedError):
            await self.database.validate_collection('collec')
        with self.assertRaises(NotImplementedError):
            await self.database.cursor_command('count')
