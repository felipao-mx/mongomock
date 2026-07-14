"""Smoke test using Beanie, an ODM built on pymongo's async API.

Beanie is not a dependency of mongomock: this test only runs when beanie is installed
(`hatch run beanie:test`). It ensures mongomock.AsyncMongoClient is a good enough stand-in
for pymongo.AsyncMongoClient to back an ODM end to end.
"""

import importlib.util
import unittest
from unittest import IsolatedAsyncioTestCase

import mongomock


_HAVE_BEANIE = importlib.util.find_spec('beanie') is not None


@unittest.skipIf(not _HAVE_BEANIE, 'beanie not installed')
class BeanieIntegrationTest(IsolatedAsyncioTestCase):
    async def test__init_and_crud(self):
        import beanie

        class Product(beanie.Document):
            name: str
            price: float

        client = mongomock.AsyncMongoClient()
        await beanie.init_beanie(database=client.products_db, document_models=[Product])

        await Product(name='Tony', price=5.95).insert()

        product = await Product.find_one(Product.name == 'Tony')
        self.assertEqual(5.95, product.price)

        products = await Product.find_all().to_list()
        self.assertEqual(1, len(products))

        self.assertEqual(1, await Product.count())

        await product.set({Product.price: 6.95})
        product = await Product.find_one(Product.name == 'Tony')
        self.assertEqual(6.95, product.price)

        await product.delete()
        self.assertEqual(0, await Product.count())
