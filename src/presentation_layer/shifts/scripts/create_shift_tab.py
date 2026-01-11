import os
import datetime
from PyQt5 import QtWidgets, uic, QtCore


class CreateShiftTab(QtWidgets.QDialog):
    def __init__(self, parent=None, employees_manager=None, selected_date=None, shift=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'create_shift_tab.ui')
        uic.loadUi(ui_path, self)

        self.employees_manager = employees_manager
        self.selected_date = selected_date

        self.buttonBox.accepted.disconnect(self.accept)
        self.buttonBox.accepted.connect(self.validate)
        self.buttonBox.rejected.connect(self.reject)

        self.populate_employees()

        if shift:
            self.setWindowTitle("Edit Shift")
            self.set_data(shift)
        else:
            self.setWindowTitle("Add Shift")

    def populate_employees(self):
        self.employees_manager.load_employees()
        for emp in self.employees_manager.employees:
            self.combo_employee.addItem(f"{emp.first_name} {emp.last_name}", emp.id)

    def set_data(self, shift):
        index = self.combo_employee.findData(shift.employee_id)
        if index >= 0:
            self.combo_employee.setCurrentIndex(index)

        start_qtime = QtCore.QTime(shift.start_time.hour, shift.start_time.minute)
        end_qtime = QtCore.QTime(shift.end_time.hour, shift.end_time.minute)

        self.time_start.setTime(start_qtime)
        self.time_end.setTime(end_qtime)
        self.spin_rate.setValue(shift.hourly_rate)

    def validate(self):
        if self.combo_employee.currentIndex() == -1:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select an employee")
            return

        if self.spin_rate.value() <= 0:
            QtWidgets.QMessageBox.warning(self, "Error", "Hourly rate must be greater than 0")
            return

        start = self.time_start.time()
        end = self.time_end.time()

        if start >= end:
             QtWidgets.QMessageBox.warning(self, "Error", "End time cannot be earlier than or equal to start time.")
             return

        self.accept()

    def get_data(self):
        start_time = self.time_start.time()
        end_time = self.time_end.time()

        start_dt = datetime.datetime.combine(self.selected_date, datetime.time(start_time.hour(), start_time.minute()))
        end_dt = datetime.datetime.combine(self.selected_date, datetime.time(end_time.hour(), end_time.minute()))

        return {
            "employee_id": self.combo_employee.currentData(),
            "start_time": start_dt,
            "end_time": end_dt,
            "hourly_rate": self.spin_rate.value()
        }