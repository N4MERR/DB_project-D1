import os
import threading

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt

from src.aplication_layer.employees_manager import EmployeesManager
from src.objects.employee import Employee
from src.presentation_layer.employees.scripts.create_new_employee_tab import CreateEmployeeTab
from src.presentation_layer.MyLib.action_delegate import ActionDelegate


class EmployeesTab(QtWidgets.QWidget):
    delete_finished_signal = QtCore.pyqtSignal(bool, str)
    load_finished_signal = QtCore.pyqtSignal(bool, str)
    edit_finished_signal = QtCore.pyqtSignal(bool, str)

    def __init__(self, employees_manager: EmployeesManager, ui_manager):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'employees_tab.ui')
        uic.loadUi(ui_path, self)

        self._employees_manager = employees_manager
        self._ui_manager = ui_manager

        self.table_employees.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_employees.verticalHeader().setVisible(False)

        self.action_delegate = ActionDelegate(self.table_employees)
        self.action_delegate.edit_clicked.connect(self.edit_employee)
        self.action_delegate.delete_clicked.connect(self.delete_employee)
        self.table_employees.setItemDelegateForColumn(2, self.action_delegate)

        self.btn_add_employee.clicked.connect(self.add_employee)
        self.btn_refresh.clicked.connect(self.load_employees)

        self.load_finished_signal.connect(self.on_load_finished)
        self.delete_finished_signal.connect(self.on_delete_finished)
        self.edit_finished_signal.connect(self.on_edit_finished)

        self.load_employees()

    def load_employees(self):
        """
        Loads employees.
        :return:
        """
        self._ui_manager.lock_ui()

        def run_load():
            try:
                self._employees_manager.load_employees()
                self.load_finished_signal.emit(True, "")
            except Exception as e:
                self.load_finished_signal.emit(False, str(e))

        threading.Thread(target=run_load).start()

    def edit_employee(self, employee):
        """
        Freezes the UI to edit the employee.
        :param employee:
        :return:
        """
        dialog = CreateEmployeeTab(self, employee)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            updated_employee = Employee(data["first_name"], data["last_name"])
            updated_employee.id = employee.id

            self._ui_manager.lock_ui()

            def run_edit():
                try:
                    self._employees_manager.edit_employee(updated_employee)
                    self._employees_manager.load_employees()
                    self.edit_finished_signal.emit(True, "")
                except Exception as e:
                    self.edit_finished_signal.emit(False, f"Edit failed: {str(e)}")

            threading.Thread(target=run_edit).start()

    def on_edit_finished(self, success, error_message):
        """
        Unfreezes the UI and shows user the result.
        :param success:
        :param error_message:
        :return:
        """
        if success:
            self.reload_employee_list()
            self._ui_manager.unlock_ui()
            QtWidgets.QMessageBox.information(self, "Success", "Employee updated.")
        else:
            self._ui_manager.unlock_ui()
            QtWidgets.QMessageBox.critical(self, "Error", f"Employee Update failed:\n{error_message}")

    def delete_employee(self, employee):
        """
        Opens a window asking for confirmation from user.
        If user confirms, freezes the UI and deletes the employee.
        :param employee:
        :return:
        """
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{employee.first_name} {employee.last_name}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if confirm == QtWidgets.QMessageBox.Yes:
            self._ui_manager.lock_ui()

            def run_delete():
                try:
                    self._employees_manager.delete_employee(employee.id)
                    self.delete_finished_signal.emit(True, "")
                except Exception as e:
                    self.delete_finished_signal.emit(False, str(e))

            threading.Thread(target=run_delete).start()

    def on_delete_finished(self, success, error_message):
        """
        Unfreezes the UI after delete finishes and shows the result.
        :param success:
        :param error_message:
        :return:
        """
        if success:
            self.reload_employee_list()
            self._ui_manager.unlock_ui()
            QtWidgets.QMessageBox.information(self, "Success", "Employee deleted.")
        else:
            self._ui_manager.unlock_ui()
            QtWidgets.QMessageBox.critical(self, "Error", f"Employee Delete failed:\n{error_message}")

    def on_load_finished(self, success, error_message):
        """
        Unfreezes the UI and shows the result of loading.
        :param success:
        :param error_message:
        :return:
        """
        if not success:
            self._ui_manager.unlock_ui()
            QtWidgets.QMessageBox.critical(self, "Error", f"Refresh failed:\n{error_message}")
            return

        self.reload_employee_list()
        self._ui_manager.unlock_ui()

    def reload_employee_list(self):
        """
        Loads the employee list into the table in the UI.
        :return:
        """
        self.table_employees.setRowCount(0)
        self.table_employees.setSortingEnabled(False)

        for employee in self._employees_manager.employees:
            row = self.table_employees.rowCount()
            self.table_employees.insertRow(row)

            id_item = QtWidgets.QTableWidgetItem(str(employee.id))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table_employees.setItem(row, 0, id_item)

            full_name = f"{employee.first_name} {employee.last_name}"
            name_item = QtWidgets.QTableWidgetItem(full_name)
            name_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table_employees.setItem(row, 1, name_item)

            action_item = QtWidgets.QTableWidgetItem()
            action_item.setData(Qt.UserRole, employee)
            self.table_employees.setItem(row, 2, action_item)

        self.table_employees.setSortingEnabled(True)

    def add_employee(self):
        """
        Adds a new employee.
        :return:
        """
        create_employee_tab = CreateEmployeeTab(self)
        if create_employee_tab.exec_() == QtWidgets.QDialog.Accepted:
            data = create_employee_tab.get_data()
            try:
                self._employees_manager.add_employee(
                    Employee(data["first_name"], data["last_name"]))
                self.load_employees()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to add employee: {str(e)}")