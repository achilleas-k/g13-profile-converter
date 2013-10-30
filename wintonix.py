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
import getpass
from zipfile import ZipFile

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
KEYDEF_FILE = os.path.join(SCRIPT_DIR, "keydef.cfg")
KEYDEF = {}

def load_keydef(KEYDEF_FILE):
    deflines = open(KEYDEF_FILE, 'r').readlines()  # TODO: Check if file exists
    for dl in deflines:
        dl = dl.strip()
        if dl.startswith("#") or not dl:
            continue
        winkey, linuxkey = dl.split(':')
        winkey = winkey.strip()
        linuxkey = linuxkey.strip()
        KEYDEF[winkey] = linuxkey
    return


def get_elements(filename):
    print("\n\nParsing %s" % filename)
    tree = ET.parse(filename)
    root = tree.getroot()
    profile = root[0]
    profile_name = profile.attrib['name']
    profile_id = profile.attrib['guid']
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
        newmacro['guid'] = macro_el.get('guid')
        for mec in macro_el.getchildren():
            newmacro['type'] = mec.tag
            newmacro['keyseq'] = []
            # TODO: separate types:
            #       - keystroke
            #       - multikey
            #       - textblock
            #       - mousefunction
            for mecc in mec.getchildren():
                newmacro['keyseq'].append(mecc.get('value'))
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
        assignments.append(newassign)
    return assignments

def assign_macros(macros, assignments):
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
        if 'keyseq' in cur_macro and cur_macro['keyseq'][0] is not None:
            # macro may not be assigned to key sequence
            # NOTE: Just taking the first one for now
            firstkey = cur_macro['keyseq'][0]
            if KEYDEF.has_key(firstkey):
                cur_kkey = KEYDEF[firstkey]
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

def build_macro_file_text(profile_name, assignments):
    print("Building output ...")
    macros_file_text = (
                "[DEFAULT]\n"+
                "name = %s\n" % (profile_name)+
                "version = 1.0\n"+
                "icon = \n"+
                "window_name =\n"+
                "base_profile = \n"+
                "background = \n"+
                "author = %s\n" % (getpass.getuser())+
                "activate_on_focus = False\n"+
                "plugins_mode = all\n"+
                "selected_plugins = ,profiles,menu\n"+
                "send_delays = True\n"+
                "fixed_delays = False\n"+
                "press_delay = 50\n"+
                "release_delay = 50\n"+
                "models = g13\n"+
                "\n"+
                "[m1]\n"+
                assignments['m1']+
                "[m2]\n"+
                assignments['m2']+
                "[m3]\n"+
                assignments['m3']+

    # TODO: Grab backlight colour too
                "\n"
                "[m1-1]\n"
                "\n"
                "[m2-1]\n"
                "\n"
                "[m3-1]\n"
                "\n"
                "[m1-2]\n"
                "backlight_color = 11,0,255\n" # TODO: Why is this here?
                "\n"
                "[m2-2]\n"
                "\n"
                "[m3-2]\n"
                "\n\n"
            )
    return macros_file_text

def save_macro_file(filename, macros_file_text):
    print("Writing Linux .macros file ...")
    # TODO: Ask about overwriting or supplying new name
    output_file_name_base = os.path.splitext(filename)[0]
    macros_file_name = output_file_name_base+".macros"
    output_file_name = output_file_name_base+".mzip"
    while os.path.exists(output_file_name):
        print("WARNING: file \"%s\" already exists: " % (output_file_name))
        overwrite = "_"
        while overwrite not in "yYnN":
            overwrite = raw_input("Overwrite file? [y/n] ")
        if overwrite in "nN":
            output_file_name = raw_input("Enter new filename: ")
        elif overwrite in "yY":
            os.remove(output_file_name)
    with ZipFile(output_file_name, 'w') as of:
        of.writestr(macros_file_name, macros_file_text)
    print("Profile written to \"%s\"" % output_file_name)

if __name__=="__main__":
    filename = sys.argv[1]  # TODO: check cl arguments
    load_keydef(KEYDEF_FILE)
    elements = get_elements(filename)
    macros_elem = elements['macros']
    macros = get_macros(macros_elem)
    assignments_elem = elements['assignments']
    assignments = get_assignments(assignments_elem)
    macro_assignments = assign_macros(macros, assignments)
    profile_name = elements['pname']
    file_contents = build_macro_file_text(profile_name, macro_assignments)
    save_macro_file(filename, file_contents)






