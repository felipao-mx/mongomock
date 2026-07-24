from unittest import IsolatedAsyncioTestCase

import mongomock
from mongomock.asynchronous import AsyncCursor


class AsyncCursorTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.collection = mongomock.AsyncMongoClient().somedb.collec

    async def test__async_iteration(self):
        await self.collection.insert_many([{'_id': i} for i in range(3)])
        docs = [doc async for doc in self.collection.find()]
        self.assertEqual([{'_id': 0}, {'_id': 1}, {'_id': 2}], docs)

    async def test__stop_async_iteration(self):
        cursor = self.collection.find()
        with self.assertRaises(StopAsyncIteration):
            await cursor.next()

    async def test__chaining(self):
        await self.collection.insert_many([{'_id': i} for i in range(5)])
        cursor = self.collection.find()
        self.assertIs(cursor, cursor.sort('_id', -1).skip(1).limit(2).batch_size(10))
        self.assertIs(cursor, cursor.hint(None).max_time_ms(1000).allow_disk_use(True))
        self.assertIs(cursor, cursor.comment('a comment').collation(None))
        self.assertEqual([{'_id': 3}, {'_id': 2}], await cursor.to_list())

    async def test__to_list_is_incremental(self):
        await self.collection.insert_many([{'_id': i} for i in range(5)])
        cursor = self.collection.find()
        self.assertEqual([{'_id': 0}, {'_id': 1}], await cursor.to_list(2))
        self.assertEqual([{'_id': 2}, {'_id': 3}, {'_id': 4}], await cursor.to_list())
        self.assertEqual([], await cursor.to_list())

    async def test__to_list_after_anext(self):
        await self.collection.insert_many([{'_id': i} for i in range(3)])
        cursor = self.collection.find()
        self.assertEqual({'_id': 0}, await cursor.next())
        self.assertEqual([{'_id': 1}, {'_id': 2}], await cursor.to_list())

    async def test__to_list_invalid_length(self):
        with self.assertRaises(ValueError):
            await self.collection.find().to_list(0)

    async def test__rewind(self):
        await self.collection.insert_many([{'_id': i} for i in range(3)])
        cursor = self.collection.find()
        first_pass = await cursor.to_list()
        self.assertIs(cursor, await cursor.rewind())
        self.assertEqual(first_pass, await cursor.to_list())

    async def test__clone(self):
        await self.collection.insert_many([{'_id': i} for i in range(3)])
        cursor = self.collection.find()
        await cursor.next()

        clone = cursor.clone()
        self.assertIsInstance(clone, AsyncCursor)
        self.assertEqual(3, len(await clone.to_list()))

    async def test__alive(self):
        await self.collection.insert_one({'x': 1})
        cursor = self.collection.find()
        self.assertTrue(cursor.alive)
        await cursor.next()
        self.assertFalse(cursor.alive)

    async def test__context_manager(self):
        await self.collection.insert_one({'x': 1})
        async with self.collection.find() as cursor:
            self.assertEqual(1, len(await cursor.to_list()))

    async def test__distinct(self):
        await self.collection.insert_many([{'x': 1}, {'x': 1}, {'x': 2}])
        self.assertEqual({1, 2}, set(await self.collection.find().distinct('x')))

    async def test__indexing_not_supported(self):
        with self.assertRaises(IndexError):
            self.collection.find()[0]

    async def test__not_implemented(self):
        cursor = self.collection.find()
        with self.assertRaises(NotImplementedError):
            cursor.where('this.x == 1')
        with self.assertRaises(NotImplementedError):
            await cursor.explain()


class AsyncCommandCursorTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.collection = mongomock.AsyncMongoClient().somedb.collec

    async def test__async_iteration(self):
        await self.collection.insert_many([{'_id': i} for i in range(3)])
        cursor = await self.collection.aggregate([{'$sort': {'_id': 1}}])
        self.assertEqual([{'_id': 0}, {'_id': 1}, {'_id': 2}], [doc async for doc in cursor])
        with self.assertRaises(StopAsyncIteration):
            await cursor.next()

    async def test__to_list_is_incremental(self):
        await self.collection.insert_many([{'_id': i} for i in range(5)])
        cursor = await self.collection.aggregate([{'$sort': {'_id': 1}}])
        self.assertEqual([{'_id': 0}, {'_id': 1}], await cursor.to_list(2))
        self.assertEqual([{'_id': 2}, {'_id': 3}, {'_id': 4}], await cursor.to_list())
        self.assertEqual([], await cursor.to_list())

    async def test__try_next(self):
        await self.collection.insert_one({'_id': 1})
        cursor = await self.collection.aggregate([])
        self.assertEqual({'_id': 1}, await cursor.try_next())
        self.assertIsNone(await cursor.try_next())

    async def test__batch_size_chaining(self):
        cursor = await self.collection.aggregate([])
        self.assertIs(cursor, cursor.batch_size(10))

    async def test__context_manager(self):
        await self.collection.insert_one({'x': 1})
        async with await self.collection.aggregate([]) as cursor:
            self.assertEqual(1, len(await cursor.to_list()))
