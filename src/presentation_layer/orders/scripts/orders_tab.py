import os
from PyQt5 import QtWidgets, uic, QtCore
from src.presentation_layer.orders.scripts.order_widget import OrderWidget


class OrdersTab(QtWidgets.QWidget):
    def __init__(self, manager, ui_manager, details_tab, create_order_tab=None):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'orders_tab.ui')
        uic.loadUi(ui_path, self)

        self.manager = manager
        self.ui_manager = ui_manager
        self.details_tab = details_tab
        self.create_order_tab = create_order_tab

        self.btn_refresh.clicked.connect(self.refresh_data)
        self.btn_create_order.clicked.connect(self.open_create_order_tab)
        self.list_orders.itemClicked.connect(self.on_order_clicked)

        self.refresh_data()

    def on_order_clicked(self, item):
        """
        Opens order details for the clicked order.
        :param item:
        :return:
        """
        order = item.data(QtCore.Qt.UserRole)

        try:
            items = self.manager.get_order_items(order.id)
            order.order_items = items

            if self.create_order_tab:
                self.create_order_tab.load_old_order(order)
                self.ui_manager.switch_to_tab(self.create_order_tab)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load order for editing: {e}")

    def refresh_data(self):
        """
        Reloads the orders.
        :return:
        """
        self.list_orders.clear()
        try:
            self.manager.load_orders()
            for order in self.manager.orders:
                item = QtWidgets.QListWidgetItem(self.list_orders)
                item.setData(QtCore.Qt.UserRole, order)

                widget = OrderWidget(order)
                widget.pay_clicked.connect(self.pay_order)
                widget.delete_clicked.connect(self.delete_order)

                item.setSizeHint(widget.sizeHint())
                self.list_orders.addItem(item)
                self.list_orders.setItemWidget(item, widget)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load orders: {e}")

    def open_create_order_tab(self):
        """
        Opens the order creation tab.
        :return:
        """
        if self.create_order_tab:
            self.create_order_tab.open_empty_tab()
            self.ui_manager.switch_to_tab(self.create_order_tab)

    def pay_order(self, order):
        """
        Opens a window that asks user for confirmation.
        If user confirms pay the order.
        :param order:
        :return:
        """
        reply = QtWidgets.QMessageBox.question(
            self, 'Pay Order', f"Pay and close order '{order.name}'?\nTotal: {order.total_price:.2f}",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                self.manager.pay_order(order.id)
                self.refresh_data()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to pay order: {e}")

    def delete_order(self, order):
        """
        Opens a window that asks the user for confirmation.
        If the user confirms delete the order and show the result.
        :param order:
        :return:
        """
        reply = QtWidgets.QMessageBox.question(
            self, 'Delete Order', f"Delete order '{order.name}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                self.manager.delete_order(order.id)
                self.refresh_data()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete order: {e}")