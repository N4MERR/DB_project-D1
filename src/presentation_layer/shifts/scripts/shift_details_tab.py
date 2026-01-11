import os
import threading
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt
from src.objects.shift import Shift
from src.presentation_layer.MyLib.action_delegate import ActionDelegate
from src.presentation_layer.shifts.scripts.create_shift_tab import CreateShiftTab


class ShiftDetailsTab(QtWidgets.QWidget):
    load_finished_signal = QtCore.pyqtSignal(bool, str)

    def __init__(self, shifts_manager, employees_manager, ui_manager, calendar_tab):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'shift_details_tab.ui')
        uic.loadUi(ui_path, self)

        self.shifts_manager = shifts_manager
        self.employees_manager = employees_manager
        self.ui_manager = ui_manager
        self.calendar_tab = calendar_tab
        self.current_date = None

        self.table_shifts.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_shifts.verticalHeader().setVisible(False)

        self.action_delegate = ActionDelegate(self.table_shifts)
        self.action_delegate.edit_clicked.connect(self.edit_shift)
        self.action_delegate.delete_clicked.connect(self.delete_shift)
        self.table_shifts.setItemDelegateForColumn(4, self.action_delegate)

        self.btn_back_to_calendar.clicked.connect(self.go_back)
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.btn_add_shift.clicked.connect(self.add_shift_dialog)
        self.load_finished_signal.connect(self.on_load_finished)

    def go_back(self):
        self.ui_manager.switch_to_tab(self.calendar_tab)

    def load_date(self, date):
        self.current_date = date
        self.lbl_shift_date_header.setText(f"Shifts for {date}")
        self.refresh_data()

    def refresh_data(self):
        if not self.current_date:
            return

        self.ui_manager.lock_ui()
        threading.Thread(target=self._run_load).start()

    def _run_load(self):
        try:
            self.shifts_manager.get_shifts_for_date(self.current_date)
            self.load_finished_signal.emit(True, "")
        except Exception as e:
            self.load_finished_signal.emit(False, str(e))

    def on_load_finished(self, success, error):
        self.ui_manager.unlock_ui()
        if not success:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load shifts: {error}")
            return
        self.populate_table()

    def populate_table(self):
        self.table_shifts.setRowCount(0)
        self.table_shifts.setSortingEnabled(False)

        for shift in self.shifts_manager.shifts:
            row = self.table_shifts.rowCount()
            self.table_shifts.insertRow(row)

            start_str = shift.start_time.strftime("%H:%M")
            end_str = shift.end_time.strftime("%H:%M")

            start_item = QtWidgets.QTableWidgetItem(start_str)
            start_item.setTextAlignment(Qt.AlignCenter)
            self.table_shifts.setItem(row, 0, start_item)

            end_item = QtWidgets.QTableWidgetItem(end_str)
            end_item.setTextAlignment(Qt.AlignCenter)
            self.table_shifts.setItem(row, 1, end_item)

            name = f"{shift.employee_first_name} {shift.employee_last_name}"
            emp_item = QtWidgets.QTableWidgetItem(name)
            emp_item.setTextAlignment(Qt.AlignCenter)
            self.table_shifts.setItem(row, 2, emp_item)

            rate_item = QtWidgets.QTableWidgetItem(f"{shift.hourly_rate:.2f}")
            rate_item.setTextAlignment(Qt.AlignCenter)
            self.table_shifts.setItem(row, 3, rate_item)

            action_item = QtWidgets.QTableWidgetItem()
            action_item.setData(Qt.UserRole, shift)
            self.table_shifts.setItem(row, 4, action_item)

        self.table_shifts.setSortingEnabled(True)

    def add_shift_dialog(self):
        dialog = CreateShiftTab(self, self.employees_manager, selected_date=self.current_date)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            try:
                new_shift = Shift(data['employee_id'], data['start_time'], data['end_time'], data['hourly_rate'])
                self.shifts_manager.add_shift(new_shift)
                self.refresh_data()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to add shift: {e}")

    def edit_shift(self, shift):
        dialog = CreateShiftTab(self, self.employees_manager, selected_date=self.current_date, shift=shift)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            try:
                shift.employee_id = data['employee_id']
                shift.start_time = data['start_time']
                shift.end_time = data['end_time']
                shift.hourly_rate = data['hourly_rate']
                self.shifts_manager.edit_shift(shift)
                self.refresh_data()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to edit shift: {e}")

    def delete_shift(self, shift):
        confirm = QtWidgets.QMessageBox.question(self, "Confirm", "Delete this shift?",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm == QtWidgets.QMessageBox.Yes:
            try:
                self.shifts_manager.delete_shift(shift.id)
                self.refresh_data()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete shift: {e}")