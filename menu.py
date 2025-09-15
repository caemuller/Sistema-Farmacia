import tkinter as tk
from tkinter import messagebox
import json
import os
import datetime

DATABASE_FILE = "funcionarios.json"
FORMULAS_FILE = "formulas.json"

def create_databases():
    """Ensures the JSON files for employees and formulas exist."""
    for file_path in [DATABASE_FILE, FORMULAS_FILE]:
        if not os.path.exists(file_path):
            if file_path == FORMULAS_FILE:
                with open(file_path, 'w') as f:
                    json.dump([], f)
            else:
                with open(file_path, 'w') as f:
                    json.dump({}, f)

def get_employees():
    """Reads all employees from the JSON file."""
    try:
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def add_employee_logic(name):
    """Adds a new employee to the database."""
    employees = get_employees()
    if name in employees:
        return False, f"Error: An employee with the name '{name}' already exists."
    else:
        employees[name] = {"name": name}
        with open(DATABASE_FILE, 'w') as f:
            json.dump(employees, f, indent=4)
        return True, f"Employee '{name}' added successfully."

def remove_employee_logic(name):
    """Removes an employee from the database."""
    employees = get_employees()
    if name not in employees:
        return False, f"Error: Employee '{name}' not found."
    else:
        del employees[name]
        with open(DATABASE_FILE, 'w') as f:
            json.dump(employees, f, indent=4)
        return True, f"Employee '{name}' removed successfully."

def add_formula_logic():
    """A placeholder for the 'Adicionar Formulas' functionality."""
    # This function will be expanded later
    messagebox.showinfo("Adicionar Formulas", "This function is not yet implemented.")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Produção")
        self.root.geometry("400x300")
       
       
        if datetime.date.today().weekday() == 0:
            self.actual_date = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
        else:
            self.actual_date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()


        create_databases()

        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack(expand=True)

        self.title_label = tk.Label(self.main_frame, text="Selecione uma opção:", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

        # Adicionar Formulas Button
        self.btn_formulas = tk.Button(self.main_frame, text="Adicionar Formulas", width=25, command=self.show_formulas_window)
        self.btn_formulas.pack(pady=5)

        # Cadastrar Funcionario Button
        self.btn_add_employee = tk.Button(self.main_frame, text="Cadastrar Funcionario", width=25, command=self.show_add_employee_window)
        self.btn_add_employee.pack(pady=5)

        # Remover Funcionario Button
        self.btn_remove_employee = tk.Button(self.main_frame, text="Remover Funcionario", width=25, command=self.show_remove_employee_window)
        self.btn_remove_employee.pack(pady=5)

    def show_formulas_window(self):


        add_formula_logic()

    def show_add_employee_window(self):
        """Displays the 'Cadastrar Funcionario' window."""
        add_win = tk.Toplevel(self.root)
        add_win.title("Cadastrar Funcionario")
        add_win.geometry("300x150")

        tk.Label(add_win, text="Nome do Funcionario:", font=("Helvetica", 12)).pack(pady=5)
        self.add_entry = tk.Entry(add_win, width=30)
        self.add_entry.pack(pady=5)

        tk.Button(add_win, text="Cadastrar", command=self.handle_add_employee).pack(pady=10)

    def handle_add_employee(self):
        """Handles the logic for adding an employee from the GUI."""
        name = self.add_entry.get().strip()
        if name:
            success, message = add_employee_logic(name)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
            self.add_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Name cannot be empty.")

    def show_remove_employee_window(self):
        """Displays the 'Remover Funcionario' window."""
        remove_win = tk.Toplevel(self.root)
        remove_win.title("Remover Funcionario")
        remove_win.geometry("300x200")

        employees = get_employees()
        
        if not employees:
            tk.Label(remove_win, text="No employees to remove.", font=("Helvetica", 12)).pack(pady=20)
            return

        tk.Label(remove_win, text="Selecione o funcionario:", font=("Helvetica", 12)).pack(pady=5)
        
        # Use a dropdown (OptionMenu) to select the employee
        self.employee_var = tk.StringVar(remove_win)
        self.employee_var.set("Select...")
        self.employee_dropdown = tk.OptionMenu(remove_win, self.employee_var, *employees.keys())
        self.employee_dropdown.pack(pady=5)

        tk.Button(remove_win, text="Remover", command=self.handle_remove_employee).pack(pady=10)

    def handle_remove_employee(self):
        """Handles the logic for removing an employee from the GUI."""
        name = self.employee_var.get()
        if name and name != "Select...":
            success, message = remove_employee_logic(name)
            if success:
                messagebox.showinfo("Success", message)
                # Refresh the remove window to update the dropdown
                self.show_remove_employee_window() 
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showerror("Error", "Please select an employee.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()