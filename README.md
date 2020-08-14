PCDSDevices Notepad IOC with happi-based autodiscovery mechanism
================================================================

Example:

```bash
$ python notepad_finder.py config.json
$ python ioc.py --list-pvs
[I 15:42:45.705       server:  133] Asyncio server starting up...
[I 15:42:45.705       server:  146] Listening on 0.0.0.0:5064
[I 15:42:45.708       server:  205] Server startup complete.
[I 15:42:45.708       server:  207] PVs available:
    PCDSDEVICES:Notepad:autosave_helper::__autosave_hook__
    PCDSDEVICES:Notepad:file_checker_helper
    XCS:MON:MPZ:01:OphydReadback
    XCS:MON:MPZ:01:OphydSetpoint
    XPP:MON:MPZ:07A:OphydReadback
    XPP:MON:MPZ:07A:OphydSetpoint
```
