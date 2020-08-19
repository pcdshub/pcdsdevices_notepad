"""
Notepad PV configuration to epicsArch.txt settings file.

See:
https://confluence.slac.stanford.edu/display/PCDS/EPICS+PV+recording+configurations
"""

import argparse
import json
import typing
from typing import Dict, List

# Stash the description for later usage by the CLI interface.
DESCRIPTION = __doc__.strip()


def load_config(config_file: str) -> List[Dict[str, dict]]:
    with open(config_file) as f:
        return json.load(f)


def create_archive(config: List[Dict[str, dict]]):
    pvs = {}
    for item in config:
        for key in ('read_pv', 'write_pv'):
            pvname = item.get(key, None)
            if pvname is not None:
                pvs[pvname] = item

    for pv, info in sorted(pvs.items()):
        yield f'* {info["dotted_name"]}'
        yield pv


def _get_argparser(parser: typing.Optional[argparse.ArgumentParser] = None):
    if parser is None:
        parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        'config_file',
        help='Notepad IOC configuration file'
    )

    parser.add_argument(
        '--output', default='-', type=str,
        help='File to write to (- for standard output)'
    )

    return parser


if __name__ == '__main__':
    parser = _get_argparser()
    args = parser.parse_args()

    config = load_config(args.config_file)

    lines = '\n'.join(create_archive(config))
    if args.output == '-':
        print(lines)
    else:
        with open(args.output, 'wt') as f:
            print(lines, file=f)
