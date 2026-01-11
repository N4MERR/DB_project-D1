class SalesReportRow:
    def __init__(self, category, product_name, orders_count, total_quantity_sold, total_revenue, total_vat):
        self.category = category
        self.product_name = product_name
        self.orders_count = orders_count
        self.total_quantity_sold = total_quantity_sold
        self.total_revenue = total_revenue
        self.total_vat = total_vat