# -*- coding: utf-8 -*-
__title__ = "Select Elements in a Room"
__doc__ = """
Select all elements inside a chosen Room/Space
Author: Yousef Gamal
"""

from pyrevit import revit, forms
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    SpatialElement,
    SpatialElementBoundaryOptions,
    XYZ,
    ElementId,
    BuiltInParameter
)
from System.Collections.Generic import List

doc = revit.doc
uidoc = revit.uidoc

# ----------------------------
# Helper Functions
# ----------------------------

def get_spatialelements():
    collector = FilteredElementCollector(doc).OfClass(SpatialElement)
    return [e for e in collector if e.LevelId is not None]

def get_param_value(element, builtin_param):
    param = element.get_Parameter(builtin_param)
    return param.AsString() if param else ""

def get_spatial_name_number(se):
    if se.GetType().Name == "Room":
        name = get_param_value(se, BuiltInParameter.ROOM_NAME)
        number = get_param_value(se, BuiltInParameter.ROOM_NUMBER)
    else:
        name = get_param_value(se, BuiltInParameter.SPACE_NAME)
        number = get_param_value(se, BuiltInParameter.SPACE_NUMBER)
    return "{} | {}".format(name or "Room/Space", number or "")

def point_in_spatial(point, spatial):
    opt = SpatialElementBoundaryOptions()
    boundaries = spatial.GetBoundarySegments(opt)
    if boundaries is None:
        return False
    for loop in boundaries:
        poly = [seg.GetCurve().GetEndPoint(0) for seg in loop]
        crossings = 0
        x, y = point.X, point.Y
        n = len(poly)
        for i in range(n):
            p1 = poly[i]
            p2 = poly[(i + 1) % n]
            if ((p1.Y > y) != (p2.Y > y)) and (x < (p2.X - p1.X) * (y - p1.Y) / (p2.Y - p1.Y + 1e-9) + p1.X):
                crossings += 1
        if crossings % 2 == 1:
            return True
    return False

def select_elements_in_spatial(spatial):
    collector = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements()
    selected_ids = []
    for e in collector:
        if isinstance(e, SpatialElement):
            continue
        bbox = e.get_BoundingBox(None)
        if bbox:
            center = (bbox.Min + bbox.Max) * 0.5
            if point_in_spatial(center, spatial):
                selected_ids.append(e.Id)
    if selected_ids:
        uidoc.Selection.SetElementIds(List[ElementId](selected_ids))
    forms.alert("{} elements selected in '{}'.".format(len(selected_ids), get_spatial_name_number(spatial)))

# ----------------------------
# Main
# ----------------------------

spatials = get_spatialelements()
if not spatials:
    forms.alert("No Rooms or Spaces found in this project.", exitscript=True)

# --- Prepare list of display strings only (Name | Number) ---
spatial_names = [get_spatial_name_number(se) for se in spatials]

# --- Show dropdown ---
choice = forms.SelectFromList.show(
    spatial_names,
    title="Select a Room/Space",
    button_name="Select",
    multiselect=False
)

if choice:
    # choice هو string (Name | Number)، نبحث عن العنصر في قائمة spatials
    selected_spatial = next(se for se in spatials if get_spatial_name_number(se) == choice)
    select_elements_in_spatial(selected_spatial)