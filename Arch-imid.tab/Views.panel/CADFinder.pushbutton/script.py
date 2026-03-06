# -*- coding: utf-8 -*-

#Button Data
__title__ = "CAD Finder"
__doc__ = """
Select CAD Files (Linked/Imported) and highlight /r delete it.
Author: Yousef Gamal
"""

#Imports

#Autodesk Imports
from Autodesk.Revit.DB import*

#Pyrevit Imports
from pyrevit import revit, forms
from pyrevit import script

##.NET Imports
import clr
clr.AddReference("System")

from System.Collections.Generic import List

#Variables

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

#Functions



#Main
try :    
    collector = FilteredElementCollector(doc).OfClass(ImportInstance).WhereElementIsNotElementType()
    cad_dict = {}

    for cad in collector:
        try:
            cad_ID = doc.GetElement(cad.GetTypeId())
            name_param = cad_ID.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
            name = name_param.AsString()
            cad_type = "CAD Link" if cad.IsLinked else "CAD Import"
            view_specific = "View Specific" if cad.ViewSpecific else "Model"

            display_name = "{} | {} | ID: {}".format(name, cad_type, cad.Id)
            
            cad_dict[display_name] = cad
        except:
            continue

    if not cad_dict:
        forms.alert("No CAD files found in this project", exitscript=True)

    selected = forms.SelectFromList.show(
        sorted(cad_dict.keys()),
        title = "Select CAD",
        multiselect = False
    )    

    if not selected:
        script.exit()

    selected_cad = cad_dict[selected]

    try:
        if selected_cad.ViewSpecific:
            view = doc.GetElement(selected_cad.OwnerViewId)
            uidoc.ActiveView = view

        ids = List[ElementId]()
        ids.Add(selected_cad.Id)

        uidoc.Selection.SetElementIds(ids)

    except Exception as error:
        forms.alert("Operation failed: {}".format(error))

except Exception as e:
    forms.alert("Script Error: {}".format(e))   