#!/usr/local/bin/python3

import argparse
import os
import xml.etree.ElementTree as ET


def clear_remotes(confdir):
    jdk_table = f'{confdir}/options/jdk.table.xml'
    tree = ET.parse(jdk_table)
    root = tree.getroot()
    jdks = root[0]
    to_remove = []

    for jdk in jdks:
        if jdk.find('additional').find('PathMappingSettings'):
            to_remove.append(jdk)

    if to_remove:
        print('\nRemoving the following interpreters:\n')
        for jdk in to_remove:
            name = jdk.find('name').get('value')
            print(f'- {name}')
            jdks.remove(jdk)
    else:
        print('\nNo remote interpreters found\n')

    tree.write(jdk_table)


def drop_deployments(confdir):
    f = f'{confdir}/options/webServers.xml'
    if os.path.exists(f):
        os.remove(f)
    else:
        print(f'The file \'{f}\' doesn\'t exist')


def free_venv(confdir):
    jdk_table = f'{confdir}/options/jdk.table.xml'
    tree = ET.parse(jdk_table)
    root = tree.getroot()
    jdks = root[0]

    to_free = []
    attr = 'ASSOCIATED_PROJECT_PATH'

    for jdk in jdks:
        if jdk.find('additional').get(attr):
            to_free.append(jdk)

    if to_free:
        print('\nFreeing the following interpreters...\n')
        for jdk in to_free:
            name = jdk.find('name').get('value')
            print(f'- {name}')
            jdk.find('additional').attrib.pop(attr)
    else:
        print('\nNoting to free...\n')

    tree.write(jdk_table)


def main():
    help_msg = """Possible actions:
    free-venv -- Un-associate venv interpreters from their projects
    clear-remotes -- Remove remote interpreters and all deployments
    """

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('confdir', type=str, help='IDE configuration directory')
    parser.add_argument('action', type=str, help=help_msg)
    args = parser.parse_args()

    confdir = args.confdir
    action = args.action

    match action:
        case "free-venv":
            free_venv(confdir)
        case "clear-remotes":
            clear_remotes(confdir)
            drop_deployments(confdir)


if __name__ == '__main__':
    main()
