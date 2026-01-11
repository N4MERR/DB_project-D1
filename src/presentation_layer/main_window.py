import os
from PyQt5 import QtWidgets, uic, QtCore

from src.aplication_layer.employees_manager import EmployeesManager
from src.aplication_layer.menu_items_manager import MenuItemsManager
from src.aplication_layer.orders_manager import OrdersManager
from src.aplication_layer.shifts_manager import ShiftsManager
from src.aplication_layer.reports_manager import ReportsManager

from src.presentation_layer.orders.scripts.orders_tab import OrdersTab
from src.presentation_layer.employees.scripts.employees_tab import EmployeesTab
from src.presentation_layer.menu_items.scripts.menu_items_tab import MenuItemsTab
from src.presentation_layer.shifts.scripts.shifts_tab import ShiftsTab
from src.presentation_layer.orders.scripts.order_details_tab import OrderDetailsTab
from src.presentation_layer.shifts.scripts.shift_details_tab import ShiftDetailsTab
from src.presentation_layer.importer.scripts.data_import_tab import DataImportTab
from src.presentation_layer.orders.scripts.create_order_tab import CreateOrderTab
from src.presentation_layer.sales_report.scripts.sales_report_tab import SalesReportTab


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(__file__), 'app_main_window.ui')
        uic.loadUi(ui_path, self)

        self._orders_manager = OrdersManager()
        self._employees_manager = EmployeesManager()
        self._menu_items_manager = MenuItemsManager()
        self._shifts_manager = ShiftsManager()
        self._reports_manager = ReportsManager()

        self._employees_tab = EmployeesTab(self._employees_manager, self)
        self._menu_items_tab = MenuItemsTab(self._menu_items_manager, self)
        self._reports_tab = SalesReportTab(self._reports_manager, self)
        self._import_tab = DataImportTab()

        self.main_stack = QtWidgets.QStackedWidget()
        central_layout = self.centralwidget.layout()
        central_layout.removeWidget(self.mainTabWidget)
        self.mainTabWidget.setParent(None)
        central_layout.addWidget(self.main_stack)
        self.main_stack.addWidget(self.mainTabWidget)

        self._orders_tab = OrdersTab(self._orders_manager, self, None)
        self.tab_order_details = OrderDetailsTab(self._orders_manager, self, self._orders_tab)
        self._orders_tab.details_tab = self.tab_order_details

        self.tab_create_order = CreateOrderTab(
            self._orders_manager,
            self._employees_manager,
            self._menu_items_manager,
            self,
            self._orders_tab
        )
        self._orders_tab.create_order_tab = self.tab_create_order

        self.main_stack.addWidget(self.tab_order_details)
        self.main_stack.addWidget(self.tab_create_order)

        self._shifts_tab = ShiftsTab(self._shifts_manager, self, None)
        self.tab_shift_details = ShiftDetailsTab(
            self._shifts_manager,
            self._employees_manager,
            self,
            self._shifts_tab
        )
        self._shifts_tab.details_tab = self.tab_shift_details
        self.main_stack.addWidget(self.tab_shift_details)

        self.mainTabWidget.addTab(self._orders_tab, "Orders")
        self.mainTabWidget.addTab(self._employees_tab, "Employees")
        self.mainTabWidget.addTab(self._menu_items_tab, "Menu Items")
        self.mainTabWidget.addTab(self._shifts_tab, "Calendar")
        self.mainTabWidget.addTab(self._reports_tab, "Sales Report")
        self.mainTabWidget.addTab(self._import_tab, "Import data")

        self.showMaximized()

    def switch_to_tab(self, target_widget):
        if target_widget == self.tab_shift_details:
            self.main_stack.setCurrentWidget(self.tab_shift_details)
        elif target_widget == self.tab_order_details:
            self.main_stack.setCurrentWidget(self.tab_order_details)
        elif target_widget == self.tab_create_order:
            self.main_stack.setCurrentWidget(self.tab_create_order)
        else:
            self.main_stack.setCurrentWidget(self.mainTabWidget)
            if target_widget is not None:
                self.mainTabWidget.setCurrentWidget(target_widget)

    def lock_ui(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.setEnabled(False)

    def unlock_ui(self):
        self.setEnabled(True)
        QtWidgets.QApplication.restoreOverrideCursor()