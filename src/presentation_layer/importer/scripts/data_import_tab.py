import os
from PyQt5 import QtWidgets, uic

from src.data_access_layer.importer import Importer


class DataImportTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'data_import_tab.ui')
        uic.loadUi(ui_path, self)

        self.btn_browse.clicked.connect(self.browse)
        self.btn_import.clicked.connect(self.import_data)

    def browse(self):
        """
        Browses files and directories.
        :return:
        """
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select a JSON File",
            "",
            "JSON Files (*.json)"
        )
        if file_path:
            self.lineEdit_file_path.setText(file_path)

    def import_data(self):
        """
        Imports data from the selected file.
        :return:
        """
        file_path = self.lineEdit_file_path.text()

        if not file_path:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a file first.")
            return

        try:
            if self.radio_menu_items.isChecked():
                Importer.import_menu_items(file_path)
                msg = "Menu Items imported successfully."
            else:
                Importer.import_employees(file_path)
                msg = "Employees imported successfully."

            QtWidgets.QMessageBox.information(self, "Success", msg)
            self.lineEdit_file_path.clear()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Failed to import data", str(e))