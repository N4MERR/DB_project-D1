class Employee:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

        self.id = None

    @classmethod
    def from_db(cls, employee_id: int, first_name: str, last_name: str):
        employee = cls(first_name, last_name)
        employee.id = employee_id
        return employee

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("id must be an int or None")
        self._id = value

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        if not isinstance(value, str):
            raise TypeError("first_name must be a string")
        if not value:
            raise ValueError("first_name cannot be empty")
        self._first_name = value

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        if not isinstance(value, str):
            raise TypeError("last_name must be a string")
        if not value:
            raise ValueError("last_name cannot be empty")
        self._last_name = value
