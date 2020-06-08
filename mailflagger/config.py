import json
import logging
import os
import os.path
import platform


logger = logging.getLogger(__name__)


def config_file_locations():
    env_filepath = os.getenv('MAIL_FLAGGER_CONFIG')
    if env_filepath:
        yield env_filepath
        return

    if (system := platform.system()) == 'Windows':
        system_dir = os.environ['LocalAppData']
    elif system == 'Darwin':
        system_dir = os.path.join(
            os.environ['HOME'],
            'Library',
            'Preferences',
        )
    else:
        system_dir = os.getenv(
            'XDG_CONFIG_HOME',
            os.path.join(
                os.environ['HOME'],
                '.config',
            ))

    filename = 'mailflagger.json'

    yield os.path.join(
        system_dir,
        'mailflagger',
        filename,
    )


def get_saved_defaults():
    d = {}
    for path in config_file_locations():
        if os.path.isfile(path):
            with open(path) as f:
                logger.debug(f'Loading configuration from {path}…')
                d = json.load(f)
                break
    return d


def save_new_defaults(args, old_defaults, /):
    logger.debug('Saving configuration…')

    config = {**old_defaults, **vars(args)}
    del config['save_config']
    if not config['imap_store_password']:
        config['imap_password'] = None

    filepath = next(config_file_locations())
    if not os.path.isdir(dirname := os.path.dirname(filepath)):
        os.mkdir(dirname)
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=4)
