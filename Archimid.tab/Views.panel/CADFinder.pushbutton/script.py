# -*- coding: utf-8 -*-

#Button Data
__title__ = "CAD Finder"
__doc__ = """
Select CAD Files (Linked/Imported) and highlight.
Author: Yousef Gamal
"""

# Imports

# Autodesk Imports
from Autodesk.Revit.DB import *

# PyRevit Imports
from pyrevit import revit, forms, script

# .NET Imports
import clr
clr.AddReference("System")

from System.Collections.Generic import List
from System.Windows import Window
from System.Windows.Controls import ListBox

# Variables
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application


# -------------------------------
# Modeless Window
# -------------------------------

class CadFinder(Window):

    def __init__(self, cad_dict):
        self.cad_dict = cad_dict

        self.Title = "CAD Finder"
        self.Width = 400
        self.Height = 500
        self.Topmost = True

        self.listbox = ListBox()
        self.listbox.ItemsSource = sorted(cad_dict.keys())

        self.Content = self.listbox

        self.listbox.SelectionChanged += self.select_cad


    def select_cad(self, sender, args):

        selected = self.listbox.SelectedItem

        if not selected:
            return

        cad = self.cad_dict[selected]

        try:

            if cad.ViewSpecific:
                view = doc.GetElement(cad.OwnerViewId)
                uidoc.ActiveView = view

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

            name_param = cad_ID.get_Parameter(
                BuiltInParameter.SYMBOL_NAME_PARAM
            )

            name = name_param.AsString()

            cad_type = "CAD Link" if cad.IsLinked else "CAD Import"
            view_specific = "View Specific" if cad.ViewSpecific else "Model"

            display_name = "{} | {} | {} | ID: {}".format(
                name,
                cad_type,
                view_specific,
                cad.Id
            )

            cad_dict[display_name] = cad

        except:
            continue


    if not cad_dict:
        forms.alert("No CAD files found in this project", exitscript=True)


    # Launch Window
    CadFinder(cad_dict).Show()


except Exception as e:
    forms.alert("Script Error: {}".format(e))