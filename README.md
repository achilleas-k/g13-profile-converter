g13-profile-converter
===========

Windows to Linux profile migration/conversion tool for Logitech G13 gameboard.  Converts
the XML files exported from the Windows G13 software to the format used by the
Gnome15 suite.


Usage
-----

    python wintonix.py [options] PROFILE

where PROFILE is a game profile (XML format) exported from the Windows G13
profile manager.

Options:

    -h, --help              show this help message and exit
    --format=FORMAT         output format: valid values are "mzip" and "bind"
                            (default: mzip)
    -f, --force             force overwrite: overwrite destination file without
                            asking
    -o OUTFILE, --output=OUTFILE
                            output file: destination file (defaults to input file
                            basename with appropriate extension)
    -k KEYDEF, --keydef=KEYDEF
                            keydef file: mappings from the Windows XML file to the
                            corresponding Gnome15 key names (default: keydef.cfg)

Formats
-------
The `mzip` format is intended to be used with [Gnome15](https://projects.russo79.com/projects/gnome15).
The resulting file is a standard Zip file, but requires the `.mzip` extension to be imported into the configuration tool.

The `bind` format is intended to be used with [ecraven's userspace driver](https://github.com/ecraven/g13).

Limitations (missing features)
-----------
- Currently, the resulting profile only assigns direct key bindings (`G key : keyboard key/combo`).
- For the `bind` format, only the first bank, `M1`, is converted, since ecraven's driver doesn't handle bank switching.
- Macros and other options are planned for the future (for Gnome15).
- Bindings to the thumbstick are ignored.
- Key delays (send\_delays, fixed\_delays, press\_delay, release\_delay) are all set to default values for Gnome15 `mzip` profiles.
    - The values are `True`, `False`, `50` and `50`, respectively.
    - ecraven's driver doesn't support delays.
- Backlight colours ignored.
