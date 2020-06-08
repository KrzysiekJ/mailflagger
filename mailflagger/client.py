import logging
import msgpack
import zmq
import zmq.asyncio


logger = logging.getLogger(__name__)


class Client:
    def __init__(self, parsed_args, /, *, asynchronous=False):
        self._async = asynchronous
        self._server_address = parsed_args.server_address
        if self._async:
            self._ctx = zmq.asyncio.Context()
        else:
            self._ctx = zmq.Context.instance()
        self._socket = self._ctx.socket(zmq.REQ)
        self._socket.connect(self._server_address)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self._socket.close()
        self._ctx.term()

    def send(self, req):
        logger.debug(f'Sending message: {req}…')
        return self._socket.send(msgpack.packb(req))

    def recv(self):
        if self._async:
            return self._async_recv()
        else:
            return self._sync_recv()

    async def _async_recv(self):
        msg = msgpack.unpackb(await self._socket.recv())
        logger.debug(f'Received message: {msg}.')
        return msg

    def _sync_recv(self):
        msg = msgpack.unpackb(self._socket.recv())
        logger.debug(f'Received message: {msg}.')
        return msg
