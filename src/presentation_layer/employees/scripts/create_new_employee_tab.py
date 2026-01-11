from PyQt5 import QtWidgets, uic
import os


class CreateEmployeeTab(QtWidgets.QDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'create_new_employee_tab.ui')
        uic.loadUi(ui_path, self)

        self.buttonBox.accepted.disconnect(self.accept)

        if employee:
            self.setWindowTitle("Edit Employee")
            self.lineEdit_first_name.setText(employee.first_name)
            self.lineEdit_last_name.setText(employee.last_name)
        else:
            self.setWindowTitle("Add New Employee")

        self.buttonBox.accepted.connect(self.validate_inputs)
        self.buttonBox.rejected.connect(self.reject)

    def validate_inputs(self):
        """
        Validates inputs.
        :return:
        """
        first_name = self.lineEdit_first_name.text().strip()
        last_name = self.lineEdit_last_name.text().strip()

        if not first_name:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "First name is required.")
            return

        if not last_name:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Last name is required.")
            return

        self.accept()

    def get_data(self):
        """
        Gets data from the create employee window.
        :return:
        """
        return {
            "first_name": self.lineEdit_first_name.text().strip(),
            "last_name": self.lineEdit_last_name.text().strip()
        }