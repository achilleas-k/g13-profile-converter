"""
The profile class

This object holds the internal representation for a loaded profile.
"""

class Profile:
    def __init__(self, name=None, profile_id=None, macros={}, assignments={},
                 backlight=None):
        self.name = name
        self.profile_id = profile_id
        self.macros = macros
        self.assignments = assignments
        self.backlight = backlight

    def save_bind(self):
        """
        Save the configuration as a `.bind` file, which can be used with the
        ecraven userspace driver (https://github.com/ecraven/g13).
        """

    def save_gnome15(self):
        """
        Save the configuration as a `.mzip` file, which can be imported into
        the gnome15 profile editor (https://projects.russo79.com/projects/gnome15)
        """


