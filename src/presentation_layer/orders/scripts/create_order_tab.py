import os
import threading
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt
from src.objects.order import Order
from src.objects.order_item import OrderItem
from src.presentation_layer.orders.scripts.create_order_item_tab import CreateOrderItemTab
from src.presentation_layer.MyLib.action_delegate import ActionDelegate


class CreateOrderTab(QtWidgets.QWidget):
    save_finished_signal = QtCore.pyqtSignal(bool, str)

    def __init__(self, orders_manager, employees_manager, menu_items_manager, ui_manager, orders_tab):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'create_order_tab.ui')
        uic.loadUi(ui_path, self)

        self.orders_manager = orders_manager
        self.employees_manager = employees_manager
        self.menu_items_manager = menu_items_manager
        self.ui_manager = ui_manager
        self.orders_tab = orders_tab

        self.current_items = []
        self.editing_order = None

        self.table_items.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.action_delegate = ActionDelegate(self.table_items)
        self.action_delegate.edit_clicked.connect(self.edit_order_item)
        self.action_delegate.delete_clicked.connect(self.delete_order_item)
        self.table_items.setItemDelegateForColumn(4, self.action_delegate)

        self.btn_cancel.clicked.connect(self.cancel_creation)
        self.btn_save_order.clicked.connect(self.save_order)
        self.btn_add_item.clicked.connect(self.add_item_dialog)

        self.save_finished_signal.connect(self.on_save_finished)

        self.btn_remove_item.setVisible(False)

    def open_empty_tab(self):
        """
        Opens an empty order creation tab.
        :return:
        """
        self.editing_order = None
        self.btn_save_order.setText("Create Order")
        self.input_order_name.clear()
        self.current_items.clear()
        self.populate_employees()
        self.refresh_order_items_table()

    def load_old_order(self, order):
        """
        Loads the old order data into the order creation tab.
        :param order:
        :return:
        """
        self.editing_order = order
        self.btn_save_order.setText("Update Order")
        self.populate_employees()

        self.input_order_name.setText(order.name)

        index = self.combo_employee.findData(order.employee_id)
        if index >= 0:
            self.combo_employee.setCurrentIndex(index)

        self.current_items = list(order.order_items)
        self.refresh_order_items_table()

    def populate_employees(self):
        """
        Loads the available employee choices for the user.
        :return:
        """
        self.combo_employee.clear()
        self.employees_manager.load_employees()
        for emp in self.employees_manager.employees:
            self.combo_employee.addItem(f"{emp.first_name} {emp.last_name}", emp.id)

    def add_item_dialog(self):
        """
        Opens the order item creation window.
        :return:
        """
        dialog = CreateOrderItemTab(self, self.menu_items_manager)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            new_item = OrderItem(data['menu_item'], data['quantity'])
            new_item.total_price = new_item.menu_item.price * new_item.quantity
            self.current_items.append(new_item)
            self.refresh_order_items_table()

    def edit_order_item(self, item):
        """
        Opens the order item edit window.
        :param item:
        :return:
        """
        dialog = CreateOrderItemTab(self, self.menu_items_manager, order_item=item)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            item.menu_item = data['menu_item']
            item.quantity = data['quantity']
            item.total_price = item.menu_item.price * item.quantity
            self.refresh_order_items_table()

    def delete_order_item(self, item):
        """
        Removes the order_item from the order_item list.
        :param item:
        :return:
        """
        if item in self.current_items:
            self.current_items.remove(item)
            self.refresh_order_items_table()

    def refresh_order_items_table(self):
        """
        Clears the table and reloads the order_items
        :return:
        """
        self.table_items.setRowCount(0)
        total_price = 0.0

        for item in self.current_items:
            row = self.table_items.rowCount()
            self.table_items.insertRow(row)

            name_item = QtWidgets.QTableWidgetItem(item.menu_item.name)
            name_item.setTextAlignment(Qt.AlignCenter)
            self.table_items.setItem(row, 0, name_item)

            qty_item = QtWidgets.QTableWidgetItem(str(item.quantity))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.table_items.setItem(row, 1, qty_item)

            price_item = QtWidgets.QTableWidgetItem(f"{item.menu_item.price:.2f}")
            price_item.setTextAlignment(Qt.AlignCenter)
            self.table_items.setItem(row, 2, price_item)

            subtotal = item.quantity * item.menu_item.price
            sub_item = QtWidgets.QTableWidgetItem(f"{subtotal:.2f}")
            sub_item.setTextAlignment(Qt.AlignCenter)
            self.table_items.setItem(row, 3, sub_item)

            action_item = QtWidgets.QTableWidgetItem()
            action_item.setData(Qt.UserRole, item)
            self.table_items.setItem(row, 4, action_item)

            total_price += subtotal

        self.lbl_total_price.setText(f"Total: {total_price:.2f}")

    def save_order(self):
        """
        Saves the new changes for the order.
        :return:
        """
        name = self.input_order_name.text().strip()
        employee_id = self.combo_employee.currentData()

        if not name:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Please enter an order name.")
            return
        if employee_id is None:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Please select an employee.")
            return

        try:
            if self.editing_order:
                self.editing_order.name = name
                self.editing_order.employee_id = employee_id
                self.editing_order.order_items = self.current_items

                order_to_save = self.editing_order
                is_update = True
            else:
                new_order = Order(employee_id, name, False)
                for item in self.current_items:
                    new_order.add_order_item(item)

                order_to_save = new_order
                is_update = False
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to prepare data: {e}")
            return

        self.ui_manager.lock_ui()

        def run_save():
            """
            Saves a new order or updates an existing order.
            :return:
            """
            try:
                if is_update:
                    self.orders_manager.update_order(order_to_save)
                else:
                    self.orders_manager.add_order(order_to_save)

                self.save_finished_signal.emit(True, "")
            except Exception as e:
                self.save_finished_signal.emit(False, str(e))

        threading.Thread(target=run_save).start()

    def on_save_finished(self, success, error_message):
        """
        Unfreeze the UI and shows the result of save.
        :param success:
        :param error_message:
        :return:
        """
        self.ui_manager.unlock_ui()

        if success:
            self.orders_tab.refresh_data()
            self.ui_manager.switch_to_tab(self.orders_tab)
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save order: {error_message}")

    def cancel_creation(self):
        """
        Cancels order creation or edit and returns to the orders tab.
        :return:
        """
        self.ui_manager.switch_to_tab(self.orders_tab)