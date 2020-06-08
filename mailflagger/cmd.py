#!/usr/bin/env python
# -*- mode: python -*-

import argparse
import logging
import sys

try:
    import gooey
except ImportError:
    gooey = None

import mailflagger.plugins.registry
from . import config


def flex_add_argument(f):
    '''Make the add_argument accept (and ignore) the widget option.'''

    def f_decorated(*args, **kwargs):
        kwargs.pop('widget', None)
        return f(*args, **kwargs)

    return f_decorated


# Monkey-patching a private class…
argparse._ActionsContainer.add_argument = flex_add_argument(argparse.ArgumentParser.add_argument)

# Do not run GUI if it is not available or if command-line arguments are given.
if gooey is None or len(sys.argv) > 1:
    ArgumentParser = argparse.ArgumentParser

    def gui_decorator(f):
        return f

    gui = False
else:
    ArgumentParser = gooey.GooeyParser
    gui_decorator = gooey.Gooey(
        program_name='Mail flagger',
        navigation='TABBED',
        suppress_gooey_flag=True,
    )
    gui = True


@gui_decorator
def main():
    parser = ArgumentParser(description='Handle flagging of requested emails.')
    subparsers = parser.add_subparsers(
        # Commented out until https://github.com/chriskiehl/Gooey/pull/545/files is merged.
        # title='commands',
    )

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        '--server-address',
        help='ZeroMQ address of server.',
        default='tcp://127.0.0.1:33985',
    )
    parent_parser.add_argument(
        '--log-level',
        default='info',
    )
    parent_parser.add_argument(
        '--save-config',
        action='store_true',
        default=gui,
    )
    parent_parser.add_argument(
        '--command-ordering',
        help='A comma-separated list of commands that should be displayed first (requires config save).',
        default='',
    )

    # # A hack which sets “daemon” as the default command when no arguments are given.
    raw_args = sys.argv[1:] or ['daemon']
    command_to_execute_name = raw_args[0]

    defaults = config.get_saved_defaults()
    parser.set_defaults(**defaults)
    for command_name, command in mailflagger.plugins.registry.iter_command_plugins(defaults):
        if command_name == command_to_execute_name:
            command_to_execute = command
        command_parser = subparsers.add_parser(
            command_name,
            parents=[parent_parser],
            help=getattr(command, 'command_help', lambda x: None)(defaults),
        )
        getattr(command, 'modify_subparser', lambda x: None)(command_parser)
        command_parser.set_defaults(**defaults)

    args = parser.parse_args(raw_args)

    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(level=log_level)

    if not gui and args.save_config:
        config.save_new_defaults(args, defaults)

    command_to_execute.run(args)
