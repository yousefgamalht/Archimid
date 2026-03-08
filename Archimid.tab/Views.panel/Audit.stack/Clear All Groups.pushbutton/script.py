# -*- coding: utf-8 -*-
__title__ = "Clear Groups"
__doc__ = """
Explode Selected Model/Detail Groups 
and Delete them from Project Browser.
Author: Yousef Gamal
"""

from pyrevit import forms, revit
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    BuiltInParameter,
    Transaction
)

doc = revit.doc


# ----------------------------
# Collect Model Group Types
# ----------------------------
model_groups = list(
    FilteredElementCollector(doc)
    .OfCategory(BuiltInCategory.OST_IOSModelGroups)
    .WhereElementIsElementType()
)

# ----------------------------
# Collect Detail Group Types
# ----------------------------
detail_groups = list(
    FilteredElementCollector(doc)
    .OfCategory(BuiltInCategory.OST_IOSDetailGroups)
    .WhereElementIsElementType()
)

if not model_groups and not detail_groups:
    forms.alert("No groups found in project.", exitscript=True)


# ----------------------------
# Prepare Display List
# ----------------------------
display_list = []
group_map = {}


def get_group_name(group_type):
    try:
        param = group_type.get_Parameter(
            BuiltInParameter.SYMBOL_NAME_PARAM
        )
        if param:
            return param.AsString()
    except:
        pass
    return "Unnamed Group"


for gt in model_groups:
    name = get_group_name(gt)
    display = "Model | {}".format(name)
    display_list.append(display)
    group_map[display] = gt

for gt in detail_groups:
    name = get_group_name(gt)
    display = "Detail | {}".format(name)
    display_list.append(display)
    group_map[display] = gt


# ----------------------------
# Show Selection Form
# ----------------------------
selected = forms.SelectFromList.show(
    sorted(display_list),
    multiselect=True,
    title="Select Groups to Delete",
    width=500
)

if not selected:
    forms.alert("No groups selected.", exitscript=True)


# ----------------------------
# Transaction
# ----------------------------
t = Transaction(doc, "Explode and Delete Groups")
t.Start()

try:
    for item in selected:

        group_type = group_map[item]

        # Get all instances of this group type
        instances = list(group_type.Groups)

        # Ungroup all instances
        for inst in instances:
            try:
                inst.UngroupMembers()
            except:
                pass

        # Delete Group Type
        try:
            doc.Delete(group_type.Id)
        except:
            pass

    t.Commit()
    forms.alert("Selected groups deleted successfully.")

except Exception as e:
    t.RollBack()
    forms.alert("Error:\n{}".format(str(e)))