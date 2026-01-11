from typing import List
import mysql.connector

from src.data_access_layer.order_items_DAO import OrderItemsDAO
from src.data_access_layer.orders_DAO import OrdersDAO
from src.data_access_layer.database_connector import DatabaseConnector
from src.objects.order import Order
from src.objects.order_item import OrderItem


class OrdersManager:
    def __init__(self):
        self.orders = []
        self._orders_DAO = OrdersDAO()
        self._order_items_DAO = OrderItemsDAO()
        self._db_connector = DatabaseConnector()

    def load_orders(self):
        """
        Loads orders from the database.
        :return:
        """
        self.orders = self._orders_DAO.get_unpaid_orders()

    def add_order(self, order: Order):
        """
        Adds a new order to the database.
        :param order:
        :return:
        """
        if not isinstance(order, Order):
            raise TypeError("Order must be an instance of Order")

        self._orders_DAO.create(order)
        self.orders.append(order)

    def update_order(self, order: Order):
        """
        Updates the order in the database.
        :param order:
        :return:
        """
        if not isinstance(order, Order):
            raise TypeError("Order must be an instance of Order")

        self._orders_DAO.update(order)
        self.load_orders()

    def remove_order(self, order_id):
        """
        Removes the order from the database.
        :param order_id:
        :return:
        """
        if not isinstance(order_id, int):
            raise TypeError("Order id must be an instance of int")

        for order in self.orders:
            if order.id == order_id:
                self.orders.remove(order)
                break

    def delete_order(self, order_id):
        """
        Deletes the order from the database.
        :param order_id:
        :return:
        """
        if not isinstance(order_id, int):
            raise TypeError("Order id must be an instance of int")

        try:
            self._orders_DAO.delete(order_id)
        except Exception as e:
            raise RuntimeError(f"failed to remove order with id: {order_id}") from e
        self.remove_order(order_id)

    def pay_order(self, order_id):
        """
        Sets is_paid to true for the order with the matching id.
        :param order_id:
        :return:
        """
        if not isinstance(order_id, int):
            raise TypeError("Order id must be an instance of int")
        try:
            self._orders_DAO.set_paid(order_id, True)
            self.remove_order(order_id)
        except Exception as e:
            raise RuntimeError(f"Failed to pay/close order {order_id}") from e

    def get_order_items(self, order_id) -> List[OrderItem]:
        """
        Fetches all order items from the database.
        :param order_id:
        :return:
        """
        if not isinstance(order_id, int):
            raise TypeError("Order id must be an instance of int")
        return self._order_items_DAO.get_items_by_order_id(order_id)

    def add_order_item(self, order_item: OrderItem):
        """
        Adds a new order item to the database.
        :param order_item:
        :return:
        """
        if not isinstance(order_item, OrderItem):
            raise TypeError("Order item must be an instance of OrderItem")

        if order_item.order_id is None:
            raise ValueError("Order item must have an order_id")

        self._order_items_DAO.create(order_item)

        for order in self.orders:
            if order.id == order_item.order_id:
                order.order_items.append(order_item)
                pass

    def edit_order_item(self, order_item: OrderItem):
        """
        Edits a new order item to the database.
        :param order_item:
        :return:
        """
        self._order_items_DAO.update(order_item)

    def delete_order_item(self, order_item_id: int):
        """
        Deletes the order item from the database.
        :param order_item_id:
        :return:
        """
        self._order_items_DAO.delete(order_item_id)

    def remove_order_item(self, order_id: int, order_item_id: int):
        """
        Removes the order item from the database.
        :param order_id:
        :param order_item_id:
        :return:
        """
        if not isinstance(order_id, int):
            raise TypeError("Order id must be an instance of int")
        if not isinstance(order_item_id, int):
            raise TypeError("Order item_id must be an instance of int")

        self._order_items_DAO.delete(order_item_id)
        for order in self.orders:
            if order.id == order_id:
                for order_item in order.order_items:
                    if order_item.id == order_item_id:
                        order.order_items.remove(order_item)
                        break