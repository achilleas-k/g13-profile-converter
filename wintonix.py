import xml.etree.ElementTree as ET
import sys
import os.path


def get_elements(filename):
    print("\n\nParsing %s" % filename)
    tree = ET.parse(filename)
    root = tree.getroot()

    profile = root[0]
    profile_name = profile.attrib['name']
    profile_id = profile.attrib['guid']
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
            'baclight': backlight_elem,
            }

def get_macros(macros_elem):
    print("Building macro list ...")
    macros = []
    for macro_el in macros_elem:
        newmacro = {}
        newmacro['name'] = macro_el.get('name')
        newmacro['guid'] = macro_el.get('guid')
        for mec in macro_el.getchildren():
            for mecc in mec.getchildren():
                newmacro['key'] = mecc.get('value')
        macros.append(newmacro)
    return macros

def get_assignments(assignments_elem):
    print("Building assingment list ...")
    assignments = []
    for assign_el in assignments_elem:
        newassign = {}
        newassign['gkey'] = assign_el.get('contextid')
        newassign['guid'] = assign_el.get('macroguid')
        assignments.append(newassign)
    return assignments

def assign_macros(macros, assignments):
    macro_indexer = dict((macro['guid'], i) for i, macro in enumerate(macros))
    #assign_indexer = dict((assign['guid'], i) for i, assign in enumerate(assignments))
    print("Merging lists ...")
    target_assignments = []
    for assign in assignments:
        guid = assign['guid']
        mindex = macro_indexer.get(guid)
        if mindex is None:
            print("Macro with guid %s not found" % guid)
            continue
        cur_macro = macros[mindex]
        cur_gkey = assign['gkey'].lower()
        cur_kkey = cur_macro['key']
        cur_name = cur_macro['name']
        cur_type = "mapped-to-key" # only mapped-to-key supported for now
        cur_maptype = "keyboard"  # only keyboard supported for now
        # TODO: keyboard key translation required -- build a file with associations
        configstring =  ("keys_%s_name = %s\n"
                        "keys_%s_type = %s\n"
                        "keys_%s_maptype = %s\n"
                        "keys_%s_mappedkey = %s\n" % (cur_gkey, cur_name,
                                                        cur_gkey, cur_type,
                                                        cur_gkey, cur_maptype,
                                                        cur_gkey, cur_kkey))
        target_assignments.append(configstring)
    return target_assignments

def build_macro_file_text(profile_name, assignments):
    print("Building output ...")
    macros_file_text = (
                "[DEFAULT]\n"
                "name = %s\n"
                "version = 1.0\n"
                "icon = \n"
                "window_name =\n"
                "base_profile = \n"
                "background = \n"
                "author = \n"
                "activate_on_focus = False\n"
                "plugins_mode = all\n"
                "selected_plugins = ,profiles,menu\n"
                "send_delays = True\n"
                "fixed_delays = False\n"
                "press_delay = 50\n"
                "release_delay = 50\n"
                "models = g13\n"
                "\n"
                "[m1]\n"
                        % (profile_name))
    for ta in assignments:
        macros_file_text += ta
    # TODO: Grab backlight colour too
    macros_file_text += (
                "[m2]\n"
                "\n"
                "[m3]\n"
                "\n"
                "[m1-1]\n"
                "\n"
                "[m2-1]\n"
                "\n"
                "[m3-1]\n"
                "\n"
                "[m1-2]\n"
                "backlight_color = 11,0,255\n"
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
    output_file_name = output_file_name_base
    while os.path.exists(output_file_name):
        print("WARNING: file \"%s\" already exists: " % (output_file_name))
        overwrite = ""
        while overwrite not in "yYnN":
            overwrite = raw_input("Overwrite file? [y/n] ")
        if overwrite in "nN":
            output_file_name = raw_input("Enter new filename: ")
        elif overwrite in "yY":
            os.remove(output_file_name)
    with open(output_file_name, 'w') as of:
        of.write(macros_file_text)
    print("Profile written to \"%s\"" % output_file_name)

if __name__=="__main__":
    filename = sys.argv[1] # TODO: check cl arguments
    elements = get_elements(filename)
    macros_elem = elements['macros']
    macros = get_macros(macros_elem)
    assignments_elem = elements['assignments']
    assignments = get_assignments(assignments_elem)
    macro_assignments = assign_macros(macros, assignments)
    profile_name = elements['pname']
    file_contents = build_macro_file_text(profile_name, assignments)
    save_macro_file(filename, file_contents)






