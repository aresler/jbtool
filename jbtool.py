#!/usr/local/bin/python3

import argparse
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


def remove_file(f: Path):
    if Path.exists(f):
        Path.unlink(f)
        print(f'\'{f}\' removed')
    else:
        print(f'The file \'{f}\' doesn\'t exist')


def validate_file(f: Path):
    if not Path.exists(f):
        print(f'The file \'{f}\' does not exist. Exiting...')
        exit(1)


def clear_remotes(confdir: Path):
    jdk_table = confdir / 'options/jdk.table.xml'
    web_servers = confdir / 'options/webServers.xml'
    validate_file(jdk_table)

    print('Removing deployments...')
    remove_file(web_servers)

    tree = ET.parse(jdk_table)
    root = tree.getroot()
    jdks = root[0]

    to_remove = []

    for jdk in jdks:
        if jdk.find('additional').find('PathMappingSettings'):
            to_remove.append(jdk)

    if to_remove:
        print('\nRemoving the following interpreters:')
        for jdk in to_remove:
            name = jdk.find('name').get('value')
            print(f'- {name}')
            jdks.remove(jdk)
    else:
        print('\nNo remote interpreters found\n')

    tree.write(jdk_table)


def free_venv(confdir: Path):
    jdk_table = confdir / 'options/jdk.table.xml'
    validate_file(jdk_table)

    tree = ET.parse(jdk_table)
    root = tree.getroot()
    jdks = root[0]

    to_free = []
    attr = 'ASSOCIATED_PROJECT_PATH'

    for jdk in jdks:
        if jdk.find('additional').get(attr):
            to_free.append(jdk)

    if to_free:
        print('\nFreeing the following interpreters:')
        for jdk in to_free:
            name = jdk.find('name').get('value')
            print(f'- {name}')
            jdk.find('additional').attrib.pop(attr)
    else:
        print('\nNoting to free...\n')

    tree.write(jdk_table)


def main():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(
        title='Possible actions',
    )

    sub1 = sub.add_parser('free-venv', help='Un-associate virtualenv interpreters')
    sub1.add_argument('-c', '--config-dir', type=str, required=True, help='Configuration directory')
    sub1.set_defaults(func=free_venv)

    sub2 = sub.add_parser('clear-remotes', help='Remove remote interpreters and all deployments')
    sub2.add_argument('-c', '--config-dir', type=str, required=True, help='Configuration directory')
    sub2.set_defaults(func=clear_remotes)

    args = parser.parse_args()
    args.func(Path(args.config_dir))


if __name__ == '__main__':
    main()
