import mysql.connector

from src.data_access_layer.database_connector import DatabaseConnector
from src.objects.employee import Employee


class EmployeesDAO:
    def __init__(self):
        self.db = DatabaseConnector()

    def add(self, employee: Employee | list[Employee]):
        sql = "INSERT INTO employees (first_name, last_name) VALUES (%(first_name)s, %(last_name)s)"

        employees_to_add = employee if isinstance(employee, list) else [employee]

        conn = None
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                for emp in employees_to_add:
                    cursor.execute(sql, {
                        "first_name": emp.first_name,
                        "last_name": emp.last_name
                    })
                    emp.id = cursor.lastrowid
                conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Failed to add employee(s): {e}")

    def load(self):
        sql = "SELECT id, first_name, last_name FROM employees"
        employees = []
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql)
                for row in cursor:
                    employees.append(Employee.from_db(row[0], row[1], row[2]))
            return employees
        except mysql.connector.Error as e:
            raise RuntimeError(f"Failed to fetch employees: {e}")

    def delete(self, employee_id: int):
        sql = "DELETE FROM employees WHERE id = %(employee_id)s"

        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql, {"employee_id": employee_id})
                conn.commit()
        except mysql.connector.Error as e:
            raise RuntimeError(f"Failed to remove employee: {e}")

    def update(self, employee: Employee):
        if not isinstance(employee, Employee):
            raise TypeError("Employee must be of type Employee")

        sql = "UPDATE employees SET first_name = %(first_name)s, last_name = %(last_name)s WHERE id = %(id)s"

        conn = None
        try:
            conn = self.db.connect()
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    {
                        "first_name": employee.first_name,
                        "last_name": employee.last_name,
                        "id": employee.id
                    }
                )
                conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Failed to update employee: {e}")