PCDSDevices Notepad IOC with happi-based autodiscovery mechanism
================================================================

Example:

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
