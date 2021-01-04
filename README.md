PCDSDevices Notepad IOC with happi-based autodiscovery mechanism
================================================================

This repository contains a
[pvNotepad](https://github.com/pcdshub/pvNotepad)-compatible configuration file
generation tool as well as a prototype replacement caproto-based IOC.

pvNotepad
---------

To first make the configuration files in ``config/notepad``:

```bash
$ cd config

# Force the discovery mechanism to search happi again:
$ make clean

# Force the discovery mechanism to search again:
$ make
```

Then, perform most of the IOC updating by way of:

```bash
$ cd iocs
$ make
```

For more information on this step, see [config/iocs/README.md].

caproto
-------

The prototype caproto IOC (which is currently unused) uses configuration files
similarly to pvNotepad.  Generate those files first, then run the IOC::

```bash
$ make -C config
# Creates all configurations, per-beamline
$ python ioc.py --config config/xcs.json --list-pvs
[I 14:13:38.874       server:  133] Asyncio server starting up...
[I 14:13:38.874       server:  146] Listening on 0.0.0.0:5064
[I 14:13:38.877       server:  205] Server startup complete.
[I 14:13:38.877       server:  207] PVs available:
    PCDSDEVICES:Notepad:autosave_helper::__autosave_hook__
    PCDSDEVICES:Notepad:file_checker_helper
    XCS:MON:MMS:24:pseudo:OphydReadback
    XCS:MON:MMS:24:pseudo:OphydSetpoint
    XCS:MON:MMS:26:pseudo:OphydReadback
    XCS:MON:MMS:26:pseudo:OphydSetpoint
    XCS:MON:MPZ:01:energy:OphydReadback
    XCS:MON:MPZ:01:energy:OphydSetpoint
    XCS:MON:MPZ:01:theta:OphydReadback
    XCS:MON:MPZ:01:theta:OphydSetpoint
    XCS:MON:MPZ:01:wavelength:OphydReadback
    XCS:MON:MPZ:01:wavelength:OphydSetpoint
```
