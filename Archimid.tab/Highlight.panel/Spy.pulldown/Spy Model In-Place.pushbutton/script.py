# -*- coding: utf-8 -*-
__title__ = "Spy Model In-Place"
__doc__ = """
Highlight Model In-Place in Current View
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
# Filter Model In-Place
# -----------------------------
inplace_elements = []

for el in elements:
    try:
        if isinstance(el, DB.FamilyInstance):
            if el.Symbol and el.Symbol.Family and el.Symbol.Family.IsInPlace:
                inplace_elements.append(el)
    except:
        continue

# -----------------------------
# No results
# -----------------------------
if not inplace_elements:
    forms.alert("✅ No Model In-Place found")
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

options = [ItemOption(el) for el in inplace_elements]

selected = forms.SelectFromList.show(
    options,
    title="🚨 Model In-Place Elements",
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