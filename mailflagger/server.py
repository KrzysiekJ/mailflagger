import asyncio
import logging
import platform

import msgpack
import zmq.asyncio

import mailflagger.plugins.registry
from . import imap

logger = logging.getLogger(__name__)


async def daemon_coroutine(args):
    imap_config = imap.get_config(args)

    ctx = zmq.asyncio.Context.instance()
    socket = ctx.socket(zmq.REP)
    socket.bind(args.server_address)
    logger.debug('Initialized socket.')

    try:
        while True:
            msg = msgpack.unpackb(await socket.recv())
            logger.debug(f'Received message: {msg}.')
            reply = imap.process_message(msg['query'], imap_config, args)
            logger.debug(f'Sending reply: {reply}…')
            await socket.send(msgpack.packb(reply))
    finally:
        socket.close()
        ctx.term()


async def gather_coro(*args, **kwargs):
    '''asyncio.gather as a coroutine.'''
    return await asyncio.gather(*args, **kwargs)


def run(args):
    aws = [daemon_coroutine(args)]
    for plugin in mailflagger.plugins.registry.iter_daemon_plugins():
        for coro in plugin.daemon_coroutines(args):
            aws.append(coro)

    # https://bugs.python.org/issue37373
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(gather_coro(*aws))


def modify_subparser(subparser):
    imap_group = subparser.add_argument_group('IMAP configuration')
    imap.add_arguments(imap_group)
    for plugin in mailflagger.plugins.registry.iter_daemon_plugins():
        getattr(plugin, 'modify_subparser', lambda x: None)(subparser)


def command_help(default_args):
    return 'Wait for flagging requests. This is the default when no arguments are given.'
