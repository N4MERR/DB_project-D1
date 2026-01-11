import os
import threading

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt

from src.aplication_layer.menu_items_manager import MenuItemsManager
from src.objects.menu_item import MenuItem
from src.presentation_layer.menu_items.scripts.create_new_menu_item_tab import CreateMenuItemTab
from src.presentation_layer.MyLib.action_delegate import ActionDelegate


class MenuItemsTab(QtWidgets.QWidget):
    delete_finished_signal = QtCore.pyqtSignal(bool, str)
    load_finished_signal = QtCore.pyqtSignal(bool, str)
    edit_finished_signal = QtCore.pyqtSignal(bool, str)

    def __init__(self, menu_items_manager: MenuItemsManager, ui_manager):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'menu_items_tab.ui')
        uic.loadUi(ui_path, self)

        self._menu_items_manager = menu_items_manager
        self._ui_manager = ui_manager

        self.table_menu.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table_menu.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_menu.verticalHeader().setVisible(False)

        self.action_delegate = ActionDelegate(self.table_menu)
        self.action_delegate.edit_clicked.connect(self.edit_item)
        self.action_delegate.delete_clicked.connect(self.delete_item)
        self.table_menu.setItemDelegateForColumn(6, self.action_delegate)

        self.btn_add_menu_item.clicked.connect(self.add_menu_item)
        self.btn_refresh.clicked.connect(self.load_menu_items)

        self.delete_finished_signal.connect(self.on_delete_finished)
        self.load_finished_signal.connect(self.on_load_finished)
        self.edit_finished_signal.connect(self.on_edit_finished)

        self.load_menu_items()

    def load_menu_items(self):
        """
        Freezes the UI and then loads the menu_items.
        :return:
        """
        self._ui_manager.lock_ui()

        def run_load():
            try:
                self._menu_items_manager.load_menu_items()
                self.load_finished_signal.emit(True, "")
            except Exception as e:
                self.load_finished_signal.emit(False, str(e))

        threading.Thread(target=run_load).start()

    def reload_menu_item_list(self):
        """
        Clears the menu_items table inserts the new data.
        :return:
        """
        self.table_menu.setRowCount(0)
        self.table_menu.setSortingEnabled(False)

        for menu_item in self._menu_items_manager.menu_items:
            row = self.table_menu.rowCount()
            self.table_menu.insertRow(row)

            def create_item(text, align=Qt.AlignLeft):
                item = QtWidgets.QTableWidgetItem(str(text))
                item.setTextAlignment(align | Qt.AlignVCenter)
                return item

            self.table_menu.setItem(row, 0, create_item(menu_item.id, Qt.AlignCenter))
            self.table_menu.setItem(row, 1, create_item(menu_item.name, Qt.AlignLeft))
            self.table_menu.setItem(row, 2, create_item(f"{menu_item.price:.2f}", Qt.AlignRight))
            self.table_menu.setItem(row, 3, create_item(f"{menu_item.vat_percentage}%", Qt.AlignRight))
            self.table_menu.setItem(row, 4, create_item(f"{menu_item.vat:.2f}", Qt.AlignRight))
            self.table_menu.setItem(row, 5, create_item(menu_item.item_type, Qt.AlignCenter))

            action_item = QtWidgets.QTableWidgetItem()
            action_item.setData(Qt.UserRole, menu_item)
            self.table_menu.setItem(row, 6, action_item)

        self.table_menu.setSortingEnabled(True)

    def add_menu_item(self):
        """
        Freezes the UI and adds a menu_item.
        :return:
        """
        create_menu_item_tab = CreateMenuItemTab(self)
        if create_menu_item_tab.exec_() == QtWidgets.QDialog.Accepted:
            data = create_menu_item_tab.get_data()
            try:
                self._menu_items_manager.add_menu_item(
                    MenuItem(data["name"], data["item_type"], data["price"], data["vat_percentage"]))
                self.load_menu_items()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to add item: {str(e)}")

    def edit_item(self, menu_item):
        """
        Freezes the UI and opens the window for editing.
        :param menu_item:
        :return:
        """
        dialog = CreateMenuItemTab(self, menu_item)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            updated_item = MenuItem(data["name"], data["item_type"], data["price"], data["vat_percentage"])
            updated_item.id = menu_item.id

            self._ui_manager.lock_ui()

            def run_edit():
                try:
                    self._menu_items_manager.edit_menu_item(updated_item)
                    self._menu_items_manager.load_menu_items()
                    self.edit_finished_signal.emit(True, "")
                except Exception as e:
                    self.edit_finished_signal.emit(False, f"Edit failed: {str(e)}")

            threading.Thread(target=run_edit).start()

    def delete_item(self, menu_item):
        """
        Opens a prompt that ask user for confirmation.
        If user confirms delete the menu_item.
        :param menu_item:
        :return:
        """
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{menu_item.name}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if confirm == QtWidgets.QMessageBox.Yes:
            self._ui_manager.lock_ui()

            def run_delete():
                try:
                    self._menu_items_manager.delete_menu_item(menu_item.id)
                    self.delete_finished_signal.emit(True, "")
                except Exception as e:
                    self.delete_finished_signal.emit(False, str(e))

            threading.Thread(target=run_delete).start()

    def on_edit_finished(self, success, error_message):
        """
        Unfreezes the UI and shows the user the result of edit.
        :param success:
        :param error_message:
        :return:
        """
        if success:
            self.reload_menu_item_list()
            self._ui_manager.unlock_ui()
            QtWidgets.QMessageBox.information(self, "Success", "Item updated.")
        else:
            self._ui_manager.unlock_ui()
            QtWidgets.QMessageBox.critical(self, "Error", f"Menu Item Update failed:\n{error_message}")

    def on_delete_finished(self, success, error_message):
        """
        Unfreezes the UI and shows the user the result of delete.
        :param success:
        :param error_message:
        :return:
        """
        if success:
            self.reload_menu_item_list()
            self._ui_manager.unlock_ui()
            QtWidgets.QMessageBox.information(self, "Success", "Item deleted.")
        else:
            self._ui_manager.unlock_ui()
            QtWidgets.QMessageBox.critical(self, "Error", f"Menu Item Delete failed:\n{error_message}")

    def on_load_finished(self, success, error_message):
        """
        Freezes the UI and shows the user the result of load.
        :param success:
        :param error_message:
        :return:
        """
        if not success:
            self._ui_manager.unlock_ui()
            QtWidgets.QMessageBox.critical(self, "Error", f"Reload failed:\n{error_message}")
            return

        self.reload_menu_item_list()
        self._ui_manager.unlock_ui()