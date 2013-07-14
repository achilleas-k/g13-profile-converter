g13wintonix
===========

Windows to Linux profile migration tool for Logitech G13 gameboard


USAGE:

    python wintonix.py profile.xml

where `profile.xml` is a game profile exported from the Windows G13 profile
manager.

The script generates a file called `profile.macros`, which should be zipped,
renamed from `profile.zip` to `profile.mzip` and imported into g15-config.

The script only handles the M1 bindings and does not transfer the backlight
colour. Also, all key bindings are assumed to be keyboard keys (no macros or
custom delays supported yet).



