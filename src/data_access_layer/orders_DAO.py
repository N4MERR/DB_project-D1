import mysql.connector
from src.data_access_layer.database_connector import DatabaseConnector
from src.data_access_layer.order_items_DAO import OrderItemsDAO
from src.objects.order import Order


class OrdersDAO:
    def __init__(self):
        self.db = DatabaseConnector()
        self._order_items_DAO = OrderItemsDAO

    def set_paid(self, order_id: int, is_paid: bool):
        """
        Sets is_paid in the database.
        :param order_id:
        :param is_paid:
        :return:
        """
        if not isinstance(order_id, int):
            raise TypeError("Order id must be an instance of int")
        if not isinstance(is_paid, bool):
            raise TypeError("is_paid must be bool")

        sql = "UPDATE orders SET is_paid = %(is_paid)s WHERE id = %(id)s"

        conn = None
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    {
                        "is_paid": int(is_paid),
                        "id": order_id
                    }
                )
                conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Payment update failed: {e}")

    def delete(self, order_id):
        """
        Deletes the order with the matching id from the database.
        :param order_id:
        :return:
        """
        if not isinstance(order_id, int):
            raise TypeError("Order id must be an instance of int")

        sql = "DELETE FROM orders WHERE id = %(id)s"

        conn = None
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql, {"id": order_id})
                conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Order delete failed: {e}")

    def create(self, order: Order):
        """
        Adds order into the database.
        :param order:
        :return:
        """
        if not isinstance(order, Order):
            raise TypeError("Order must be an instance of Order")

        sql_order = "INSERT INTO orders (employee_id, name, is_paid) VALUES (%(employee_id)s, %(name)s, %(is_paid)s)"
        sql_item = "INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (%(order_id)s, %(menu_item_id)s, %(quantity)s)"
        sql_fetch = "SELECT creation_date, employee_first_name, employee_last_name FROM orders WHERE id = %s"

        conn = None

        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            cursor.execute(
                sql_order,
                {
                    "employee_id": order.employee_id,
                    "name": order.name,
                    "is_paid": int(order.is_paid),
                },
            )
            order.id = cursor.lastrowid

            for item in order.order_items:
                cursor.execute(
                    sql_item,
                    {
                        "order_id": order.id,
                        "menu_item_id": item.menu_item.id,
                        "quantity": item.quantity
                    }
                )
                item.id = cursor.lastrowid
                item.order_id = order.id

            cursor.execute(sql_fetch, (order.id,))
            result = cursor.fetchone()
            if result:
                order.creation_date = result[0]
                order.employee_first_name = result[1]
                order.employee_last_name = result[2]

            conn.commit()
            cursor.close()

        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Order create failed: {e}")

    def update(self, order: Order):
        """
        Updates the order in the database.
        :param order:
        :return:
        """
        if not isinstance(order, Order):
            raise TypeError("Order must be an instance of Order")

        sql_update_header = """
                            UPDATE orders o
                                JOIN employees e 
                            ON e.id = %(employee_id)s
                                SET
                                    o.employee_id = %(employee_id)s, o.name = %(name)s, o.employee_first_name = e.first_name, o.employee_last_name = e.last_name
                            WHERE o.id = %(id)s
                            """

        sql_get_current_ids = "SELECT id FROM order_items WHERE order_id = %s"

        sql_update_item = "UPDATE order_items SET quantity = %(quantity)s WHERE id = %(id)s"

        sql_insert_item = "INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (%(order_id)s, %(menu_item_id)s, %(quantity)s)"

        conn = None
        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            cursor.execute(sql_update_header, {
                "employee_id": order.employee_id,
                "name": order.name,
                "id": order.id
            })

            cursor.execute(sql_get_current_ids, (order.id,))
            current_db_ids = {row[0] for row in cursor.fetchall()}

            passed_ids = set()

            for item in order.order_items:
                if item.id and item.id in current_db_ids:
                    passed_ids.add(item.id)
                    cursor.execute(sql_update_item, {
                        "quantity": item.quantity,
                        "id": item.id
                    })
                else:
                    cursor.execute(sql_insert_item, {
                        "order_id": order.id,
                        "menu_item_id": item.menu_item.id,
                        "quantity": item.quantity
                    })
                    item.id = cursor.lastrowid
                    item.order_id = order.id

            ids_to_delete = current_db_ids - passed_ids
            if ids_to_delete:
                format_strings = ','.join(['%s'] * len(ids_to_delete))
                sql_delete = f"DELETE FROM order_items WHERE id IN ({format_strings})"
                cursor.execute(sql_delete, list(ids_to_delete))

            conn.commit()
            cursor.close()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Order update failed: {e}")

    def get_unpaid_orders(self):
        """
        Fetches all unpaid orders from the database.
        :return:
        """
        sql = "SELECT * FROM view_paid_orders"

        try:
            orders = []
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql)
                for row in cursor:
                    orders.append(Order.from_db(row[0], row[1], row[2], row[3], row[4], row[5], row[6], float(row[7]), float(row[8])))
            return orders
        except mysql.connector.Error as e:
            raise RuntimeError(f"Order get unpaid orders failed: {e}")