import json

from caproto.server import (PVGroup, SubGroup, pvproperty, run,
                            template_arg_parser)
from caproto.server.autosave import (AutosaveHelper, RotatingFileManager,
                                     autosaved)


def pvproperty_from_metadata(
        name,
        read_pv, write_pv=None,
        default_value=0.0, record='ai',
        lower_ctrl_limit=None, upper_ctrl_limit=None,
        lower_alarm_limit=None, upper_alarm_limit=None,
        owner_type=None, dotted_name=None,
        signal_kwargs=None,
        **other_metadata
        ):

    pvproperty_kwargs = dict(
        value=default_value,
        doc=other_metadata.get('doc', dotted_name),
    )

    if isinstance(default_value, (float, int)):
        for key in ('lower_ctrl_limit', 'upper_ctrl_limit',
                    'lower_alarm_limit', 'upper_alarm_limit'):
            if locals()[key] is not None:
                pvproperty_kwargs[key] = locals()[key]

    result = {}
    result[name] = autosaved(
        pvproperty(record=record,
                   name=read_pv,
                   read_only=write_pv is not None,
                   **pvproperty_kwargs,
                   )
    )

    if write_pv is not None:
        prop = pvproperty(record=record,
                          name=write_pv,
                          read_only=False,
                          **pvproperty_kwargs,
                          )
        result[name + '_write'] = autosaved(prop)

        @prop.putter
        async def prop_putter(self, instance, value):
            read_attr = getattr(self, name)
            await read_attr.write(value)

    return result


class PcdsdevicesNotepad(PVGroup):
    """
    """
    autosave_helper = SubGroup(AutosaveHelper)
    file_checker_helper = pvproperty(
        value=0,
        doc='Helper to periodically reload the config file'
    )

    def _find_new_properties(self, config_items):
        props = {}
        for metadata in config_items:
            if metadata['read_pv'] not in self.pvdb:
                for attr, prop in pvproperty_from_metadata(**metadata).items():
                    props[attr] = prop

        return props

    def _add_to_pvdb(self, props):
        new_cls = type('FakeGroup', (PVGroup, ), props)
        inst = new_cls(prefix='')
        for pv in inst.pvdb:
            self.log.info('New PV available: %s', pv)

        # Combine it all...
        for attr in inst._pvs_:
            setattr(self, attr, getattr(inst, attr))

        self.pvdb.update(**inst.pvdb)
        self._pvs_.update(**inst._pvs_)

    @file_checker_helper.startup
    async def file_checker_helper(self, instance, async_lib):
        self.async_lib = async_lib
        while True:
            self._update_database()
            await async_lib.library.sleep(10)

    def _get_properties_from_autosave(self, autosaved_data):
        """
        Carry forward autosaved PVs that aren't in pcdsdevices currently,
        just in case.

        Since this is a lossy operation without access to that information,
        this makes a couple arbitrary choices: sequential attribute names and
        picking the `ai` record .
        """
        props = {}
        for idx, (pv, info) in enumerate((autosaved_data or {}).items()):
            props[f'autosaved_carryover_{idx}'] = pvproperty(
                value=info['value'], name=pv, record='ai'
            )

        return props

    def _update_database(self, autosaved_data=None):
        with open(self.config_file) as f:
            config_items = json.load(f)

        props = self._find_new_properties(config_items)

        # Aggregate all of the new property PV names:
        pvs = set(prop.pvspec.name for prop in props.values())

        for attr, prop in (autosaved_data or {}).items():
            if prop.pvspec.name not in pvs:
                self.log.warning(
                    'PV %r from autosave not found from happi. Adding as an '
                    '`ai` record with attribute=%s value=%s',
                    prop.pvspec.name, attr, prop.pvspec.value
                )
                props[attr] = prop
                pvs.add(prop.pvspec.name)

        if props:
            self._add_to_pvdb(props)

        return props

    def __init__(self, config_file, autosaved_data, **kwargs):
        super().__init__(**kwargs)
        self._first_update = True
        self.config_file = config_file
        autosaved_props = self._get_properties_from_autosave(autosaved_data)
        self._update_database(autosaved_props)


def create_ioc(config_file, *, autosave_path, **ioc_options):
    """IOC Setup."""

    try:
        with open(autosave_path) as f:
            autosaved_data = json.load(f)
    except Exception:
        autosaved_data = {}

    ioc = PcdsdevicesNotepad(config_file=config_file,
                             autosaved_data=autosaved_data,
                             **ioc_options)
    ioc.autosave_helper.filename = autosave_path
    ioc.autosave_helper.file_manager = RotatingFileManager(autosave_path)

    return ioc


if __name__ == '__main__':
    parser, split_args = template_arg_parser(
        default_prefix='PCDSDEVICES:Notepad:',
        desc='PCDSDevices PV notepad IOC'
    )

    parser.add_argument(
        '--config', dest='config_file', type=str,
        default='config.json',
        help='Notepad configuration file location (default: config.json)',
    )

    parser.add_argument(
        '--autosave', dest='autosave_path', type=str,
        default='notepad_autosave.json',
        help='Notepad autosave file location (default: notepad_autosave.json)',
    )

    args = parser.parse_args()
    ioc_options, run_options = split_args(args)
    ioc = create_ioc(config_file=args.config_file,
                     autosave_path=args.autosave_path,
                     **ioc_options)
    run(ioc.pvdb, **run_options)
