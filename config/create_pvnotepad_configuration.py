"""
Create a pvNotepad IOC configuration file.
"""

import argparse
import json
import pathlib
import typing
from typing import Dict, List

import jinja2

# Stash the description for later usage by the CLI interface.
DESCRIPTION = __doc__.strip()


SUPPORTED_RECORD_MAP = {
    # These are the only records currently available (R2.0.1):
    'ao': 'ao',
    'bo': 'bo',
    'longout': 'longout',
    'mbbo': 'mbbo',
    'stringin': 'stringin',
    'waveform': 'waveform',

    # Map any input records onto their output equivalent:
    'ai': 'ao',
    'bi': 'bo',
    'longin': 'longout',
    'mbbi': 'mbbo',
    'stringout': 'stringin',
}


def load_json(config_file: str) -> List[Dict[str, dict]]:
    with open(config_file) as f:
        return json.load(f)


def _truncate_middle(string, max_length):
    '''
    Truncate a string to a maximum length, replacing the skipped middle section
    with an ellipsis.

    Parameters
    ----------
    string : str
        The string to optionally truncate
    max_length : int
        The maximum length
    '''
    # Based on https://www.xormedia.com/string-truncate-middle-with-ellipsis/
    if len(string) <= max_length:
        return string

    # half of the size, minus the 3 dots
    n2 = max_length // 2 - 3
    n1 = max_length - n2 - 3
    return '...'.join((string[:n1], string[-n2:]))


def create_configuration(
        template_filename: str,
        config: List[Dict[str, dict]],
        *,
        macros: Dict[str, str],
        ):

    template_filename = pathlib.Path(template_filename)
    template_path = template_filename.parent
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    jinja_env.filters['truncate_middle'] = _truncate_middle
    template = jinja_env.get_template(template_filename.name)
    return template.render(records=config, record_map=SUPPORTED_RECORD_MAP,
                           **macros)


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
        '--template', default='pvnotepad_template.cfg', type=str,
        help='Template filename'
    )

    parser.add_argument(
        '--macro-file', type=str, required=False,
        help='Macros from a JSON file',
    )

    parser.add_argument(
        '-m', '--macro', type=str, nargs='*',
        help='Macro in the form key=value'
    )

    return parser


if __name__ == '__main__':
    parser = _get_argparser()
    args = parser.parse_args()

    print(args)

    config = load_json(args.config_file)
    macros = load_json(args.macro_file) if args.macro_file else {}
    for macro in args.macro or []:
        key, value = macro.split('=', 1)
        macros[key] = value

    config_lines = create_configuration(
        template_filename=args.template,
        config=config,
        macros=macros,
    )

    if args.output == '-':
        print(config_lines)
    else:
        with open(args.output, 'wt') as f:
            print(config_lines, file=f)
