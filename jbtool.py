#!/usr/local/bin/python3

import argparse
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
import psutil


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


def check_process_exist(p):
    for proc in psutil.process_iter(['name']):
        if proc.info.get('name') == p:
            print(f'Process "{p}" is running. Exiting...')
            exit(0)


def switch_config(confdir: Path):
    path = confdir.__str__()
    if 'pycharm' in path.lower():
        check_process_exist('pycharm')
    elif 'idea' in path.lower():
        check_process_exist('idea')
    else:
        print('No known IDE process found...')
        exit(1)

    confname = confdir.name
    parent = confdir.parent
    conf_test = parent / (confname + '.test')
    conf_prod = parent / (confname + '.prod')

    if not Path.exists(conf_test) and not Path.exists(conf_prod):
        print('Making a copy of config...')
        shutil.copytree(confdir, conf_prod)
    elif Path.exists(conf_test):
        print('Switching to test...')
        Path.rename(confdir, conf_prod)
        Path.rename(conf_test, confdir)
    elif Path.exists(conf_prod):
        print('Switching to prod...')
        Path.rename(confdir, conf_test)
        Path.rename(conf_prod, confdir)


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

    sub3 = sub.add_parser('switch-config', help='Switch between test and prod configs')
    sub3.add_argument('-c', '--config-dir', type=str, required=True, help='Configuration directory')
    sub3.set_defaults(func=switch_config)

    args = parser.parse_args()
    args.func(Path(args.config_dir))


if __name__ == '__main__':
    main()
