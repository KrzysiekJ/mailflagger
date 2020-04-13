from mailflagger.client import Client


def modify_subparser(subparser):
    subparser.add_argument(
        'query',
        help='IMAP query to obtain message to be flagged.',
    )


def run(args):
    with Client(args) as c:
        c.send({'query': args.query})
        reply = c.recv()
        assert reply.get('processed')


def command_help(default_args):
    return 'Flag a message.'
