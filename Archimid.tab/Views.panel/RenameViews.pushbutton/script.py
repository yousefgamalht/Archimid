# -*- coding: utf-8 -*-

#Button Data
__title__ = "Rename Views"
__doc__ = """
Rename Views in Revit by using Find/Replace Logic
Author: Yousef Gamal
"""

#Imports

#Autodesk Imports
from Autodesk.Revit.DB import*

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
#Select Views
sel_el_ids = uidoc.Selection.GetElementIds()

sel_elem = [doc.GetElement(e_id) for e_id in sel_el_ids]

sel_views = [el for el in sel_elem if issubclass(type(el), View)]

if not sel_views:
    sel_views = forms.select_views()

if not sel_views:
    forms.alert('No Views Selected! Please try again', exitscript=True)

#Define Renaming Rules
from rpw.ui.forms import (FlexForm, Label, TextBox, Separator, Button)
componenets = [Label('Prefix:'), TextBox('prefix'),
               Label('Find:'), TextBox('find'),
               Label('Replace:'), TextBox('replace'),
               Label('Suffix'), TextBox('suffix'),
               Separator(), Button('Rename Views')]

form = FlexForm('Title', componenets)
form.show()

user_inputs = form.values
Prefix = user_inputs['prefix']
Find = user_inputs['find']
Replace = user_inputs['replace']
Suffix = user_inputs['suffix']

t = Transaction(doc, 'YG-Rename Views')

t.Start()
for view in sel_views:
    #cCreate new View Name
    old_name = view.Name
    new_name = Prefix + old_name.replace(Find, Replace) + Suffix

    # Rename Views
    for i in range(20):
        try:
            view.Name = new_name
            print('{} -> {}'.format(old_name, new_name))
            break
        except:
            new_name += '*'
t.Commit()