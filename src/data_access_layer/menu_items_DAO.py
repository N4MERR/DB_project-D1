import mysql.connector

from src.data_access_layer.database_connector import DatabaseConnector
from src.objects.menu_item import MenuItem


class MenuItemsDAO:
    def __init__(self):
        self.db = DatabaseConnector()

    def load(self):
        """
        Loads menu items from the database
        :return:
        """
        sql = "SELECT id, name, item_type, price, vat_percentage, vat FROM menu_items order by item_type, name"

        items = []

        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql)
                for row in cursor:
                    items.append(MenuItem.from_db(row[0], row[1], row[2], float(row[3]), row[4], float(row[5])))
            return items
        except mysql.connector.Error as e:
            raise RuntimeError(f"Failed to fetch menu items: {e}")

    def add(self, menu_item: MenuItem | list[MenuItem]):
        sql_insert = "INSERT INTO menu_items (name, item_type, price, vat_percentage) VALUES (%(name)s, %(item_type)s, %(price)s, %(vat_percentage)s)"
        sql_select = "SELECT vat FROM menu_items WHERE id = %(id)s"

        items_to_add = menu_item if isinstance(menu_item, list) else [menu_item]
        conn = None

        try:
            conn = self.db.connect()

            with conn.cursor() as cursor:
                for item in items_to_add:
                    cursor.execute(sql_insert, {
                        "name": item.name,
                        "item_type": item.item_type,
                        "price": item.price,
                        "vat_percentage": item.vat_percentage
                    })

                    new_id = cursor.lastrowid
                    item.id = new_id

                    cursor.execute(sql_select, {"id": new_id})
                    row = cursor.fetchone()
                    if row:
                        item.vat = float(row[0])

            conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Failed to add menu item(s): {e}")

    def delete(self, menu_item_id: int):
        """
        Deletes menu_item with the matching id from the database.
        :param menu_item_id:
        :return:
        """
        if not isinstance(menu_item_id, int):
            raise TypeError("Menu item id must be an integer")

        sql = "DELETE FROM menu_items WHERE id = %(id)s"

        conn = None

        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql, {"id": menu_item_id})
                conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Failed to delete item {menu_item_id}: {e}")

    def update(self, menu_item: MenuItem):
        """
        Updates menu item in the database.
        :param menu_item:
        :return:
        """
        update_sql = "UPDATE menu_items SET name = %(name)s, item_type = %(item_type)s, price = %(price)s, vat_percentage = %(vat_percentage)s WHERE id = %(id)s"
        select_vat_sql = "SELECT vat FROM menu_items WHERE id = %(id)s"

        conn = None
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(
                    update_sql,
                    {
                        "id": menu_item.id,
                        "name": menu_item.name,
                        "item_type": menu_item.item_type,
                        "price": menu_item.price,
                        "vat_percentage": menu_item.vat_percentage
                    }
                )

                cursor.execute(select_vat_sql, {"id": menu_item.id})
                row = cursor.fetchone()

                if row:
                    menu_item.vat = float(row[0])

                conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Failed to update menu item: {e}")