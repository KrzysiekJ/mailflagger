from typing import Any, Iterable, Tuple

import pkg_resources


def iter_command_plugins(default_args, /) -> Iterable[Tuple[str, Any]]:
    ordering = default_args.get('command_ordering', '').split(',')
    ordering.append('daemon')

    unordered_commands = {
        entry_point.name: entry_point.load()
        for entry_point in pkg_resources.iter_entry_points('mailflagger.plugins.commands')}
    for prioritized_name in ordering:
        if command := unordered_commands.pop(prioritized_name, None):
            yield prioritized_name, command
    for name, command in unordered_commands.items():
        yield name, command


def iter_daemon_plugins():
    for entry_point in pkg_resources.iter_entry_points('mailflagger.plugins.daemon'):
        yield entry_point.load()
