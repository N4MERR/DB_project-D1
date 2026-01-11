from src.data_access_layer.shift_DAO import ShiftsDAO
from src.objects.shift import Shift

class ShiftsManager:
    def __init__(self):
        self._shift_DAO = ShiftsDAO()
        self.shifts = []

    def get_shifts_for_date(self, date):
        """
        Loads shifts with the matching date
        :param date:
        :return:
        """
        self.shifts = self._shift_DAO.get_shifts_by_date(date)
        return self.shifts

    def add_shift(self, shift: Shift):
        """
        Adds a shift to the database
        :param shift:
        :return:
        """
        if not isinstance(shift, Shift):
            raise TypeError('Shift must be of type Shift')
        self._shift_DAO.add(shift)

    def edit_shift(self, shift: Shift):
        """
        Edits a shift in the database.
        :param shift:
        :return:
        """
        if not isinstance(shift, Shift):
            raise TypeError('Shift must be of type Shift')
        self._shift_DAO.update(shift)

    def delete_shift(self, shift_id: int):
        """
        Deletes the shift with the matching id from the database.
        :param shift_id:
        :return:
        """
        if not isinstance(shift_id, int):
            raise TypeError('Shift ID must be an integer')
        self._shift_DAO.delete(shift_id)