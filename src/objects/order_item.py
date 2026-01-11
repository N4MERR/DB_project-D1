from src.objects.menu_item import MenuItem


class OrderItem:
    def __init__(self, menu_item: MenuItem, quantity: int):
        self.menu_item = menu_item
        self.quantity = quantity

        self.order_id = None
        self.id = None

        self.total_price = 0
        self.total_vat = 0

    @classmethod
    def from_db(cls, id: int, order_id: int, menu_item: MenuItem, quantity: int,total_price: float, total_vat: float):
        order_item = cls(menu_item, quantity)
        order_item.id = id
        order_item.order_id = order_id
        order_item.total_price = total_price
        order_item.total_vat = total_vat

        return order_item

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("id must be int or None")
        self._id = value

    @property
    def order_id(self):
        return self._order_id

    @order_id.setter
    def order_id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("order_id must be int")
        self._order_id = value

    @property
    def menu_item(self):
        return self._menu_item

    @menu_item.setter
    def menu_item(self, value):
        if not isinstance(value, MenuItem):
            raise TypeError("menu_item must be MenuItem instance")
        self._menu_item = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if not isinstance(value, int):
            raise TypeError("quantity must be int")
        if value <= 0:
            raise ValueError("quantity must be > 0")
        self._quantity = value