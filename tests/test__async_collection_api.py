from unittest import IsolatedAsyncioTestCase
from unittest import skipIf

import mongomock
from mongomock import helpers
from mongomock.asynchronous import AsyncCollection
from mongomock.asynchronous import AsyncCommandCursor
from mongomock.asynchronous import AsyncCursor


class AsyncCollectionApiTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = mongomock.AsyncMongoClient()
        self.db = self.client.somedb
        self.collection = self.db.collec

    def test__properties(self):
        self.assertEqual('collec', self.collection.name)
        self.assertEqual('somedb.collec', self.collection.full_name)
        self.assertIs(self.db, self.collection.database)
        self.assertIsNotNone(self.collection.codec_options)
        self.assertIsNotNone(self.collection.read_preference)
        self.assertIsNotNone(self.collection.read_concern)
        self.assertEqual({}, self.collection.write_concern.document)

    def test__sub_collection(self):
        self.assertEqual('collec.sub', self.collection.sub.name)
        self.assertEqual('collec.sub', self.collection['sub'].name)
        self.assertIsInstance(self.collection.sub, AsyncCollection)

    def test__getattr_underscore(self):
        with self.assertRaises(AttributeError) as err_context:
            self.collection._users  # noqa: B018

        self.assertIn("AsyncCollection has no attribute '_users'", str(err_context.exception))

    def test__equality(self):
        self.assertEqual(self.collection, self.db.get_collection('collec'))
        self.assertNotEqual(self.collection, self.db.get_collection('other'))
        self.assertEqual(hash(self.collection), hash(self.db.get_collection('collec')))

    def test__repr(self):
        self.assertEqual(
            "AsyncCollection(AsyncDatabase(mongomock.AsyncMongoClient('localhost', 27017), "
            "'somedb'), 'collec')",
            repr(self.collection),
        )

    def test__with_options(self):
        collection = self.collection.with_options(read_preference=self.collection.read_preference)
        self.assertIsInstance(collection, AsyncCollection)
        self.assertEqual(self.collection, collection)

    async def test__insert_and_find_one(self):
        result = await self.collection.insert_one({'x': 1})
        self.assertTrue(result.inserted_id)
        self.assertEqual({'x': 1}, await self.collection.find_one({}, {'_id': 0}))

    async def test__insert_many(self):
        result = await self.collection.insert_many([{'x': 1}, {'x': 2}])
        self.assertEqual(2, len(result.inserted_ids))

    async def test__update(self):
        await self.collection.insert_one({'_id': 1, 'x': 1})

        result = await self.collection.update_one({'_id': 1}, {'$set': {'x': 2}})
        self.assertEqual(1, result.modified_count)

        result = await self.collection.update_many({}, {'$inc': {'x': 1}})
        self.assertEqual(1, result.modified_count)

        result = await self.collection.replace_one({'_id': 1}, {'x': 0})
        self.assertEqual(1, result.modified_count)
        self.assertEqual({'_id': 1, 'x': 0}, await self.collection.find_one())

    async def test__delete(self):
        await self.collection.insert_many([{'x': 1}, {'x': 2}, {'x': 3}])

        result = await self.collection.delete_one({'x': 1})
        self.assertEqual(1, result.deleted_count)

        result = await self.collection.delete_many({})
        self.assertEqual(2, result.deleted_count)

    async def test__find_returns_async_cursor(self):
        cursor = self.collection.find({})
        self.assertIsInstance(cursor, AsyncCursor)
        self.assertIs(self.collection, cursor.collection)

    async def test__find_one_and_update(self):
        await self.collection.insert_one({'_id': 1, 'x': 1})
        doc = await self.collection.find_one_and_update({'_id': 1}, {'$set': {'x': 2}})
        self.assertEqual({'_id': 1, 'x': 1}, doc)

    async def test__find_one_and_replace(self):
        await self.collection.insert_one({'_id': 1, 'x': 1})
        doc = await self.collection.find_one_and_replace({'_id': 1}, {'x': 2})
        self.assertEqual({'_id': 1, 'x': 1}, doc)

    async def test__find_one_and_delete(self):
        await self.collection.insert_one({'_id': 1, 'x': 1})
        doc = await self.collection.find_one_and_delete({'_id': 1})
        self.assertEqual({'_id': 1, 'x': 1}, doc)
        self.assertEqual(0, await self.collection.count_documents({}))

    async def test__counts(self):
        await self.collection.insert_many([{'x': 1}, {'x': 2}])
        self.assertEqual(2, await self.collection.count_documents({}))
        self.assertEqual(1, await self.collection.count_documents({'x': 1}))
        self.assertEqual(2, await self.collection.estimated_document_count())

    async def test__distinct(self):
        await self.collection.insert_many([{'x': 1}, {'x': 1}, {'x': 2}])
        self.assertEqual({1, 2}, set(await self.collection.distinct('x')))

    async def test__aggregate(self):
        await self.collection.insert_many([{'x': 1}, {'x': 2}, {'x': 3}])
        cursor = await self.collection.aggregate([{'$match': {'x': {'$gte': 2}}}])
        self.assertIsInstance(cursor, AsyncCommandCursor)
        self.assertEqual(2, len([doc async for doc in cursor]))

    async def test__indexes(self):
        name = await self.collection.create_index([('x', 1)])
        self.assertEqual('x_1', name)

        cursor = await self.collection.list_indexes()
        self.assertIsInstance(cursor, AsyncCommandCursor)
        self.assertIn('x_1', [index['name'] async for index in cursor])

        index_information = await self.collection.index_information()
        self.assertIn('x_1', index_information)

        await self.collection.drop_index('x_1')
        self.assertNotIn('x_1', await self.collection.index_information())

        await self.collection.create_index([('y', 1)])
        await self.collection.drop_indexes()
        self.assertNotIn('y_1', await self.collection.index_information())

    @skipIf(not helpers.HAVE_PYMONGO, 'pymongo not installed')
    async def test__bulk_write(self):
        from pymongo import InsertOne

        result = await self.collection.bulk_write([InsertOne({'x': 1}), InsertOne({'x': 2})])
        self.assertEqual(2, result.inserted_count)

    async def test__rename(self):
        await self.collection.insert_one({'x': 1})
        await self.collection.rename('other_name')
        self.assertEqual(['other_name'], await self.db.list_collection_names())

    async def test__drop(self):
        await self.collection.insert_one({'x': 1})
        await self.collection.drop()
        self.assertEqual([], await self.db.list_collection_names())

    async def test__session(self):
        with self.assertRaises(NotImplementedError):
            await self.collection.insert_one({'x': 1}, session=1)

    async def test__not_implemented(self):
        with self.assertRaises(NotImplementedError):
            await self.collection.options()
        with self.assertRaises(NotImplementedError):
            await self.collection.watch()
