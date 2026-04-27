import json
import os

DATABASE_FILE = "data/funcionarios.json"

def create_database():
    """
    Creates an empty JSON database file if it doesn't already exist.
    """
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as f:
            json.dump({}, f)
        print(f"Database file '{DATABASE_FILE}' created.")

def add_employee(employee_name: str, employee_data: dict):
    """
    Adds a new employee to the database, using their name as the unique ID.

    Args:
        employee_name (str): The unique name of the employee.
        employee_data (dict): A dictionary containing the employee's information.
    """
    create_database()
    with open(DATABASE_FILE, 'r+') as f:
        data = json.load(f)
        if employee_name in data:
            print(f"Error: Employee with the name '{employee_name}' already exists.")
        else:
            data[employee_name] = employee_data
            f.seek(0)
            json.dump(data, f, indent=4)
            print(f"Employee '{employee_name}' added successfully.")

def delete_employee(employee_name: str):
    """
    Deletes an employee from the database, using their name as the unique ID.

    Args:
        employee_name (str): The unique name of the employee to delete.
    """
    if not os.path.exists(DATABASE_FILE):
        print("Error: Database file not found.")
        return

    with open(DATABASE_FILE, 'r+') as f:
        data = json.load(f)
        if employee_name not in data:
            print(f"Error: Employee with the name '{employee_name}' not found.")
        else:
            del data[employee_name]
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
            print(f"Employee '{employee_name}' deleted successfully.")

def get_all_employees():
    """
    Retrieves all employees from the database.

    Returns:
        dict: A dictionary of all employees or an empty dictionary if the file is not found.
    """
    if not os.path.exists(DATABASE_FILE):
        return {}

    with open(DATABASE_FILE, 'r') as f:
        return json.load(f)
