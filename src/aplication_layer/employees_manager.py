from src.data_access_layer.employees_DAO import EmployeesDAO
from src.objects.employee import Employee


class EmployeesManager:
    def __init__(self):
        self.employees = []
        self._employee_DAO = EmployeesDAO()

    @property
    def employees(self):
        return self._employees

    @employees.setter
    def employees(self, value):
        if not isinstance(value, list):
            raise ValueError("employees must be an instance of list")
        self._employees = value

    def load_employees(self):
        """
        Loads employees from the database into employees list.
        :return:
        """
        self.employees = self._employee_DAO.load()

    def add_employee(self, employee: Employee):
        """
        Adds an employee to the employees list and the database.
        :param employee:
        :return:
        """
        if not isinstance(employee, Employee):
            raise ValueError("employee must be an instance of Employee")

        self.employees.append(employee)
        self._employee_DAO.add(employee)

    def delete_employee(self, employee_id: int):
        """
        Deletes an employee from the employees list and the Database.
        :param employee_id:
        :return:
        """
        if not isinstance(employee_id, int):
            raise ValueError("employee id must be an integer")

        for employee in self.employees:
            if employee.id == employee_id:
                self.employees.remove(employee)

        self._employee_DAO.delete(employee_id)

    def edit_employee(self, employee: Employee):
        """
        Edits an employee from the employees list and the database.
        :param employee:
        :return:
        """
        if not isinstance(employee, Employee):
            raise ValueError("employee must be an instance of Employee")

        self._employee_DAO.update(employee)

        for i, emp in enumerate(self.employees):
            if emp.id == employee.id:
                self.employees[i] = emp
                break
