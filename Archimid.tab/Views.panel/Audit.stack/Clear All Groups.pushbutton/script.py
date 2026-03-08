# -*- coding: utf-8 -*-
__title__ = "Clear Groups"
__doc__ = """
Explode selected Model/Detail Groups 
and Delete them from Project Browser.
Author: Yousef Gamal
"""

from Autodesk.Revit.DB import *
from pyrevit import forms, script

doc = __revit__.ActiveUIDocument.Document

# Collect all Group Types
group_types = list(FilteredElementCollector(doc).OfClass(GroupType))

if not group_types:
    forms.alert("No groups found in this project.", exitscript=True)

group_names = []
group_map = {}

for gt in group_types:
    try:
        # SAFE WAY to get name
        name_param = gt.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
        name = name_param.AsString() if name_param else "Unnamed Group"

        display = "{} (ID: {})".format(name, gt.Id.IntegerValue)
        group_names.append(display)
        group_map[display] = gt
    except:
        continue

if not group_names:
    forms.alert("No valid groups found.", exitscript=True)

selected = forms.SelectFromList.show(
    sorted(group_names),
    title="Select Group to Explode & Delete",
    multiselect=False
)

if not selected:
    script.exit()

group_type = group_map[selected]

confirm = forms.alert(
    "Explode ALL instances and delete this group type?",
    yes=True,
    no=True
)

if not confirm:
    script.exit()

t = Transaction(doc, "Explode & Delete Group")
t.Start()

# Explode instances
instances = FilteredElementCollector(doc).OfClass(Group)

for inst in instances:
    if inst.GroupType.Id == group_type.Id:
        inst.Ungroup()

# Delete type
doc.Delete(group_type.Id)

t.Commit()

forms.alert("Group deleted successfully.")