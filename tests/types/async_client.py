import mongomock


async def use_async_client() -> None:
    client = mongomock.AsyncMongoClient()
    collection = client['somedb']['collec']
    await collection.insert_one({'x': 1})
    await collection.find_one({'x': 1})
    async for _document in collection.find():
        pass
    await client.close()
