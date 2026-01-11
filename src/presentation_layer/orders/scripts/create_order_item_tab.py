import os
from PyQt5 import QtWidgets, uic
from src.objects.order_item import OrderItem


class CreateOrderItemTab(QtWidgets.QDialog):
    def __init__(self, parent=None, menu_items_manager=None, order_item=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'create_order_item_tab.ui')
        uic.loadUi(ui_path, self)

        self.menu_items_manager = menu_items_manager
        self.load_choices()

        if order_item:
            self.setWindowTitle("Edit Order Item")
            self.set_data(order_item)
        else:
            self.setWindowTitle("Add Order Item")

    def load_choices(self):
        """
        Loads possible choices for the user.
        :return:
        """
        self.menu_items_manager.load_menu_items()
        for item in self.menu_items_manager.menu_items:
            self.combo_items.addItem(f"{item.name} - {item.price}", item)

    def set_data(self, order_item):
        """
        Pre-fills the UI widgets with values from an existing order_item object.
        :param order_item:
        :return:
        """
        self.spin_quantity.setValue(order_item.quantity)

        index = self.combo_items.findData(order_item.menu_item)
        if index >= 0:
            self.combo_items.setCurrentIndex(index)
        else:
            for i in range(self.combo_items.count()):
                data = self.combo_items.itemData(i)
                if data and data.id == order_item.menu_item.id:
                    self.combo_items.setCurrentIndex(i)
                    break

    def get_data(self):
        """
        Returns data from user input.
        :return:
        """
        return {
            "menu_item": self.combo_items.currentData(),
            "quantity": self.spin_quantity.value()
        }