import json
import logging
import sys
import typing

import happi
import ophyd
import pcdsdevices

logger = logging.getLogger(__name__)


def get_all_devices(
        client: happi.Client = None
        ) -> typing.Generator[ophyd.Device, None, None]:
    """
    Get all devices from a given happi client.

    Parameters
    ----------
    client : happi.Client

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


def find_notepad_signals():
    patch_and_use_dummy_shim()

    def is_notepad_signal(obj):
        return isinstance(obj, pcdsdevices.signal.NotepadLinkedSignal)

    found = {}
    for dev in get_all_devices():
        for sig in get_components_matching(dev, predicate=is_notepad_signal):
            metadata = sig.notepad_metadata
            found[metadata['read_pv']] = metadata

    return list(metadata for key, metadata in
                sorted(found.items(), key=lambda keyval: keyval[0]))


if __name__ == '__main__':
    try:
        target_filename = sys.argv[1]
    except Exception:
        target_filename = '-'

    found = find_notepad_signals()

    if target_filename == '-':
        print(json.dumps(found))
    else:
        with open(target_filename, 'wt') as f:
            json.dump(found, f)
