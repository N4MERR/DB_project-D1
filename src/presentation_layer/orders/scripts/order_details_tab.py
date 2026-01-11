import os
import threading
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt
from src.presentation_layer.MyLib.action_delegate import ActionDelegate
from src.aplication_layer.menu_items_manager import MenuItemsManager
from src.presentation_layer.orders.scripts.create_order_item_tab import CreateOrderItemTab
from src.objects.order_item import OrderItem


class OrderDetailsTab(QtWidgets.QWidget):
    load_finished_signal = QtCore.pyqtSignal(bool, str)

    def __init__(self, manager, ui_manager, orders_tab):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'order_details_tab.ui')
        uic.loadUi(ui_path, self)

        self.manager = manager
        self.ui_manager = ui_manager
        self.orders_tab = orders_tab
        self.menu_items_manager = MenuItemsManager()
        self.current_order = None

        self.table_order_items.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.action_delegate = ActionDelegate(self.table_order_items)
        self.action_delegate.edit_clicked.connect(self.edit_item)
        self.action_delegate.delete_clicked.connect(self.delete_item)
        self.table_order_items.setItemDelegateForColumn(4, self.action_delegate)

        self.btn_back_to_orders.clicked.connect(self.go_back)
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.btn_add_item_to_order.clicked.connect(self.add_item_dialog)
        self.btn_delete_order.clicked.connect(self.delete_current_order)
        self.btn_pay_order.clicked.connect(self.pay_current_order)

        self.load_finished_signal.connect(self.on_load_finished)

    def go_back(self):
        """
        Go back to the orders tab.
        :return:
        """
        self.orders_tab.refresh_data()
        self.ui_manager.switch_to_tab(self.orders_tab)

    def load_order(self, order):
        """
        Loads order data.
        :param order:
        :return:
        """
        self.current_order = order
        self.lbl_order_name_header.setText(f"Order: {order.name}")
        self.refresh_data()

    def refresh_data(self):
        """
        Locks the UI and starts a new thread to load order data.
        :return:
        """
        if not self.current_order:
            return
        self.ui_manager.lock_ui()
        threading.Thread(target=self._run_load).start()

    def _run_load(self):
        """
        Loads order data.
        :return:
        """
        try:
            items = self.manager.get_order_items(self.current_order.id)
            self.current_order.order_items = items

            total = sum(item.total_price for item in items)
            self.current_order.total_price = total
            self.load_finished_signal.emit(True, "")
        except Exception as e:
            self.load_finished_signal.emit(False, str(e))

    def on_load_finished(self, success, error):
        """
        Unfreezes the UI and shows the result of loading.
        :param success:
        :param error:
        :return:
        """
        self.ui_manager.unlock_ui()
        if not success:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load items: {error}")
            return

        self.lbl_order_total_footer.setText(f"Total: {self.current_order.total_price:.2f}")
        self.populate_table()

    def populate_table(self):
        """
        Loads order data into the table.
        :return:
        """
        self.table_order_items.setRowCount(0)
        self.table_order_items.setSortingEnabled(False)

        for item in self.current_order.order_items:
            row = self.table_order_items.rowCount()
            self.table_order_items.insertRow(row)

            name_item = QtWidgets.QTableWidgetItem(item.menu_item.name)
            name_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table_order_items.setItem(row, 0, name_item)

            qty_item = QtWidgets.QTableWidgetItem(str(item.quantity))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.table_order_items.setItem(row, 1, qty_item)

            price_item = QtWidgets.QTableWidgetItem(f"{item.menu_item.price:.2f}")
            price_item.setTextAlignment(Qt.AlignCenter)
            self.table_order_items.setItem(row, 2, price_item)

            total_item = QtWidgets.QTableWidgetItem(f"{item.total_price:.2f}")
            total_item.setTextAlignment(Qt.AlignCenter)
            self.table_order_items.setItem(row, 3, total_item)

            action_item = QtWidgets.QTableWidgetItem()
            action_item.setData(Qt.UserRole, item)
            self.table_order_items.setItem(row, 4, action_item)

        self.table_order_items.resizeRowsToContents()
        self.table_order_items.setSortingEnabled(True)

    def add_item_dialog(self):
        """
        Opens the order_item creating tab and waits for user confirmation, then adds the new order_item.
        :return:
        """
        dialog = CreateOrderItemTab(self, self.menu_items_manager)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            try:
                new_item = OrderItem(data['menu_item'], data['quantity'])
                new_item.order_id = self.current_order.id
                self.manager.add_order_item(new_item)
                self.refresh_data()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to add item: {e}")

    def edit_item(self, order_item):
        """
        Opens the order_item editing tab and waits for user confirmation, then edits the order_item.
        :param order_item:
        :return:
        """
        dialog = CreateOrderItemTab(self, self.menu_items_manager, order_item=order_item)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            try:
                order_item.menu_item = data['menu_item']
                order_item.quantity = data['quantity']
                self.manager.edit_order_item(order_item)
                self.refresh_data()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to edit item: {e}")

    def delete_item(self, order_item):
        """
        Opens a window that ask user for confirmation.
        If user confirms delete the order_item and show the result.
        :param order_item:
        :return:
        """
        confirm = QtWidgets.QMessageBox.question(self, "Confirm", "Delete this item?",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm == QtWidgets.QMessageBox.Yes:
            try:
                self.manager.delete_order_item(order_item.id)
                self.refresh_data()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete item: {e}")

    def delete_current_order(self):
        """
        Opens a window that ask user for confirmation.
        If user confirms delete the current order and show the result.
        :return:
        """
        reply = QtWidgets.QMessageBox.question(
            self, 'Delete Order', "Delete this entire order?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                self.manager.delete_order(self.current_order.id)
                self.go_back()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete order: {e}")

    def pay_current_order(self):
        """
        Opens a window that asks user for confirmation.
        If user confirms pay the current order and show the result.
        :return:
        """
        reply = QtWidgets.QMessageBox.question(
            self, 'Pay Order', f"Pay and close order? Total: {self.current_order.total_price:.2f}",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                self.manager.pay_order(self.current_order.id)
                self.go_back()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to pay order: {e}")