# -*- coding: utf-8 -*-
__title__ = "Spy Groups"
__doc__ = """
Highlight Groups in the Current View
Author: Yousef Gamal
"""

from pyrevit import revit, DB, forms, script
from System.Collections.Generic import List

doc = revit.doc
uidoc = revit.uidoc
view = doc.ActiveView

# -----------------------------
# Collect Groups in view
# -----------------------------
model_groups = DB.FilteredElementCollector(doc, view.Id)\
    .OfCategory(DB.BuiltInCategory.OST_IOSModelGroups)\
    .WhereElementIsNotElementType()\
    .ToElements()

detail_groups = DB.FilteredElementCollector(doc, view.Id)\
    .OfCategory(DB.BuiltInCategory.OST_IOSDetailGroups)\
    .WhereElementIsNotElementType()\
    .ToElements()

groups = list(model_groups) + list(detail_groups)

# -----------------------------
# No results
# -----------------------------
if not groups:
    forms.alert("✅ No Groups found")
    script.exit()

# -----------------------------
# UI List
# -----------------------------
class ItemOption(forms.TemplateListItem):
    @property
    def name(self):
        try:
            return "{} | {} | ID: {}".format(
                self.item.Category.Name,
                self.item.Name,
                self.item.Id.IntegerValue
            )
        except:
            return "Element ID: {}".format(self.item.Id.IntegerValue)

options = [ItemOption(el) for el in groups]

selected = forms.SelectFromList.show(
    options,
    title="🚨 Groups in View",
    multiselect=False
)

# -----------------------------
# Select + Zoom
# -----------------------------
if selected:
    if hasattr(selected, "item"):
        element = selected.item
    else:
        element = selected

    ids = List[DB.ElementId]()
    ids.Add(element.Id)

    uidoc.Selection.SetElementIds(ids)
    uidoc.ShowElements(element)