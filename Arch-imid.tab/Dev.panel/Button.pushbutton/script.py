# -*- coding: utf-8 -*-

#Button Data
__title__ = "Button"
__doc__ = """Description"""

#Imports

#Autodesk Imports
from Autodesk.Revit.DB import*
from Autodesk.Revit.DB.Architecture import*


#Pyrevit Imports
from pyrevit import revit, forms

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
collector = FilteredElementCollector(doc).OfClass(SpatialElement)

for elem in collector:
    if isinstance(elem, Room):
        print(elem.Id.IntegerValue)