# -*- coding: utf-8 -*-
__title__ = "Clear Unused Views & Empty Sheets (Safe)"
__doc__ = """
Delete unused Views (Plans, Sections, Drafting, 3D, Elevations) and empty Sheets,
excluding Project Browser, System Browser, Legends, and Templates.
Shows type and number of elements for each View.
Author: Yousef Gamal
"""

from pyrevit import forms, revit
from Autodesk.Revit.DB import FilteredElementCollector, View, ViewSheet, Transaction

doc = revit.doc

# ----------------------------
# Prepare mapping of Views placed on sheets
# ----------------------------
sheet_views = set()
for sheet in FilteredElementCollector(doc).OfClass(ViewSheet).WhereElementIsNotElementType():
    for v_id in sheet.GetAllPlacedViews():
        sheet_views.add(v_id.IntegerValue)

# ----------------------------
# Collect all usable views (exclude templates and system views)
# ----------------------------
all_views = FilteredElementCollector(doc).OfClass(View).WhereElementIsNotElementType()
unused_views = []

system_view_types = {
    # Views that should never be deleted
    "ProjectBrowser", 
    "SystemBrowser", 
    "Legend", 
    "Internal", 
    "Schedule"
}

for v in all_views:
    if v.IsTemplate:
        continue
    if str(v.ViewType) in system_view_types:
        continue
    if v.Id.IntegerValue in sheet_views:
        continue  # Skip views placed on sheets
    # Count elements in the view
    collector = FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType()
    element_count = collector.GetElementCount()
    unused_views.append((v, element_count))

# ----------------------------
# Collect empty sheets
# ----------------------------
all_sheets = FilteredElementCollector(doc).OfClass(ViewSheet).WhereElementIsNotElementType()
empty_sheets = []
for s in all_sheets:
    # Only real sheets
    if s.Name.startswith("Browser") or s.Name.startswith("System"):
        continue
    if not s.GetAllPlacedViews() or len(s.GetAllPlacedViews()) == 0:
        empty_sheets.append(s)

if not unused_views and not empty_sheets:
    forms.alert("No unused views or empty sheets found.", exitscript=True)

# ----------------------------
# Prepare display list
# ----------------------------
display_list = []
element_map = {}

for v, count in unused_views:
    display = "View | {} ({}) - {} elements".format(v.Name, v.ViewType, count)
    display_list.append(display)
    element_map[display] = v

for s in empty_sheets:
    display = "Sheet | {} - {}".format(s.SheetNumber, s.Name)
    display_list.append(display)
    element_map[display] = s

# ----------------------------
# Show selection form
# ----------------------------
selected = forms.SelectFromList.show(
    sorted(display_list),
    multiselect=True,
    title="Select Views/Sheets to Delete",
    width=700
)

if not selected:
    forms.alert("No items selected.", exitscript=True)

# ----------------------------
# Transaction to delete
# ----------------------------
t = Transaction(doc, "Delete Unused Views & Empty Sheets")
t.Start()
try:
    for item in selected:
        elem = element_map[item]
        try:
            doc.Delete(elem.Id)
        except:
            pass
    t.Commit()
    forms.alert("Selected views/sheets deleted successfully.")
except Exception as e:
    t.RollBack()
    forms.alert("Error:\n{}".format(str(e)))