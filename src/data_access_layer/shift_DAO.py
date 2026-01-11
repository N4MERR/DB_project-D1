import mysql.connector
from src.data_access_layer.database_connector import DatabaseConnector
from src.objects.shift import Shift

class ShiftsDAO:
    def __init__(self):
        self.db = DatabaseConnector()

    def get_shifts_by_date(self, target_date):
        """
        Gets shifts for a specific date from the database.
        :param target_date:
        :return: List of shifts with the matching date.
        """
        sql = "SELECT id, employee_id, employee_first_name, employee_last_name, start_time, end_time, hourly_rate FROM view_shifts_log WHERE shift_date = %s ORDER BY start_time"
        shifts = []
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql, (target_date,))
                for row in cursor:
                    shifts.append(Shift.from_db(
                        row[0], row[1], row[2], row[3], row[4], row[5], float(row[6])
                    ))
            return shifts
        except mysql.connector.Error as e:
            raise RuntimeError(f"Failed to load shifts: {e}")

    def add(self, shift: Shift):
        """
        Adds a shift to the database.
        :param shift:
        :return:
        """
        sql = "INSERT INTO shifts (employee_id, start_time, end_time, hourly_rate) VALUES (%(emp_id)s, %(start)s, %(end)s, %(rate)s)"
        conn = None
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql, {
                    "emp_id": shift.employee_id,
                    "start": shift.start_time,
                    "end": shift.end_time,
                    "rate": shift.hourly_rate
                })
                shift.id = cursor.lastrowid
            conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Could not add shift: {e}")

    def update(self, shift: Shift):
        """
        Updates the matching shift in the database.
        :param shift:
        :return:
        """
        sql = "UPDATE shifts SET employee_id=%(emp_id)s, start_time=%(start)s, end_time=%(end)s, hourly_rate=%(rate)s WHERE id=%(id)s"
        conn = None
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql, {
                    "emp_id": shift.employee_id,
                    "start": shift.start_time,
                    "end": shift.end_time,
                    "rate": shift.hourly_rate,
                    "id": shift.id
                })
                conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Could not update shift: {e}")

    def delete(self, shift_id: int):
        """
        Deletes the shift with the matching id from the database.
        :param shift_id:
        :return:
        """
        sql = "DELETE FROM shifts WHERE id = %(id)s"
        conn = None
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql, {"id": shift_id})
                conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Could not delete shift: {e}")