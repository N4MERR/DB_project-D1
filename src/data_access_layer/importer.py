import json

from src.data_access_layer.employees_DAO import EmployeesDAO
from src.data_access_layer.menu_items_DAO import MenuItemsDAO
from src.objects.employee import Employee
from src.objects.menu_item import MenuItem

class Importer:

    @staticmethod
    def import_menu_items(file_path: str):
        """
        Imports menu items from a JSON file into the database.
        :param file_path:
        :return:
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise TypeError("JSON root must be a list of menu_items")

            menu_items = []
            required_keys = {'name', 'item_type', 'price', 'vat_percentage'}

            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    raise TypeError(f"Item at index {i} is not an object")

                if not required_keys.issubset(item.keys()):
                    missing = required_keys - item.keys()
                    raise ValueError(f"Item at index {i} is missing keys: {', '.join(missing)}")

                menu_items.append(
                    MenuItem(
                        item['name'],
                        item['item_type'],
                        item['price'],
                        item['vat_percentage']
                    )
                )

            dao = MenuItemsDAO()
            dao.add(menu_items)

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in {file_path}")

    @staticmethod
    def import_employees(file_path: str):
        """
        Imports employees from a JSON file into the database.
        :param file_path:
        :return:
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise TypeError("JSON root must be a list of employees")

            employees = []
            required_keys = {'first_name', 'last_name'}

            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    raise TypeError(f"Employee at index {i} is not an object")

                if not required_keys.issubset(item.keys()):
                    missing = required_keys - item.keys()
                    raise ValueError(f"Employee at index {i} is missing keys: {', '.join(missing)}")

                employees.append(
                    Employee(
                        item['first_name'],
                        item['last_name']
                    )
                )

            dao = EmployeesDAO()
            dao.add(employees)

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in {file_path}")