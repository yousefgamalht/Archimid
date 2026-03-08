# -*- coding: utf-8 -*-

# Button Data
__title__ = "CAD Finder"
__doc__ = """
Select CAD Files (Linked/Imported) and highlight.
Author: Yousef Gamal
"""

# Imports
from Autodesk.Revit.DB import *
from pyrevit import revit, forms
import clr
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows import Window, Thickness
from System.Windows.Controls import ListBox, Button, StackPanel

# Variables
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# -------------------------------
# Modeless Window
# -------------------------------

class CadFinder(Window):

    def __init__(self, cad_dict):
        self.cad_dict = cad_dict

        self.Title = "CAD Finder"
        self.Width = 400
        self.Height = 550
        self.Topmost = True

        # Layout
        panel = StackPanel()
        panel.Margin = Thickness(10)

        # ListBox
        self.listbox = ListBox()
        self.listbox.ItemsSource = sorted(cad_dict.keys())
        self.listbox.Height = 450
        panel.Children.Add(self.listbox)

        # Select Button
        self.select_btn = Button()
        self.select_btn.Content = "Select CAD"
        self.select_btn.Margin = Thickness(0, 10, 0, 0)
        self.select_btn.Click += self.select_cad
        panel.Children.Add(self.select_btn)

        self.Content = panel

    def select_cad(self, sender, args):
        selected = self.listbox.SelectedItem
        if not selected:
            forms.alert("Please select a CAD file first.")
            return

        cad = self.cad_dict[selected]

        try:
            # Switch view if CAD is view-specific
            if cad.ViewSpecific and cad.OwnerViewId != ElementId.InvalidElementId:
                view = doc.GetElement(cad.OwnerViewId)
                if view:
                    uidoc.ActiveView = view

            # Select the CAD instance
            ids = List[ElementId]()
            ids.Add(cad.Id)
            uidoc.Selection.SetElementIds(ids)

        except Exception as error:
            forms.alert("Operation failed: {}".format(error))


# -------------------------------
# Main
# -------------------------------

try:
    collector = FilteredElementCollector(doc)\
        .OfClass(ImportInstance)\
        .WhereElementIsNotElementType()

    cad_dict = {}

    for cad in collector:
        try:
            cad_ID = doc.GetElement(cad.GetTypeId())
            name_param = cad_ID.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
            name = name_param.AsString()
            cad_type = "CAD Link" if cad.IsLinked else "CAD Import"
            view_specific = "View Specific" if cad.ViewSpecific else "Model"

            display_name = "{} | {} | {} | ID: {}".format(
                name, cad_type, view_specific, cad.Id
            )

            cad_dict[display_name] = cad
        except:
            continue

    if not cad_dict:
        forms.alert("No CAD files found in this project", exitscript=True)

    # ---- Launch Modeless Window ----
    win = CadFinder(cad_dict)
    win.Show()  # Modeless, works in Revit

except Exception as e:
    forms.alert("Script Error: {}".format(e))