from datetime import datetime
from src.objects.order_item import OrderItem

class Order:
    def __init__(self, employee_id: int, name: str, is_paid: bool):
        self.employee_id = employee_id
        self.name = name
        self.is_paid = is_paid
        self.order_items = []

        self.employee_first_name = None
        self.employee_last_name = None

        self.id = None
        self.creation_date = None
        self.total_price = 0
        self.total_vat = 0

    @classmethod
    def from_db(cls, id, employee_id, first_name, last_name, name, creation_date, is_paid, total_price, total_vat):
        order = cls(employee_id, name, bool(is_paid))
        order.id = id
        order.employee_first_name = first_name
        order.employee_last_name = last_name
        order.creation_date = creation_date
        order.total_price = total_price
        order.total_vat = total_vat
        return order

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("name must be str")
        self._name = value

    @property
    def creation_date(self):
        return self._creation_date

    @creation_date.setter
    def creation_date(self, value):
        if value is not None and not isinstance(value, datetime):
            raise TypeError("creation_date must be datetime or None")
        self._creation_date = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("id must be int")
        self._id = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("employee_id must be int or None")
        self._employee_id = value

    @property
    def is_paid(self):
        return self._is_paid

    @is_paid.setter
    def is_paid(self, value):
        if not isinstance(value, bool):
            raise ValueError("is_paid must a bool")
        self._is_paid = value

    @property
    def total_price(self):
        return self._total_price

    @total_price.setter
    def total_price(self, value):
        if not isinstance(value, (int, float, type(None))):
            raise TypeError("total_price must be a number")
        self._total_price = value or 0.0

    @property
    def total_vat(self):
        return self._total_vat

    @total_vat.setter
    def total_vat(self, value):
        if not isinstance(value, (int, float, type(None))):
            raise TypeError("total_vat must be a number")
        self._total_vat = value or 0.0

    def add_order_item(self, order_item: OrderItem):
        if not isinstance(order_item, OrderItem):
            raise TypeError("item must be OrderItem instance")
        order_item.order_id = self.id
        self.order_items.append(order_item)