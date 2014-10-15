"""
The profile class

This object holds the internal representation for a loaded profile.
"""
import os
from zipfile import ZipFile
import getpass
import xml.etree.ElementTree as ET

class G13Profile(object):
    def __init__(self, name=None, profile_id=None, assignments={},
                 backlight=None):
        self.name = name
        self.profile_id = profile_id
        self.assignments = assignments
        self.backlight = backlight
        self.g15text = None
        self.bindtext = None

    @staticmethod
    def _find_assignments(macros_elem, assignments_elem):
        """
        Matches macros with assignments
        """


    def parse_windows_xml(self, xmlstring):
        """
        Parses windows configuration XML string and stores the information in
        the appropriate attributes.
        """
        root = ET.fromstring(xmlstring)
        xmlprofile = root[0]
        self.name = xmlprofile.attrib['name']
        self.profile_id = xmlprofile.attrib['guid']
        macros_elem = None
        assignments_elem = None
        for pchild in xmlprofile:
            if "macros" in pchild.tag:
                macros_elem = pchild
            elif "assignments" in pchild.tag:
                assignments_elem = pchild
            elif "backlight" in pchild.tag:
                self.backlight = pchild
        self.assignments = self.find_assignments(macros_elem, assignments_elem)

    def build_macro_file_text(self):
        """
        Construct the file text for the Gnome15 configuration file.
        """
        print("Building output ...")
        macros_file_text = (
            "[DEFAULT]\n"+
            "name = %s\n" % (self.name)+
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
            "models = g13\n"
        )
        for midx in range(1, 4):
            mstr = "m%i" % midx
            macros_file_text += (
                "[%s]\n%s\n" % (mstr, self.assignments[mstr])
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
        output_file_name_base = os.path.split(filename)[-1]
        output_file_name_base = os.path.splitext(output_file_name_base)[0]
        macros_file_name = output_file_name_base+".macros"
        output_file_name = output_file_name_base+".mzip"
        if not force_overwrite:
            while os.path.exists(output_file_name):
                print("\"%s\" already exists: " % (output_file_name))
                overwrite = "_"
                while overwrite not in "yYnN":
                    overwrite = input("Overwrite file? [y/n] ")
                if overwrite in "nN":
                    output_file_name = input("Enter new filename: ")
                elif overwrite in "yY":
                    os.remove(output_file_name)
        with ZipFile(output_file_name, 'w') as of:
            of.writestr(macros_file_name, text)
        print("Profile written to \"%s\"" % output_file_name)

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
        output_file_name_base = os.path.split(filename)[-1]
        output_file_name_base = os.path.splitext(output_file_name_base)[0]
        output_file_name = output_file_name_base+".bind"
        if not force_overwrite:
            while os.path.exists(output_file_name):
                print("\"%s\" already exists: " % (output_file_name))
                overwrite = "_"
                while overwrite not in "yYnN":
                    overwrite = input("Overwrite file? [y/n] ")
                if overwrite in "nN":
                    output_file_name = input("Enter new filename: ")
                elif overwrite in "yY":
                    os.remove(output_file_name)
        with open(output_file_name, 'w') as of:
            of.write(text)
        print("Profile written to \"%s\"" % output_file_name)
