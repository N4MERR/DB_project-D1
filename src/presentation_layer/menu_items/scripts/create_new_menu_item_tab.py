from PyQt5 import QtWidgets, uic
import os

from src.objects.menu_item import MenuItem


class CreateMenuItemTab(QtWidgets.QDialog):
    def __init__(self, parent=None, menu_item=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'create_new_menu_item_tab.ui')
        uic.loadUi(ui_path, self)

        self.doubleSpinBox_price.setMaximum(1000000.00)
        self.buttonBox.accepted.disconnect(self.accept)
        self.set_options()

        if menu_item:
            self.setWindowTitle("Edit Menu Item")
            self.lineEdit_name.setText(menu_item.name)
            self.doubleSpinBox_price.setValue(menu_item.price)

            index_type = self.comboBox_type.findText(menu_item.item_type)
            if index_type >= 0:
                self.comboBox_type.setCurrentIndex(index_type)

            index_vat = self.comboBox_vat.findData(menu_item.vat_percentage)
            if index_vat >= 0:
                self.comboBox_vat.setCurrentIndex(index_vat)
        else:
            self.setWindowTitle("Add New Menu Item")

        self.buttonBox.accepted.connect(self.validate_inputs)
        self.buttonBox.rejected.connect(self.reject)

    def set_options(self):
        """
        Loads choices for the user.
        :return:
        """
        self.comboBox_type.addItems(MenuItem.VALID_ITEM_TYPES)
        for vat in MenuItem.VALID_VAT_PERCENTAGES:
            self.comboBox_vat.addItem(f"{vat}%", vat)

    def validate_inputs(self):
        """
        Validates the user inputs.
        :return:
        """
        name = self.lineEdit_name.text().strip()
        price = self.doubleSpinBox_price.value()

        if not name:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Name is required.")
            return

        if price <= 0:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Price must be greater than 0.")
            return

        self.accept()

    def get_data(self):
        """
        Gets data from the create_menu_item window.
        :return:
        """
        return {
            "name": self.lineEdit_name.text().strip(),
            "item_type": self.comboBox_type.currentText(),
            "price": self.doubleSpinBox_price.value(),
            "vat_percentage": self.comboBox_vat.currentData()
        }