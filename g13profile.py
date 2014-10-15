"""
The profile class

This object holds the internal representation for a loaded profile.
"""
import os
import sys
import getpass
from zipfile import ZipFile
import xml.etree.ElementTree as ET

class G13Profile(object):
    def __init__(self, xmlstring, keydef=None):
        self.keydef = keydef
        self.parse_windows_xml(xmlstring)
        self.g15text = None
        self.bindtext = None

    @staticmethod
    def _find_assignments(macros_elem, assignments_elem, keydef):
        """
        Matches macros with assignments
        """
        print("Creating bindings ...")
        macros = G13Profile._get_macros(macros_elem)
        assignments = G13Profile._get_assignments(assignments_elem)
        macro_indexer = dict((macro['guid'], i) for i, macro in enumerate(macros))
        #assign_indexer = dict((assign['guid'], i) for i, assign in enumerate(assignments))
        bank_assignments = {'m1': {}, 'm2': {}, 'm3': {}}
        for assign in assignments:
            guid = assign['guid']
            mindex = macro_indexer.get(guid)
            if mindex is None:
                print("WARNING: Macro with guid %s not found" % guid,
                      file=sys.stderr)
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
                # TODO: Handle different types
                cur_type = "mapped-to-key"
                cur_maptype = "keyboard"
                cur_name = cur_macro['name']
                bank_assignments[bank][cur_gkey] = {
                    "name": cur_name,
                    "type": cur_type,
                    "maptype": cur_maptype,
                    "key": cur_kkey
                }
        return bank_assignments

    @staticmethod
    def _get_macros(elements):
        print("Building macro list ...")
        macros = []
        for macro_el in elements:
            newmacro = {}
            newmacro['name'] = macro_el.get('name')
            newmacro['guid'] = macro_el.get('guid')
            # TODO: Handle XMLNS (xml namespace); i.e., REMOVE
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

    @staticmethod
    def _get_assignments(elements):
        print("Building assingment list ...")
        assignments = []
        for assign_el in elements:
            newassign = {}
            newassign['gkey'] = assign_el.get('contextid')
            newassign['bank'] = 'm'+assign_el.get('shiftstate')
            newassign['guid'] = assign_el.get('macroguid')
            assignments.append(newassign)
        return assignments

    def parse_windows_xml(self, xmlstring):
        """
        Parses windows configuration XML string and stores the information in
        the appropriate attributes.
        """
        print("Parsing windows XML profile ...")
        root = ET.fromstring(xmlstring)
        xmlprofile = root[0]
        self.name = xmlprofile.attrib['name']
        self.profile_id = xmlprofile.attrib['guid']
        self.author = getpass.getuser
        macros_elem = None
        assignments_elem = None
        for pchild in xmlprofile:
            if "macros" in pchild.tag:
                macros_elem = pchild
            elif "assignments" in pchild.tag:
                assignments_elem = pchild
            elif "backlight" in pchild.tag:
                self.backlight = pchild
        self.assignments = G13Profile._find_assignments(macros_elem,
                                                       assignments_elem,
                                                       self.keydef)

    def build_macro_file_text(self):
        """
        Construct the file text for the Gnome15 configuration file.
        """
        print("Building output ...")
        bank_strings = {'m1': '', 'm2': '', 'm3': ''}
        for bank, gkey_assignment in self.assignments.items():
            for gkey, assign_info in gkey_assignment.items():
                configstring =  (
                        "keys_{gkey}_name = {name}\n"
                        "keys_{gkey}_type = {type}\n"
                        "keys_{gkey}_maptype = {maptype}\n"
                        "keys_{gkey}_mappedkey = {kkey}\n".format(
                            gkey=gkey, name=assign_info["name"],
                            type=assign_info["type"],
                            maptype=assign_info["maptype"],
                            kkey=assign_info["key"]
                        )
                )
                bank_strings[bank] += configstring
        macros_file_text = (
            "[DEFAULT]\n"+
            "name = %s\n" % (self.name)+
            "version = 1.0\n"+
            "icon = \n"+
            "window_name =\n"+
            "base_profile = \n"+
            "background = \n"+
            "author = %s\n" % (self.author)+
            "activate_on_focus = False\n"+
            "plugins_mode = all\n"+
            "selected_plugins = ,profiles,menu\n"+
            "send_delays = True\n"+
            "fixed_delays = False\n"+
            "press_delay = 50\n"+
            "release_delay = 50\n"+
            "models = g13\n"
        )
        for bank, configstring in bank_strings.items():
            macros_file_text += (
                "[%s]\n%s\n" % (bank, configstring)
            )
        macros_file_text += (
            "\n"
            "[m1-1]\n"
            "\n"
            "[m2-1]\n"
            "\n"
            "[m3-1]\n"
            "\n"
            "[m1-2]\n"
            "\n"
            "[m2-2]\n"
            "\n"
            "[m3-2]\n"
            "\n\n"
        )
        self.g15text = macros_file_text

    def save_gnome15(self, filename, force_overwrite):
        """
        Save the configuration as a `.mzip` file, which can be imported into
        the gnome15 profile editor (https://projects.russo79.com/projects/gnome15)
        """
        self.build_macro_file_text()
        text = self.g15text
        print("Writing Gnome15 .mzip file ...")
        output_file_name_base = os.path.splitext(filename)[0]
        macros_file_name = output_file_name_base+".macros"
        if not force_overwrite:
            while os.path.exists(filename):
                print("\"%s\" already exists: " % (filename))
                overwrite = "_"
                while overwrite not in "yYnN":
                    overwrite = input("Overwrite file? [y/n] ")
                if overwrite in "nN":
                    filename = input("Enter new filename: ")
                elif overwrite in "yY":
                    os.remove(filename)
        with ZipFile(filename, 'w') as of:
            of.writestr(macros_file_name, text)
        print("Profile written to \"%s\"" % filename)

    def build_bind_file_text(self):
        """
        Construct the file text for the ecraven bind file.
        """
        text = ""
        for key, binding in self.assignments:
            text += "bind "+key.upper()+" "+binding.upper()+"\n"
        self.bindtext = text

    def save_bind(self, filename, force_overwrite):
        """
        Save the configuration as a `.bind` file, which can be used with the
        ecraven userspace driver (https://github.com/ecraven/g13).
        """
        self.build_bind_file_text()
        text = self.bindtext
        print("Writing ecraven .bind file ...")
        if not force_overwrite:
            while os.path.exists(filename):
                print("\"%s\" already exists: " % (filename))
                overwrite = "_"
                while overwrite not in "yYnN":
                    overwrite = input("Overwrite file? [y/n] ")
                if overwrite in "nN":
                    filename = input("Enter new filename: ")
                elif overwrite in "yY":
                    os.remove(filename)
        with open(filename, 'w') as of:
            of.write(text)
        print("Profile written to \"%s\"" % filename)
