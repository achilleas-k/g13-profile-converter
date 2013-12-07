g13-profile-migrator
===========

Windows to Linux profile migration tool for Logitech G13 gameboard.  Converts
the XML files exported from the Windows G13 software to the format used by the
Gnome15 suite.


USAGE:

    python wintonix.py [options] profile.xml

where `profile.xml` is a game profile exported from the Windows G13 profile
manager.

The script generates a file called `profile.mzip`, a zip archive which
conains the converted .macros profile and can be imported into
g15-connfig.


Options:
  -h, --help            show this help message and exit
  -k KEYDEF, --keydef=KEYDEF
                        keydef file: mappings from the Windows XML file to the
                        corresponding Gnome15 key names (default: keydef.cfg)
  -v                    enable verbose output


