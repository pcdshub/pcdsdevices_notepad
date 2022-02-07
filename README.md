PCDSDevices Notepad IOC with happi-based autodiscovery mechanism
================================================================

This repository contains a
[pvNotepad](https://github.com/pcdshub/pvNotepad)-compatible configuration file
generation tool.

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
$ make iocs
```

It's also possible to combine the above two steps, of course:

```bash
# Update the configuration files and update the checked out version of the
# hutch's IOC:
$ make clean all iocs
```

For more information on this step, see [config/iocs/README.md].
