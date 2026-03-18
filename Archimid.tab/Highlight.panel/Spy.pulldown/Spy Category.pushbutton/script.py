# -*- coding: utf-8 -*-
__title__ = "Spy Category"
__doc__ = """
Highlight Elements By Category in current View
Author: Yousef Gamal
"""

from pyrevit import revit, DB, forms, script
from System.Collections.Generic import List

doc = revit.doc
uidoc = revit.uidoc
view = doc.ActiveView

# -----------------------------
# Get all categories in view
# -----------------------------
categories = []

for cat in doc.Settings.Categories:
    try:
        if cat.CategoryType == DB.CategoryType.Model and cat.AllowsBoundParameters:
            categories.append(cat)
    except:
        continue

# Sort categories by name
categories = sorted(categories, key=lambda x: x.Name)

# -----------------------------
# UI Category Selection
# -----------------------------
class CategoryOption(forms.TemplateListItem):
    @property
    def name(self):
        return self.item.Name

cat_options = [CategoryOption(c) for c in categories]

selected_cat = forms.SelectFromList.show(
    cat_options,
    title="Select Category",
    multiselect=False
)

if not selected_cat:
    script.exit()

# unwrap category
if hasattr(selected_cat, "item"):
    category = selected_cat.item
else:
    category = selected_cat

# -----------------------------
# Collect elements of category in view
# -----------------------------
elements = DB.FilteredElementCollector(doc, view.Id)\
    .OfCategoryId(category.Id)\
    .WhereElementIsNotElementType()\
    .ToElements()

if not elements:
    forms.alert("❌ No elements found in this category")
    script.exit()

# -----------------------------
# UI Elements List
# -----------------------------
class ElementOption(forms.TemplateListItem):
    @property
    def name(self):
        try:
            return "{} | ID: {}".format(
                self.item.Name,
                self.item.Id.IntegerValue
            )
        except:
            return "Element ID: {}".format(self.item.Id.IntegerValue)

options = [ElementOption(el) for el in elements]

selected = forms.SelectFromList.show(
    options,
    title="Elements in {}".format(category.Name),
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