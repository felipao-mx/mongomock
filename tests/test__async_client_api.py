from unittest import IsolatedAsyncioTestCase

import mongomock
from mongomock.asynchronous import AsyncCommandCursor
from mongomock.asynchronous import AsyncDatabase
from mongomock.asynchronous import AsyncMongoClient


class AsyncMongoClientApiTest(IsolatedAsyncioTestCase):
    def test__top_level_export(self):
        self.assertIs(mongomock.AsyncMongoClient, AsyncMongoClient)

    def test__parse_url(self):
        client = mongomock.AsyncMongoClient('mongodb://localhost:27017/')
        self.assertEqual(('localhost', 27017), client.address)

        client = mongomock.AsyncMongoClient('mongodb://localhost:1234/')
        self.assertEqual(('localhost', 1234), client.address)

    def test__connection_kwargs(self):
        client = mongomock.AsyncMongoClient(maxPoolSize=10, serverSelectionTimeoutMS=100)
        self.assertEqual(('localhost', 27017), client.address)

    def test__get_database(self):
        client = mongomock.AsyncMongoClient()
        database = client.get_database('somedb')
        self.assertIsInstance(database, AsyncDatabase)
        self.assertEqual('somedb', database.name)
        self.assertEqual(database, client['somedb'])
        self.assertEqual(database, client.somedb)

    def test__get_default_database(self):
        client = mongomock.AsyncMongoClient('mongodb://localhost:27017/somedb')
        self.assertEqual('somedb', client.get_default_database().name)

        client = mongomock.AsyncMongoClient()
        self.assertEqual('otherdb', client.get_default_database('otherdb').name)

    def test__getattr_underscore(self):
        client = mongomock.AsyncMongoClient()
        with self.assertRaises(AttributeError) as err_context:
            client._some_db  # noqa: B018

        self.assertIn("AsyncMongoClient has no attribute '_some_db'", str(err_context.exception))

    async def test__aconnect_and_close(self):
        client = mongomock.AsyncMongoClient()
        await client.aconnect()
        await client.close()
        await client.aclose()

    async def test__context_manager(self):
        async with mongomock.AsyncMongoClient() as client:
            await client.somedb.collec.insert_one({'x': 1})
            self.assertTrue(await client.somedb.collec.find_one({'x': 1}))

    async def test__list_database_names(self):
        client = mongomock.AsyncMongoClient()
        self.assertEqual([], await client.list_database_names())

        await client.one_db.my_collec.insert_one({})
        self.assertEqual(['one_db'], await client.list_database_names())

    async def test__list_databases(self):
        client = mongomock.AsyncMongoClient()
        await client.one_db.my_collec.insert_one({})

        cursor = await client.list_databases()
        self.assertIsInstance(cursor, AsyncCommandCursor)
        self.assertEqual(
            [{'name': 'one_db', 'sizeOnDisk': 0, 'empty': False}],
            [database async for database in cursor],
        )

    async def test__drop_database_by_name(self):
        client = mongomock.AsyncMongoClient()
        await client.one_db.my_collec.insert_one({})
        await client.drop_database('one_db')
        self.assertEqual([], await client.list_database_names())

    async def test__drop_database_by_object(self):
        client = mongomock.AsyncMongoClient()
        await client.one_db.my_collec.insert_one({})
        await client.drop_database(client.one_db)
        self.assertEqual([], await client.list_database_names())

    async def test__server_info(self):
        client = mongomock.AsyncMongoClient()
        server_info = await client.server_info()
        self.assertEqual(mongomock.SERVER_VERSION, server_info['version'])

    def test__properties(self):
        client = mongomock.AsyncMongoClient()
        self.assertTrue(client.is_mongos)
        self.assertTrue(client.is_primary)

    def test__equality(self):
        self.assertEqual(mongomock.AsyncMongoClient(), mongomock.AsyncMongoClient())
        self.assertNotEqual(
            mongomock.AsyncMongoClient('mongodb://localhost:1234/'),
            mongomock.AsyncMongoClient(),
        )
        self.assertEqual(hash(mongomock.AsyncMongoClient()), hash(mongomock.AsyncMongoClient()))

    def test__repr(self):
        self.assertEqual(
            "mongomock.AsyncMongoClient('localhost', 27017)", repr(mongomock.AsyncMongoClient())
        )

    def test__start_session(self):
        client = mongomock.AsyncMongoClient()
        with self.assertRaises(NotImplementedError):
            client.start_session()

    async def test__not_implemented(self):
        client = mongomock.AsyncMongoClient()
        with self.assertRaises(NotImplementedError):
            await client.watch()
        with self.assertRaises(NotImplementedError):
            await client.bulk_write([])
