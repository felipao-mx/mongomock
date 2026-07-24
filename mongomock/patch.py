import time
from unittest import mock

from .asynchronous import AsyncMongoClient
from .mongo_client import MongoClient


try:
    import pymongo
    from pymongo.uri_parser import parse_uri
    from pymongo.uri_parser import split_hosts

    _IMPORT_PYMONGO_ERROR = None
except ImportError as error:
    from .helpers import parse_uri
    from .helpers import split_hosts

    _IMPORT_PYMONGO_ERROR = error


def _parse_any_host(host, default_port=27017):
    if isinstance(host, tuple):
        return _parse_any_host(host[0], host[1])
    if '://' in host:
        return parse_uri(host, warn=True)['nodelist']
    return split_hosts(host, default_port=default_port)


def patch(servers='localhost', on_new='error'):
    """Patch pymongo.MongoClient and, when available, pymongo.AsyncMongoClient.

    This will patch the class MongoClient and use mongomock to mock MongoDB
    servers. It keeps a consistant state of servers across multiple clients so
    you can do:

    ```
    client = pymongo.MongoClient(host='localhost', port=27017)
    client.db.coll.insert_one({'name': 'Pascal'})

    other_client = pymongo.MongoClient('mongodb://localhost:27017')
    client.db.coll.find_one()
    ```

    The data is persisted as long as the patch lives, and shared between sync and async
    clients connecting to the same server. Note that, like pymongo.mongo_client.MongoClient,
    code importing AsyncMongoClient from pymongo.asynchronous.mongo_client directly is not
    patched.

    Args:
        on_new: Behavior when accessing a new server (not in servers):
            'create': mock a new empty server, accept any client connection.
            'error': raise a ValueError immediately when trying to access.
            'timeout': behave as pymongo when a server does not exist, raise an
                error after a timeout.
            'pymongo': use an actual pymongo client.
        servers: a list of server that are avaiable.
    """

    PyMongoClient = None if _IMPORT_PYMONGO_ERROR else pymongo.MongoClient  # noqa: N806
    PyMongoAsyncClient = (  # noqa: N806
        None if _IMPORT_PYMONGO_ERROR else getattr(pymongo, 'AsyncMongoClient', None)
    )

    persisted_clients = {}
    parsed_servers = set()
    for server in servers if isinstance(servers, (list, tuple)) else [servers]:
        parsed_servers.update(_parse_any_host(server))

    def _attach_persistent_store(client):
        """Share the persisted store for the client's address, if the server is known."""
        try:
            persisted_client = persisted_clients[client.address]
            client._store = persisted_client._store
            return True
        except KeyError:
            pass

        if client.address in parsed_servers or on_new == 'create':
            persisted_clients[client.address] = client
            return True

        return False

    def _handle_unknown_server(address, pymongo_client_class, args, kwargs):
        if on_new == 'timeout':
            # TODO(pcorpet): Only wait when trying to access the server's data.
            time.sleep(kwargs.get('serverSelectionTimeoutMS', 30000))
            raise pymongo.errors.ServerSelectionTimeoutError(
                '%s:%d: [Errno 111] Connection refused' % address
            )

        if on_new == 'pymongo':
            return pymongo_client_class(*args, **kwargs)

        raise ValueError(f'MongoDB server {address}:{parsed_servers} does not exist.')

    def _create_persistent_client(*args, **kwargs):
        if _IMPORT_PYMONGO_ERROR:
            raise _IMPORT_PYMONGO_ERROR  # pylint: disable=raising-bad-type

        client = MongoClient(*args, **kwargs)
        if _attach_persistent_store(client):
            return client
        return _handle_unknown_server(client.address, PyMongoClient, args, kwargs)

    def _create_persistent_async_client(*args, **kwargs):
        if _IMPORT_PYMONGO_ERROR:
            raise _IMPORT_PYMONGO_ERROR  # pylint: disable=raising-bad-type

        client = AsyncMongoClient(*args, **kwargs)
        if _attach_persistent_store(client._delegate):
            return client
        return _handle_unknown_server(client.address, PyMongoAsyncClient, args, kwargs)

    class _PersistentClient:
        def __new__(cls, *args, **kwargs):
            return _create_persistent_client(*args, **kwargs)

    class _PersistentAsyncClient:
        def __new__(cls, *args, **kwargs):
            return _create_persistent_async_client(*args, **kwargs)

    if PyMongoAsyncClient is not None:
        return mock.patch.multiple(
            'pymongo',
            MongoClient=_PersistentClient,
            AsyncMongoClient=_PersistentAsyncClient,
        )
    return mock.patch('pymongo.MongoClient', _PersistentClient)
