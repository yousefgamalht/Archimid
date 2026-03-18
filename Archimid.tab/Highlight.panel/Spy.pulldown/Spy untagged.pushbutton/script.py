# -*- coding: utf-8 -*-
__title__ = "Spy Untagged"
__doc__ = """
Highlight Elements that not tagged
Author: Yousef Gamal
"""

from pyrevit import revit, DB, forms, script
from System.Collections.Generic import List

doc = revit.doc
uidoc = revit.uidoc
view = doc.ActiveView

# -----------------------------
# Collect elements in view
# -----------------------------
elements = DB.FilteredElementCollector(doc, view.Id)\
    .WhereElementIsNotElementType()\
    .ToElements()

# -----------------------------
# Collect tags in view
# -----------------------------
tags = DB.FilteredElementCollector(doc, view.Id)\
    .OfClass(DB.IndependentTag)\
    .ToElements()

# -----------------------------
# Get tagged element IDs
# -----------------------------
tagged_ids = set()

for tag in tags:
    try:
        refs = tag.GetTaggedLocalElementIds()
        for ref in refs:
            tagged_ids.add(ref.IntegerValue)
    except:
        continue

# -----------------------------
# Filter untagged elements
# -----------------------------
untagged = []

for el in elements:
    try:
        if el.Id.IntegerValue not in tagged_ids:
            if el.Category and el.Category.HasMaterialQuantities:
                untagged.append(el)
    except:
        continue

# -----------------------------
# No results
# -----------------------------
if not untagged:
    forms.alert("✅ No untagged elements found")
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

options = [ItemOption(el) for el in untagged]

selected = forms.SelectFromList.show(
    options,
    title="🚨 Untagged Elements",
    multiselect=False
)

# -----------------------------
# Select + Zoom
# -----------------------------
if selected:
    # handle both cases (wrapped / direct)
    if hasattr(selected, "item"):
        element = selected.item
    else:
        element = selected

    ids = List[DB.ElementId]()
    ids.Add(element.Id)

    uidoc.Selection.SetElementIds(ids)
    uidoc.ShowElements(element)