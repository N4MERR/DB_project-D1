from typing import List
import mysql.connector
from src.data_access_layer.database_connector import DatabaseConnector
from src.objects.sales_report_row import SalesReportRow


class ReportsDAO:
    def __init__(self):
        self.db = DatabaseConnector()

    def get_sales_report(self, start_date, end_date) -> List[SalesReportRow]:
        """
        Fetches aggregated sales data filtered by date range.
        """
        sql = """
              SELECT mi.item_type         AS category, \
                     mi.name              AS product_name, \
                     COUNT(DISTINCT o.id) AS orders_count, \
                     SUM(oi.quantity)     AS total_quantity_sold, \
                     SUM(oi.total_price)  AS total_revenue, \
                     SUM(oi.total_vat)    AS total_vat
              FROM menu_items mi
                       JOIN order_items oi ON mi.id = oi.menu_item_id
                       JOIN orders o ON oi.order_id = o.id
              WHERE o.creation_date BETWEEN %s AND %s
              GROUP BY mi.item_type, mi.name
              ORDER BY total_revenue DESC; \
              """

        report_data = []
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql, (start_date, end_date))
                for row in cursor:
                    report_data.append(SalesReportRow(
                        category=row[0],
                        product_name=row[1],
                        orders_count=row[2],
                        total_quantity_sold=float(row[3]) if row[3] else 0.0,
                        total_revenue=float(row[4]) if row[4] else 0.0,
                        total_vat=float(row[5]) if row[5] else 0.0
                    ))
            return report_data
        except mysql.connector.Error as e:
            raise RuntimeError(f"Failed to fetch sales report: {e}")