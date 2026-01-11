class MenuItem:
    VALID_ITEM_TYPES = ['appetizer', 'main', 'dessert', 'beverage']
    VALID_VAT_PERCENTAGES = [0, 10, 15, 21]

    def __init__(self, name: str, item_type: str, price: float, vat_percentage: int):
        self.name = name
        self.item_type = item_type
        self.price = price
        self.vat_percentage = vat_percentage

        self.id = None
        self.vat = None

    @classmethod
    def from_db(cls, menu_item_id: int, name: str, item_type: str, price: float, vat_percentage: int, vat: float):
        menu_item = MenuItem(name, item_type, price, vat_percentage)
        menu_item.id = menu_item_id
        menu_item.vat = vat
        return menu_item

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("id must be int or None")
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("name must be string")
        if not value:
            raise ValueError("name cannot be empty")
        self._name = value

    @property
    def item_type(self):
        return self._item_type

    @item_type.setter
    def item_type(self, value):
        if not isinstance(value, str):
            raise TypeError("item_type must be string")
        if value not in self.VALID_ITEM_TYPES:
            raise ValueError(f"item_type must be one of {self.VALID_ITEM_TYPES}")
        self._item_type = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("price must be a number")
        if value <= 0:
            raise ValueError("price must be > 0")
        self._price = value

    @property
    def vat(self):
        return self._vat

    @vat.setter
    def vat(self, value):
        if value is not None and not isinstance(value, (int, float)):
            raise TypeError("vat must be a number or None")
        if isinstance(value, (int, float)) and value < 0:
            raise ValueError("vat must be > 0")
        self._vat = value


    @property
    def vat_percentage(self):
        return self._vat_percentage

    @vat_percentage.setter
    def vat_percentage(self, value):
        if not isinstance(value, int):
            raise TypeError("vat_percentage must be int")
        if value not in self.VALID_VAT_PERCENTAGES:
            raise ValueError(f"vat_percentage must be one of {self.VALID_VAT_PERCENTAGES}")
        self._vat_percentage = value
