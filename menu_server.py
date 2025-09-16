import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime
import requests

SERVER_URL = "http://192.168.0.168:5000"

# --- File Management Functions (Same as before) ---
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
    try:
        response = requests.get(f"{SERVER_URL}/employees")
        return response.json()
    except:
        return {}

    
def add_employee_logic(name, is_farmaceutico):
    try:
        data = {"name": name}
        if is_farmaceutico:
            data["role"] = "Farmaceutico"
        response = requests.post(f"{SERVER_URL}/employees", json=data)
        if response.status_code == 200:
            return True, response.json().get("message")
        else:
            return False, response.json().get("error")
    except Exception as e:
        return False, f"Server error: {str(e)}"


def remove_employee_logic(name):
    try:
        response = requests.delete(f"{SERVER_URL}/employees/{name}")
        if response.status_code == 200:
            return True, response.json().get("message")
        else:
            return False, response.json().get("error")
    except Exception as e:
        return False, f"Server error: {str(e)}"


def save_formula(data):
    try:
        response = requests.post(f"{SERVER_URL}/formulas", json=data)
        return response.status_code == 200
    except:
        return False


# --- GUI Application Class ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Produção")
        self.root.geometry("400x300")
        
        create_databases()
        self.employees = get_employees()

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
    
    # --- New Formula Window Logic (Modified) ---
    def show_formulas_window(self):
        """Hides the main window and shows a new Toplevel window for formula input."""
        # Hide the main window
        self.root.withdraw()
        
        self.formulas_win = tk.Toplevel(self.root)
        self.formulas_win.title("Adicionar Formulas")
        self.formulas_win.geometry("450x600")
        
        # Define what happens when the window is closed
        self.formulas_win.protocol("WM_DELETE_WINDOW", self.on_formulas_window_close)
        
        main_frame = tk.Frame(self.formulas_win, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # NR da Formula
        tk.Label(main_frame, text="NR da Formula:", font=("Helvetica", 12)).pack(pady=5)
        self.nr_entry = tk.Entry(main_frame, width=30)
        self.nr_entry.pack(pady=5)
        
        # Tipo de Formula
        tk.Label(main_frame, text="Tipo de Formula:", font=("Helvetica", 12)).pack(pady=5)
        formula_types = ["Cápsulas", "Sachês", "Sub-Lingual/Cápsulas Oleosas", "Semi-Sólidos", "Líquidos Orais"]
        self.formula_type_var = tk.StringVar(self.formulas_win)
        self.formula_type_dropdown = ttk.Combobox(main_frame, textvariable=self.formula_type_var, values=formula_types, state="readonly")
        self.formula_type_dropdown.pack(pady=5)
        self.formula_type_dropdown.set(formula_types[0])
        
        # Funcionario Pesagem (Farmaceutico)
        tk.Label(main_frame, text="Funcionario Pesagem:", font=("Helvetica", 12)).pack(pady=5)
        farmaceuticos = [name for name, details in self.employees.items()]
        self.pesagem_var = tk.StringVar(self.formulas_win)
        self.pesagem_dropdown = ttk.Combobox(main_frame, textvariable=self.pesagem_var, values=farmaceuticos, state="readonly")
        self.pesagem_dropdown.pack(pady=5)
        
        # Funcionario Manipulacao
        tk.Label(main_frame, text="Funcionario Manipulacao:", font=("Helvetica", 12)).pack(pady=5)
        all_employees = list(self.employees.keys())
        self.manipulacao_var = tk.StringVar(self.formulas_win)
        self.manipulacao_dropdown = ttk.Combobox(main_frame, textvariable=self.manipulacao_var, values=all_employees, state="readonly")
        self.manipulacao_dropdown.pack(pady=5)
        
        # Funcionario PM
        tk.Label(main_frame, text="Funcionario PM:", font=("Helvetica", 12)).pack(pady=5)
        self.pm_var = tk.StringVar(self.formulas_win)
        self.pm_dropdown = ttk.Combobox(main_frame, textvariable=self.pm_var, values=all_employees, state="readonly")
        self.pm_dropdown.pack(pady=5)

        # Checkboxes
        self.refeito_pm_var = tk.BooleanVar()
        self.refeito_exc_var = tk.BooleanVar()
        self.estoque_usado_var = tk.BooleanVar()
        self.estoque_feito_var = tk.BooleanVar()

        refeito_frame = tk.Frame(main_frame)
        refeito_frame.pack(pady=10)
        
        estoque_frame = tk.Frame(main_frame)
        estoque_frame.pack(pady=5)
        
        new_checkbox_frame = tk.Frame(main_frame)
        new_checkbox_frame.pack(pady=5)

        tk.Checkbutton(refeito_frame, text="Refeito PM", variable=self.refeito_pm_var, font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(refeito_frame, text="Refeito EXC", variable=self.refeito_exc_var, font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
        
        tk.Checkbutton(estoque_frame, text="Estoque Usado", variable=self.estoque_usado_var, font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(estoque_frame, text="Estoque Feito", variable=self.estoque_feito_var, font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
        
        # New "Refeito Semi-Sólidos" Checkbox
        
        # Save Button
        save_button = tk.Button(main_frame, text="Salvar Formula", command=self.save_formula_data)
        save_button.pack(pady=20)
    
    def save_formula_data(self):
        """Gathers data from the form and saves it. Resets the form for the next entry."""
        nr = self.nr_entry.get().strip()
        formula_type = self.formula_type_var.get()
        funcionario_pesagem = self.pesagem_var.get()
        funcionario_manipulacao = self.manipulacao_var.get()
        funcionario_pm = self.pm_var.get()
        refeito_pm = self.refeito_pm_var.get()
        refeito_exc = self.refeito_exc_var.get()
        estoque_usado = self.estoque_usado_var.get()
        estoque_feito = self.estoque_feito_var.get()

        if not nr or not formula_type or not funcionario_pesagem or not funcionario_manipulacao or not funcionario_pm:
            messagebox.showerror("Validation Error", "Please fill in all fields.")
            return

        try:
            nr = int(nr)
        except ValueError:
            messagebox.showerror("Validation Error", "NR must be a number.")
            return

        formula_data = {
            "date": datetime.date.today().isoformat(),
            "time": datetime.datetime.now().strftime("%H:%M"),
            "nr": nr,
            "tipo_formula": formula_type,
            "funcionario_pesagem": funcionario_pesagem,
            "funcionario_manipulacao": funcionario_manipulacao,
            "funcionario_pm": funcionario_pm,
            "refeito_pm": refeito_pm,
            "refeito_exc": refeito_exc,
            "estoque_usado": estoque_usado,
            "estoque_feito": estoque_feito,
        }

        save_formula(formula_data)
        messagebox.showinfo("Success", "Formula saved successfully! You can now add another.")
        
        # Reset all form fields for the next entry
        self.nr_entry.delete(0, tk.END)
        self.pesagem_var.set('')
        self.manipulacao_var.set('')
        self.pm_var.set('')
        self.refeito_pm_var.set(False)
        self.refeito_exc_var.set(False)
        self.estoque_usado_var.set(False)
        self.estoque_feito_var.set(False)
        self.nr_entry.focus_set()

    def on_formulas_window_close(self):
        """Handles the window close event to unhide the main menu."""
        self.formulas_win.destroy()
        self.root.deiconify()

    def show_add_employee_window(self):
        """Displays the 'Cadastrar Funcionario' window with Farmaceutico checkbox."""
        add_win = tk.Toplevel(self.root)
        add_win.title("Cadastrar Funcionario")
        add_win.geometry("350x180")

        tk.Label(add_win, text="Nome do Funcionario:", font=("Helvetica", 12)).pack(pady=5)
        entry_frame = tk.Frame(add_win)
        entry_frame.pack(pady=5)

        self.add_entry = tk.Entry(entry_frame, width=22)
        self.add_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.farmaceutico_var = tk.BooleanVar()
        tk.Checkbutton(entry_frame, text="Farmaceutico", variable=self.farmaceutico_var, font=("Helvetica", 10)).pack(side=tk.LEFT)

        tk.Button(add_win, text="Cadastrar", command=lambda: self.handle_add_employee(add_win)).pack(pady=15)

    def handle_add_employee(self, window):
        """Handles the logic for adding an employee from the GUI, with Farmaceutico role."""
        name = self.add_entry.get().strip()
        is_farmaceutico = self.farmaceutico_var.get()
        
        if name:
            success, message = add_employee_logic(name, is_farmaceutico)
            if success:
                messagebox.showinfo("Success", message)
                self.employees = get_employees() 
                window.destroy()
            else:
                messagebox.showerror("Error", message)
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
        
        self.employee_var = tk.StringVar(remove_win)
        self.employee_var.set("Select...")
        self.employee_dropdown = tk.OptionMenu(remove_win, self.employee_var, *employees.keys())
        self.employee_dropdown.pack(pady=5)

        tk.Button(remove_win, text="Remover", command=lambda: self.handle_remove_employee(remove_win)).pack(pady=10)

    def handle_remove_employee(self, window):
        """Handles the logic for removing an employee from the GUI."""
        name = self.employee_var.get()
        if name and name != "Select...":
            success, message = remove_employee_logic(name)
            if success:
                messagebox.showinfo("Success", message)
                self.employees = get_employees() 
                window.destroy()
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showerror("Error", "Please select an employee.")

if __name__ == "__main__":
    # Create an example funcionarios.json for demonstration if it doesn't exist
    if not os.path.exists(DATABASE_FILE):
        example_employees = {}
        with open(DATABASE_FILE, 'w') as f:
            json.dump(example_employees, f, indent=4)
            
    root = tk.Tk()
    app = App(root)
    root.mainloop()