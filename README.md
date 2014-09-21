g13-profile-migrator
===========

Windows to Linux profile migration tool for Logitech G13 gameboard.  Converts
the XML files exported from the Windows G13 software to the format used by the
Gnome15 suite.


USAGE:

    python wintonix.py [options] PROFILE

where PROFILE is a game profile (XML format) exported from the Windows G13
profile manager.

The script generates a file with the same basename as PROFILE and the extension
`.mzip`, a zip archive which conains the converted .macros profile. The output
file can be imported into g15-config, the key configuration utility of the
[Gnome15 project](https://projects.russo79.com/projects/gnome15)


Options:

    -h, --help              show this help message and exit
    -k KEYDEF, --keydef=KEYDEF
                            keydef file: mappings from the Windows XML file to the
                            corresponding Gnome15 key names (default: keydef.cfg)
    -v                      enable verbose output


### TODO
Secondary output format for [ecraven/g13](https://github.com/ecraven/g13).
