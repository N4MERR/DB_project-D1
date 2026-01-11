import os
from PyQt5 import QtWidgets, uic, QtCore

class ShiftsTab(QtWidgets.QWidget):
    def __init__(self, manager, ui_manager, details_tab):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'shifts_tab.ui')
        uic.loadUi(ui_path, self)

        self.manager = manager
        self.ui_manager = ui_manager
        self.details_tab = details_tab

        self.calendar_shifts.clicked.connect(self.on_date_clicked)

    def on_date_clicked(self, date):
        python_date = date.toPyDate()
        self.details_tab.load_date(python_date)
        self.ui_manager.switch_to_tab(self.details_tab)