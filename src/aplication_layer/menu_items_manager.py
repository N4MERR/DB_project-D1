from src.data_access_layer.menu_items_DAO import MenuItemsDAO
from src.objects.menu_item import MenuItem


class MenuItemsManager:
    def __init__(self):
        self.menu_items = []
        self._menu_items_DAO = MenuItemsDAO()

    @property
    def menu_items(self):
        return self._menu_items

    @menu_items.setter
    def menu_items(self, value: list):
        if not isinstance(value, list):
            raise ValueError("menu_items must be a list")
        self._menu_items = value

    def load_menu_items(self):
        """
        Loads menu items from the database into the menu_items list.
        :return:
        """
        self.menu_items = self._menu_items_DAO.load()

    def add_menu_item(self, menu_item: MenuItem):
        """
        Adds a menu item into the menu_items list and the database.
        :param menu_item:
        :return:
        """
        if not isinstance(menu_item, MenuItem):
            raise ValueError("menu_item must be an instance of MenuItem")

        self.menu_items.append(menu_item)
        self._menu_items_DAO.add(menu_item)

    def delete_menu_item(self, menu_item_id: int):
        """
        Deletes a menu item from the menu_items list and the database.
        :param menu_item_id:
        :return:
        """
        if not isinstance(menu_item_id, int):
            raise ValueError("menu_item_id must be an integer")

        for menu_item in self.menu_items:
            if menu_item.id == menu_item_id:
                self.menu_items.remove(menu_item)

        self._menu_items_DAO.delete(menu_item_id)

    def edit_menu_item(self, menu_item: MenuItem):
        """
        Edits a menu item from the menu_items list and the database.
        :param menu_item:
        :return:
        """
        if not isinstance(menu_item, MenuItem):
            raise ValueError("menu_item must be an instance of MenuItem")

        self._menu_items_DAO.update(menu_item)

        for i, item in enumerate(self.menu_items):
            if item.id == menu_item.id:
                self.menu_items[i] = menu_item
                break
