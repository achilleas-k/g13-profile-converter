import xml.etree.ElementTree as ET

filename = sys.argv[1] # TODO: check arguments

tree = ET.parse(filename)
root = tree.getroot()

profile = root[0]
profile_name = profile.attrib['name']
profile_id = profile.attrib['guid']
for pchild in profile:
    if "macros" in pchild.tag:
        macros_elems = pchild
    elif "assignments" in pchild.tag:
        assignments_elems = pchild
    elif "backlight" in pchild.tags:
        backlight_elems = pchild

macros = []
for macro_el in macros_elems:
    newmacro = {}
    newmacro['name'] = macro_el.get('name')
    newmacro['guid'] = macro_el.get('guid')
    newmacro['key'] = macro_el.getchildren()[0].getchildren()[0].get('value')
                        # ^^^ ugly, but works
    macros.append(newmacro)

assignments = []
for assign_el in assignments_elems:
    newassign = {}
    newassign['gkey'] = assign_el.get('contextid')
    newassign['macroguid'] = assign_el.get('macroguid')
    assignments = newassign







