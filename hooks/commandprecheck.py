from pyrevit import forms, script

def require_password(func):
    def wrapper(*aargs, **kwargs):
        pwd = "1234"  # أو اقرأ من ملف

        user_input = forms.ask_for_string(
            message="Enter password to use this command",
            default=""
        )

        if user_input != pwd:
            forms.alert("Wrong password! Access denied.")
            script.exit()  # يوقف تنفيذ السكريبت
        return func(*args, **kwargs)
    return wrapper