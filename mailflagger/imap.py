import collections
import logging
import imaplib
import time

logger = logging.getLogger(__name__)


IMAPConfig = collections.namedtuple(
    'IMAPConfig',
    [
        'server',
        'login',
        'password',
        'mailbox',
        'ssl',
        'port',
    ],
)


def add_arguments(group):
    group.add_argument(
        '--imap-server',
    )
    group.add_argument(
        '--imap-login',
    )
    group.add_argument(
        '--imap-password',
        widget='PasswordField',
    )
    store_password = group.add_mutually_exclusive_group()
    store_password.add_argument(
        '--imap-store-password',
        action='store_true',
        dest='imap_store_password',
        help='Store password (as plain text) in configuration file',
    )
    store_password.add_argument(
        '--imap-no-store-password',
        dest='imap_store_password',
        action='store_false',
        help='Do not store password in configuration file',
    )
    group.add_argument(
        '--imap-mailbox',
        default='INBOX',
        help='INBOX by default',
    )
    ssl = group.add_mutually_exclusive_group()
    ssl.add_argument(
        '--imap-ssl',
        help='Use SSL',
        dest='imap_ssl',
        action='store_true',
        default=True,
    )
    ssl.add_argument(
        '--imap-no-ssl',
        help='Do not use SSL',
        dest='imap_ssl',
        action='store_false',
    )
    group.add_argument(
        '--imap-port',
        type=int,
        help=f'By default {imaplib.IMAP4_SSL_PORT} if SSL is enabled, else {imaplib.IMAP4_PORT}',
    )

    action_flag = group.add_mutually_exclusive_group()
    action_flag.add_argument(
        '--action-flag',
        dest='action_flag',
        action='store_true',
        help='Flag message',
    )
    action_flag.add_argument(
        '--action-no-flag',
        dest='action_flag',
        action='store_false',
        help='Do not flag message',
    )

    group.add_argument(
        '--action-copy-to',
        help='Copy message to specified folder',
    )

    group.set_defaults(
        imap_ssl=True,
        imap_store_password=False,
        action_flag=True,
    )


def get_config(args):
    return IMAPConfig(
        args.imap_server,
        args.imap_login,
        args.imap_password,
        args.imap_mailbox,
        args.imap_ssl,
        args.imap_port or (imaplib.IMAP4_SSL_PORT if args.imap_ssl else imaplib.IMAP4_PORT),
    )


def imap_connection(config: IMAPConfig):
    class_ = imaplib.IMAP4_SSL if config.ssl else imaplib.IMAP4
    c = class_(config.server, config.port)
    logger.debug('Connected to IMAP server.')
    c.login(config.login, config.password)
    status, info = c.enable('UTF8=ACCEPT')
    assert status == 'OK'
    status, info = c.select(config.mailbox)
    assert status == 'OK'
    return c


def flag_message(imap, args, id_: bytes):
    status, result = imap.store(id_, '+FLAGS', '\\Flagged')
    assert status == 'OK'
    logger.info(f'Flagged message {int(id_)}.')


def copy_message(imap, args, id_: bytes):
    status, result = imap.copy(id_, args.action_copy_to)
    assert status == 'OK'
    logger.info(f'Copied message {int(id_)}.')


def actions(args):
    if args.action_flag:
        yield flag_message
    if args.action_copy_to:
        yield copy_message


def perform_actions(imap, args, msg_id: bytes):
    for action in actions(args):
        action(imap, args, msg_id)


def process_message(query, imap_config, args, retries=2):
    """Try to perform actions on message specified by IMAP query.

    For privacy reasons, this function does not inform whether message has been found.
    """
    full_query = ["UNFLAGGED", query]
    try:
        with imap_connection(imap_config) as imap:
            try:
                status, results = imap.search(None, *full_query)
            except imaplib.IMAP4.error as exc:
                if isinstance(exc, (imaplib.IMAP4.abort, imaplib.IMAP4.readonly)):
                    raise
                else:
                    logger.warning(f'IMAP error when doing search for query: “{full_query}”.')
                    # Query syntax error?
                    return {'processed': True}
            assert status == 'OK'
            found_msgs = results[0].split()
            if found_msgs:
                msg_id = found_msgs[0]
                logger.info(f'Performing actions on message {int(msg_id)}…')
                perform_actions(imap, args, msg_id)
            else:
                logger.warning(f'Have not found messages for query: {full_query}.')
            return {'processed': True}
    except (imaplib.IMAP4.abort, imaplib.IMAP4.readonly) as exc:
        if retries:
            logger.warning(f'Encountered error: “{exc}”. Retrying…')
            time.sleep(1)
            process_message(query, imap_config, args, retries - 1)
        else:
            raise
