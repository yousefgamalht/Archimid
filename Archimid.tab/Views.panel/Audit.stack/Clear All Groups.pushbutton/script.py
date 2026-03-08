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

# Collect all group instances
instances = list(FilteredElementCollector(doc).OfClass(Group))

if not instances:
    forms.alert("No group instances found in this project.", exitscript=True)

# Build dictionary of GroupType -> Category
group_map = {}

for inst in instances:
    gtype = inst.GroupType
    cat_name = inst.Category.Name if inst.Category else "Unknown"

    # Safe name extraction
    name_param = gtype.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
    name = name_param.AsString() if name_param else "Unnamed"

    group_type_label = "MODEL" if "Model" in cat_name else "DETAIL"

    display = "[{}] {} (ID: {})".format(
        group_type_label,
        name,
        gtype.Id.IntegerValue
    )

    group_map[display] = gtype

if not group_map:
    forms.alert("No valid groups found.", exitscript=True)

# Multi-select
selected = forms.SelectFromList.show(
    sorted(group_map.keys()),
    title="Select Groups to Explode & Delete",
    multiselect=True
)

if not selected:
    script.exit()

confirm = forms.alert(
    "Explode ALL instances and delete selected group types?",
    yes=True,
    no=True
)

if not confirm:
    script.exit()

t = Transaction(doc, "Explode & Delete Groups")
t.Start()

try:
    selected_types = [group_map[s] for s in selected]

    # Explode instances
    for inst in instances:
        if inst.GroupType in selected_types:
            inst.Ungroup()

    # Delete group types
    for gt in selected_types:
        doc.Delete(gt.Id)

    t.Commit()
    forms.alert("Selected groups deleted successfully.")

except Exception as e:
    t.RollBack()
    forms.alert("Error occurred:\n{}".format(e))