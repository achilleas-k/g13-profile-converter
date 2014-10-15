"""

   Copyright 2013 Achilleas Koutsou

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""
import sys
import os.path
from optparse import OptionParser
from g13profile import G13Profile

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def load_keydef(keydef_file):
    if not os.path.isfile(keydef_file):
        print("Error: Keydef file %s does not exist or is not a valid file." % (
            keydef_file),
              file=sys.stderr)
        sys.exit(2)
    deflines = open(keydef_file, 'r').readlines()
    keydef = {}
    for dl in deflines:
        dl = dl.strip()
        if dl.startswith("#") or not dl:
            continue
        winkey, linuxkey = dl.split(':')
        winkey = winkey.strip()
        linuxkey = linuxkey.strip()
        keydef[winkey] = linuxkey
    return keydef

def setupOptionParser():
    parser = OptionParser()
    parser.add_option("--format", action="store",
                      type="string", dest="format",
                      help=("output format: valid values are "
                            "\"mzip\" and \"bind\" (default: mzip)"),
                      metavar="FORMAT", default="mzip")
    parser.add_option("-f", "--force", action="store_true", dest="force",
                      help=("force overwrite: overwrite destination file "
                            "without asking"))
    parser.add_option("-o", "--output", action="store",
                      type="string", dest="outfile",
                      help=("output file: destination file (defaults to input "
                            "file basename with appropriate extension)"))
    parser.add_option("-k", "--keydef", action="store",
                      type="string", dest="keydef",
                      help=("keydef file: mappings from the Windows XML file to"
                            " the corresponding Gnome15 key names (default: %default)"),
                      metavar="KEYDEF", default="keydef.cfg")
    parser.usage = "usage: %prog [options] filename"
    return parser

def create_outfilename(inputfile, outfmt, outfilename):
    if outfilename is None:
        output_file_name_base = os.path.split(filename)[-1]
        output_file_name_base = os.path.splitext(output_file_name_base)[0]
        output_file_name = output_file_name_base+"."+outfmt
    else:
        output_file_name = outfilename
    return output_file_name


if __name__=="__main__":
    parser = setupOptionParser()
    options, args = parser.parse_args()
    if len(args) == 0:
        print("ERROR: No filename supplied.")
        sys.exit(2)
    filename = args[0]
    xmlstring = open(filename).read()
    keydef_file = options.keydef
    keydef = load_keydef(keydef_file)
    outfmt = options.format
    outfilename = create_outfilename(filename, outfmt, options.outfile)
    force_overwrite = options.force
    if outfmt not in ["bind", "mzip"]:
        print("ERROR: Invalid format specified (%s)" % outfmt,
              file=sys.stderr)
        sys.exit(2)
    bindingobj = G13Profile(xmlstring, keydef)
    if outfmt == "bind":
        bindingobj.save_bind(outfilename, force_overwrite)
    elif outfmt == "mzip":
        bindingobj.save_gnome15(outfilename, force_overwrite)
