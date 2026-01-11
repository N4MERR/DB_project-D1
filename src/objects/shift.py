from datetime import datetime


class Shift:
    def __init__(self, employee_id: int, start_time: datetime, end_time: datetime, hourly_rate: float):
        self.employee_id = employee_id
        self.start_time = start_time
        self.end_time = end_time
        self.hourly_rate = hourly_rate

        self.employee_first_name = None
        self.employee_last_name = None
        self.id = None

    @classmethod
    def from_db(cls, id: int, employee_id: int, first_name: str, last_name: str, start_time: datetime,
                end_time: datetime, hourly_rate: float):
        shift = cls(employee_id, start_time, end_time, hourly_rate)
        shift.id = id
        shift.employee_first_name = first_name
        shift.employee_last_name = last_name
        return shift

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("id must be int or None")
        self._id = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Allow None if employee was deleted
        if value is not None and not isinstance(value, int):
            raise TypeError("employee_id must be int or None")
        self._employee_id = value

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        if not isinstance(value, datetime):
            raise TypeError("start_time must be datetime")
        if hasattr(self, "_end_time") and self._end_time and value >= self._end_time:
            raise ValueError("start_time must be before end_time")
        self._start_time = value

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        if not isinstance(value, datetime):
            raise TypeError("end_time must be datetime")
        if hasattr(self, "_start_time") and self._start_time and value <= self._start_time:
            raise ValueError("end_time must be after start_time")
        self._end_time = value

    @property
    def hourly_rate(self):
        return self._hourly_rate

    @hourly_rate.setter
    def hourly_rate(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("hourly_rate must be a number")
        if value <= 0:
            raise ValueError("hourly_rate must be > 0")
        self._hourly_rate = value