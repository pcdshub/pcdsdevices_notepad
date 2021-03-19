"""
Notepad PV finder - search all happi devices for matching items.
"""

import argparse
import fnmatch
import json
import logging
import typing
from typing import Dict, List, Union

import happi
import ophyd
import pcdsdevices
import pcdsdevices.signal

logger = logging.getLogger(__name__)

# Stash the description for later usage by the CLI interface.
DESCRIPTION = __doc__.strip()
CriteriaDict = Dict[str, Union[float, str]],


def load_config(config_file: str) -> List[Dict[str, dict]]:
    with open(config_file) as f:
        return json.load(f)


def get_all_devices(
        client: happi.Client = None
        ) -> typing.Generator[ophyd.Device, None, None]:
    """
    Get all devices from a given happi client.

    Parameters
    ----------
    client : happi.Client, optional
        The happi client to use.  Defaults to using one from the environment
        configuration.

    Yields
    ------
    ophyd.Device
    """
    if client is None:
        client = happi.Client.from_config()

    for dev in client:
        try:
            obj = client[dev].get()
        except Exception:
            logger.exception('Failed to instantiate device: %s', obj)
        else:
            yield obj


def get_devices_by_criteria(
        search_criteria: CriteriaDict,
        *,
        client: happi.Client = None,
        regex: bool = True,
        ) -> typing.Generator[ophyd.Device, None, None]:
    """
    Get all devices from a given happi client.

    Parameters
    ----------
    search_criteria : dict
        Dictionary of ``{'happi_key': 'search_value'}``.

    client : happi.Client, optional
        The happi client to use.  Defaults to using one from the environment
        configuration.

    Yields
    ------
    ophyd.Device
    """
    if client is None:
        client = happi.Client.from_config()

    search_method = client.search_regex if regex else client.search
    for item in search_method(**search_criteria):
        try:
            obj = item.get()
        except Exception:
            logger.exception('Failed to instantiate device: %s', obj)
        else:
            yield obj


def get_components_matching(
        obj: ophyd.Device,
        predicate: callable,
        ) -> typing.Generator[ophyd.ophydobj.OphydObject, None, None]:
    """
    Find signals of a specific type from a given ophyd Device.

    Parameters
    ----------
    obj : ophyd.Device
        The ophyd Device.

    predicate : callable
        Callable that should return True on a match.

    Yields
    ------
    obj : ophyd.ophydobj.OphydObject
    """
    for walk in obj.walk_signals(include_lazy=True):
        try:
            included = predicate(walk.item)
        except Exception:
            logger.exception('Failed to check predicate against %s', walk)
        else:
            if included:
                yield walk.item


def patch_and_use_dummy_shim():
    """
    Hack ophyd and its dummy shim.  We don't want _any_ control-layer
    connections being made while we're looking for signals.

    Warning
    -------
    Under no circumstances should this be used in a production environment
    where you intend to actually _use_ ophyd for its intended purpose.
    """
    ophyd.Device.lazy_wait_for_connection = False

    def _no_op(*args, **kwargs):
        ...

    class _PVStandIn:
        _reference_count = 0

        def __init__(self, pvname, *args, **kwargs):
            self.pvname = pvname
            self.connected = True

        add_callback = _no_op
        remove_callback = _no_op
        clear_callbacks = _no_op
        get = _no_op
        put = _no_op
        get_with_metadata = _no_op
        wait_for_connection = _no_op

    def get_pv(pvname, *args, **kwargs):
        return _PVStandIn(pvname)

    from ophyd import _dummy_shim
    _dummy_shim.get_pv = get_pv
    _dummy_shim.release_pvs = _no_op
    ophyd.set_cl('dummy')


def find_signals(
        criteria: CriteriaDict,
        signal_class: type = pcdsdevices.signal.NotepadLinkedSignal,
        ) -> List[Dict[str, dict]]:
    """
    Find all signal metadata that match the given criteria.

    Returns
    -------
    items : list
        A list of all matching metadata.
    """

    patch_and_use_dummy_shim()

    def is_notepad_signal(obj):
        return isinstance(obj, signal_class)

    if not criteria:
        devices = get_all_devices()
    else:
        devices = get_devices_by_criteria(criteria)

    found = {}
    for dev in devices:
        for sig in get_components_matching(dev, predicate=is_notepad_signal):
            metadata = sig.notepad_metadata
            found[metadata['read_pv']] = metadata

    return list(metadata for key, metadata in
                sorted(found.items(), key=lambda keyval: keyval[0]))


def _parse_criteria(criteria_string: str) -> CriteriaDict:
    """
    Parse search criteria into a dictionary of ``{key: value}``.

    Converts floating point values to float.
    """
    search_args = {}
    for user_arg in args.search_criteria:
        if '=' in user_arg:
            criteria, value = user_arg.split('=', 1)
        else:
            criteria = 'name'
            value = user_arg

        if criteria in search_args:
            logger.warning(
                'Received duplicate search criteria %s=%r (was %r)',
                criteria, value, search_args[criteria]
            )
            continue

        try:
            value = float(value)
        except ValueError:
            value = fnmatch.translate(value)

        search_args[criteria] = value

    return search_args


def _get_argparser(parser: typing.Optional[argparse.ArgumentParser] = None):
    if parser is None:
        parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        '--output', default='-', type=str,
        help='File to write to (- for standard output)'
    )

    parser.add_argument(
        '--update', action='store_true',
        help=(
            'If `--output` is specified, load and update it instead of '
            'overwriting'
        )
    )

    parser.add_argument(
        'search_criteria', nargs='*',
        help='Search criteria: field=value'
    )
    return parser


if __name__ == '__main__':
    parser = _get_argparser()
    args = parser.parse_args()

    if args.update:
        try:
            config = load_config(args.output)
        except FileNotFoundError:
            logger.warning('--update specified but %s does not exist',
                           args.output)
            config = []
    else:
        config = []

    config_by_pvname = {item['read_pv']: item for item in config}

    criteria = _parse_criteria(args.search_criteria)
    for item in find_signals(criteria):
        read_pv = item['read_pv']
        if read_pv in config_by_pvname:
            # Update the existing item
            config_by_pvname.update(**item)
        else:
            # Add a new item
            config_by_pvname[read_pv] = item
            config.append(item)

    if args.output == '-':
        print(json.dumps(config, sort_keys=True, indent=4))
    else:
        with open(args.output, 'wt') as f:
            json.dump(config, f, sort_keys=True, indent=4)
