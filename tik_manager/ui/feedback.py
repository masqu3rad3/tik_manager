"""Feedback functions for QT"""

from tik_manager.core.environment import get_environment_data

ENV_DATA = get_environment_data()

# import Qt module depending on the DCC
# The reason not to use directly is that pyinstaller is not working well with Qt.py
if ENV_DATA["dcc"] == "standalone" or ENV_DATA["dcc"] == "photoshop":
    from PyQt5 import QtWidgets
else:
    from tik_manager.ui.Qt import QtWidgets


class Feedback(object):
    def __init__(self, *args, **kwargs):
        self.parent=None

    def pop_info(self, title="Info", text="", details="", critical=False):
        msg = QtWidgets.QMessageBox(parent=self.parent)
        if critical:
            msg.setIcon(QtWidgets.QMessageBox.Critical)
        else:
            msg.setIcon(QtWidgets.QMessageBox.Information)

        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setInformativeText(details)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.button(QtWidgets.QMessageBox.Ok).setFixedHeight(30)
        msg.button(QtWidgets.QMessageBox.Ok).setFixedWidth(100)
        return msg.exec_()

    def pop_question(self, title="Question", text="", details="", buttons=("save", "no", "cancel")):
        button_dict = {
            "yes": "QtWidgets.QMessageBox.Yes",
            "save": "QtWidgets.QMessageBox.Save",
            "ok": "QtWidgets.QMessageBox.Ok",
            "no": "QtWidgets.QMessageBox.No",
            "cancel": "QtWidgets.QMessageBox.Cancel"
        }
        widgets = []
        for button in buttons:
            widget = button_dict.get(button)
            if not widget:
                raise Exception("Non-valid button defined. Valid buttons are: %s" %button_dict.keys())
            widgets.append(widget)

        q = QtWidgets.QMessageBox(parent=self.parent)
        q.setIcon(QtWidgets.QMessageBox.Question)
        q.setWindowTitle(title)
        q.setText(text)
        q.setInformativeText(details)
        eval('q.setStandardButtons(%s)' %(" | ".join(widgets)))
        ret = q.exec_()
        for key, value in button_dict.items():
            if ret == eval(value):
                return key
