from typing import List
import mysql.connector
from src.data_access_layer.database_connector import DatabaseConnector
from src.objects.order_item import OrderItem
from src.objects.menu_item import MenuItem


class OrderItemsDAO:
    def __init__(self):
        self.db = DatabaseConnector()

    def create(self, order_item: OrderItem | List[OrderItem]):
        """
        Adds order_item to the database.
        :param order_item:
        :return:
        """
        sql = "INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (%(order_id)s, %(menu_item_id)s, %(quantity)s)"

        conn = None

        try:
            conn = self.db.connect()
            order_items_to_add = order_item if isinstance(order_item, list) else [order_item]
            with conn.cursor() as cursor:
                for item in order_items_to_add:
                    cursor.execute(
                        sql,
                        {
                            "order_id": item.order_id,
                            "menu_item_id": item.menu_item.id,
                            "quantity": item.quantity
                        }
                    )
                    item.id = cursor.lastrowid
            conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Failed to add order_item(s): {e}")

    def delete(self, order_item_id: int):
        """
        Deletes the order_item from the database.
        :param order_item_id:
        :return:
        """
        if not isinstance(order_item_id, int):
            raise TypeError("order_item_id must be int")
        conn = None
        sql = "DELETE FROM order_items WHERE id = %(id)s"
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql, {"id": order_item_id})
                conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Failed to remove item: {e}") from e

    def update(self, order_item: OrderItem):
        """
        Updates the order_item in the database.
        :param order_item:
        :return:
        """
        if not isinstance(order_item, OrderItem):
            raise TypeError("order_item must be OrderItem")
        sql = "UPDATE order_items SET order_id = %(order_id)s, menu_item_id = %(menu_item_id)s, quantity = %(quantity)s WHERE id = %(id)s"
        conn = None
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    {
                        "id": order_item.id,
                        "order_id": order_item.order_id,
                        "menu_item_id": order_item.menu_item.id,
                        "quantity": order_item.quantity
                    }
                )
                conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Failed to update item: {e}") from e

    def get_items_by_order_id(self, order_id: int) -> List[OrderItem]:
        """
        Fetches order_items with the matching order_id from the database.
        :param order_id:
        :return:
        """
        sql = """
              SELECT id,
                     order_id,
                     quantity,
                     total_price,
                     total_vat,
                     menu_item_id,
                     item_name,
                     item_type,
                     item_price,
                     vat_percentage,
                     item_vat
              FROM order_items
              WHERE order_id = %s \
              """
        items = []
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql, (order_id,))
                for row in cursor:

                    menu_item = MenuItem.from_db(
                        menu_item_id=row[5],
                        name=row[6],
                        item_type=row[7],
                        price=float(row[8]),
                        vat_percentage=int(row[9]),
                        vat=float(row[10])
                    )

                    order_item = OrderItem.from_db(
                        id=row[0],
                        order_id=row[1],
                        menu_item=menu_item,
                        quantity=row[2],
                        total_price=float(row[3]),
                        total_vat=float(row[4])
                    )
                    items.append(order_item)
            return items
        except mysql.connector.Error as e:
            raise RuntimeError(f"Failed to fetch order items: {e}")