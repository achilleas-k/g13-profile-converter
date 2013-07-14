import xml.etree.ElementTree as ET
import sys

filename = sys.argv[1] # TODO: check arguments

print("\n\nParsing %s" % filename)
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
    elif "backlight" in pchild.tag:
        backlight_elems = pchild

print("Building macro list ...")
macros = []
for macro_el in macros_elems:
    newmacro = {}
    newmacro['name'] = macro_el.get('name')
    newmacro['guid'] = macro_el.get('guid')
    for mec in macro_el.getchildren():
        for mecc in mec.getchildren():
            newmacro['key'] = mecc.get('value')
                        # ^^^ ugly, but works
    macros.append(newmacro)

print("Building assingment list ...")
assignments = []
for assign_el in assignments_elems:
    newassign = {}
    newassign['gkey'] = assign_el.get('contextid')
    newassign['guid'] = assign_el.get('macroguid')
    assignments.append(newassign)

print("Building indexers ...")
macro_indexer = dict((macro['guid'], i) for i, macro in enumerate(macros))
assign_indexer = dict((assign['guid'], i) for i, assign in enumerate(assignments))


print("Merging lists ...")
target_assignments = []
for assign in assignments:
    guid = assign['guid']
    




