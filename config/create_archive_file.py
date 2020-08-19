"""
Notepad PV configuration to archive appliance settings file.
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


def create_archive(
        config: List[Dict[str, dict]],
        *,
        period: int = 1,
        method: str = 'scan'
        ):
    pvs = set()
    for item in config:
        for key in ('read_pv', 'write_pv'):
            pvname = item.get(key, None)
            if pvname is not None:
                pvs.add(pvname)

    for pv in sorted(pvs):
        yield f'{pv}\t{period}\t{method}'


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

    parser.add_argument(
        '--period', type=int, default=1,
        help='Archiver appliance update period'
    )

    parser.add_argument(
        '--method', choices=['scan', 'monitor'], default='scan',
        help='Archiver appliance update method'
    )
    return parser


if __name__ == '__main__':
    parser = _get_argparser()
    args = parser.parse_args()

    config = load_config(args.config_file)

    lines = '\n'.join(create_archive(config, period=args.period,
                                     method=args.method))
    if args.output == '-':
        print(lines)
    else:
        with open(args.output, 'wt') as f:
            print(lines, file=f)
