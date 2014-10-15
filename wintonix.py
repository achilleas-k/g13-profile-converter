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
import xml.etree.ElementTree as ET
import sys
import os.path
from optparse import OptionParser
from g13profile import G13Profile

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def verboseprint(output):
    print(output, file=sys.stderr)

def load_keydef(keydef_file):
    if not os.path.isfile(keydef_file):
        print("Error: Keydef file %s does not exist or is not a valid file." % (
            keydef_file),
              file=sys.stderr)
        sys.exit(2)
    deflines = open(keydef_file, 'r').readlines()
    verboseprint("Keydef file %s loaded successfully." % (keydef_file))
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

def get_elements(filename):
    if not os.path.isfile(filename):
        print("Error: input file %s does not exist." % filename,
              file=sys.stderr)
        sys.exit(2)
    print("\n\nParsing %s" % filename)
    tree = ET.parse(filename)
    root = tree.getroot()
    profile = root[0]
    verboseprint(profile)
    profile_name = profile.attrib['name']
    profile_id = profile.attrib['guid']
    verboseprint("Profile name: %s, ID: %s" % (profile_name, profile_id))
    macros_elem = None
    assignments_elem = None
    backlight_elem = None
    for pchild in profile:
        if "macros" in pchild.tag:
            macros_elem = pchild
        elif "assignments" in pchild.tag:
            assignments_elem = pchild
        elif "backlight" in pchild.tag:
            backlight_elem = pchild
    return {
            'pname': profile_name,
            'pid': profile_id,
            'macros': macros_elem,
            'assignments': assignments_elem,
            'backlight': backlight_elem,
            }

def get_macros(macros_elem):
    print("Building macro list ...")
    macros = []
    for macro_el in macros_elem:
        newmacro = {}
        newmacro['name'] = macro_el.get('name')
        verboseprint("New macro: %s" % (newmacro['name']))
        newmacro['guid'] = macro_el.get('guid')
        verboseprint("\tguid: %s" % (newmacro['guid']))
        # TODO: Handle XMLNS (xml namespace); i.e., REMOVE
        for mec in macro_el.getchildren():
            newmacro['type'] = mec.tag
            verboseprint("\tmacro type: %s" % (newmacro['type']))
            newmacro['keyseq'] = []
            # TODO: separate types:
            #       - keystroke
            #       - multikey
            #       - textblock
            #       - mousefunction
            for mecc in mec.getchildren():
                newmacro['keyseq'].append(mecc.get('value'))
            verboseprint("\tkeyseq: %s" % (newmacro['keyseq']))
        macros.append(newmacro)
    return macros

def get_assignments(assignments_elem):
    print("Building assingment list ...")
    assignments = []
    for assign_el in assignments_elem:
        newassign = {}
        newassign['gkey'] = assign_el.get('contextid')
        newassign['bank'] = 'm'+assign_el.get('shiftstate')
        newassign['guid'] = assign_el.get('macroguid')
        verboseprint("New assignment:\n"+
                "\tKey: %s\n" % (newassign['gkey'])+
                "\tBank: %s\n" % (newassign['bank'])+
                "\tMacro guid: %s\n" % (newassign['guid']))
        assignments.append(newassign)
    return assignments

def assign_macros(macros, assignments, keydef):
    macro_indexer = dict((macro['guid'], i) for i, macro in enumerate(macros))
    #assign_indexer = dict((assign['guid'], i) for i, assign in enumerate(assignments))
    print("Merging lists ...")
    target_assignments = {'m1': '', 'm2': '', 'm3': ''}
    for assign in assignments:
        guid = assign['guid']
        mindex = macro_indexer.get(guid)
        if mindex is None:
            print("Macro with guid %s not found" % guid)
            continue
        cur_macro = macros[mindex]
        cur_gkey = assign['gkey'].lower()
        bank = assign['bank']
        cur_kkey = ''
        if ('keyseq' in cur_macro and
                len(cur_macro['keyseq']) and
                cur_macro['keyseq'][0] is not None):
            # macro may not be assigned to key sequence
            # NOTE: Just taking the first one for now
            firstkey = cur_macro['keyseq'][0]
            if firstkey in keydef:
                cur_kkey = keydef[firstkey]
            else:
                cur_kkey = "KEY_"+firstkey
            cur_name = cur_macro['name']
            # TODO: Handle different types
            cur_type = "mapped-to-key"
            cur_maptype = "keyboard"
            configstring =  (
                    "keys_%s_name = %s\n"
                    "keys_%s_type = %s\n"
                    "keys_%s_maptype = %s\n"
                    "keys_%s_mappedkey = %s\n" % (cur_gkey, cur_name,
                                                    cur_gkey, cur_type,
                                                    cur_gkey, cur_maptype,
                                                    cur_gkey, cur_kkey)
                    )

            target_assignments[bank]+=configstring
    return target_assignments

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
    parser.add_option("-v", action="store_true", dest="verbose",
                      help="enable verbose output")
    parser.usage = "usage: %prog [options] filename"
    return parser


if __name__=="__main__":
    # TODO: Update readme
    parser = setupOptionParser()
    options, args = parser.parse_args()
    if not options.verbose:
        verboseprint = lambda *a: None
    if len(args) == 0:
        print("ERROR: No filename supplied.")
        sys.exit(1)
    filename = args[0]
    keydef_file = options.keydef
    keydef = load_keydef(keydef_file)
    outfmt = options.format
    outfilename = options.outfile
    force_overwrite = options.force
    # TODO: Handle other options
    if outfilename is None:
        outfilename = filename
        # TODO: Handle extension(s)
    if outfmt not in ["bind", "mzip"]:
        print("ERROR: Invalid format specified (%s)" % outfmt,
              file=sys.stderr)
        sys.exit(2)
    elements = get_elements(filename)
    macros_elem = elements['macros']
    macros = get_macros(macros_elem)
    assignments_elem = elements['assignments']
    assignments = get_assignments(assignments_elem)
    macro_assignments = assign_macros(macros, assignments, keydef)
    profile_name = elements['pname']
    bindingobj = G13Profile(name=elements['pname'], profile_id=elements['pid'],
                      assignments=macro_assignments)
    if outfmt == "bind":
        bindingobj.save_bind(outfilename, force_overwrite)
    elif outfmt == "mzip":
        bindingobj.save_gnome15(outfilename, force_overwrite)
