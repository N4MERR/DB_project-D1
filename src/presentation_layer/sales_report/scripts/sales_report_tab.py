import os
import calendar
from datetime import datetime
from PyQt5 import QtWidgets, uic, QtCore


class SalesReportTab(QtWidgets.QWidget):
    def __init__(self, manager, main_window):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'sales_report_tab.ui')
        uic.loadUi(ui_path, self)

        self.manager = manager
        self.main_window = main_window

        self.setup_tab()
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.refresh_data()

    def setup_tab(self):
        """
        Sets up the tab.
        :return:
        """
        today = datetime.now()
        first_day = today.replace(day=1)
        last_day_num = calendar.monthrange(today.year, today.month)[1]
        last_day = today.replace(day=last_day_num)

        self.date_from.setDate(first_day)
        self.date_to.setDate(last_day)

        self.table_report.setColumnCount(6)
        self.table_report.setHorizontalHeaderLabels(
            ["Product", "Category", "Orders Count", "Qty Sold", "Revenue", "Total VAT"])

        self.table_report.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table_report.verticalHeader().setVisible(False)

        header = self.table_report.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.table_report.setWordWrap(True)

        self.table_report.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_report.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table_report.setFocusPolicy(QtCore.Qt.NoFocus)

    def refresh_data(self):
        """
        Reloads the sales report.
        :return:
        """
        start_date = self.date_from.date().toString("yyyy-MM-dd") + " 00:00:00"
        end_date = self.date_to.date().toString("yyyy-MM-dd") + " 23:59:59"

        try:
            self.manager.load_sales_report(start_date, end_date)
            self.populate_table(self.manager.sales_report_data)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load report: {e}")

    def populate_table(self, data):
        """
        Adds  sales reports to the table.
        :param data:
        :return:
        """
        self.table_report.setRowCount(0)
        self.table_report.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            item_name = QtWidgets.QTableWidgetItem(str(row_data.product_name))
            item_cat = QtWidgets.QTableWidgetItem(str(row_data.category))

            item_orders = QtWidgets.QTableWidgetItem(str(row_data.orders_count))
            item_orders.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

            item_qty = QtWidgets.QTableWidgetItem(str(row_data.total_quantity_sold))
            item_qty.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

            item_rev = QtWidgets.QTableWidgetItem(f"{row_data.total_revenue:.2f}")
            item_rev.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

            item_vat = QtWidgets.QTableWidgetItem(f"{row_data.total_vat:.2f}")
            item_vat.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

            self.table_report.setItem(row_idx, 0, item_name)
            self.table_report.setItem(row_idx, 1, item_cat)
            self.table_report.setItem(row_idx, 2, item_orders)
            self.table_report.setItem(row_idx, 3, item_qty)
            self.table_report.setItem(row_idx, 4, item_rev)
            self.table_report.setItem(row_idx, 5, item_vat)

        self.table_report.resizeRowsToContents()