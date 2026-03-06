# -*- coding: utf-8 -*-
from pyrevit import forms, script
import os

def require_password(func):
    def wrapper(*args, **kwargs):
        # اقرأ الباسورد من ملف config/password.txt
        pwd_file = os.path.join(os.path.dirname(__file__), "..", "config", "password.txt")
        with open(pwd_file, "r") as f:
            pwd = f.read().strip()

        user_input = forms.ask_for_string(
            message="Enter password to use this command",
            default=""
        )

        if user_input != pwd:
            forms.alert("Wrong password! Access denied.")
            script.exit()
        return func(*args, **kwargs)
    return wrapper