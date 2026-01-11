from datetime import datetime
from src.data_access_layer.reports_DAO import ReportsDAO

class ReportsManager:
    def __init__(self):
        self._reports_DAO = ReportsDAO()
        self.sales_report_data = []

    def load_sales_report(self, start_date: datetime, end_date: datetime):
        """
        Loads filtered report data.
        """
        self.sales_report_data = self._reports_DAO.get_sales_report(start_date, end_date)