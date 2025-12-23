import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime

# --- File Management Functions ---
EMPLOYEES_FILE = "funcionarios_julia.json"
DATA_FILE = "data_julia.json"
ERROR_TYPES_FILE = "tipos_erro.json"

def create_databases():
    """Ensures the JSON files exist."""
    files_to_init = {
        EMPLOYEES_FILE: {},
        DATA_FILE: [],
        ERROR_TYPES_FILE: []
    }

    for file_path, default_data in files_to_init.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump(default_data, f, indent=4)

# --- Employee Logic ---
def get_employees():
    try:
        with open(EMPLOYEES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def add_employee_logic(name, is_farmaceutico):
    employees = get_employees()
    if name in employees:
        return False, f"Erro: Funcionário '{name}' já existe."
    else:
        employee_data = {"name": name}
        if is_farmaceutico:
            employee_data["role"] = "Farmaceutico"
        employees[name] = employee_data
        with open(EMPLOYEES_FILE, 'w') as f:
            json.dump(employees, f, indent=4)
        return True, f"Funcionário '{name}' adicionado com sucesso."

def remove_employee_logic(name):
    employees = get_employees()
    if name not in employees:
        return False, f"Erro: Funcionário '{name}' não encontrado."
    else:
        del employees[name]
        with open(EMPLOYEES_FILE, 'w') as f:
            json.dump(employees, f, indent=4)
        return True, f"Funcionário '{name}' removido com sucesso."

# --- Error Types Logic ---
def get_error_types():
    try:
        with open(ERROR_TYPES_FILE, 'r') as f:
            data = json.load(f)
            # Ensure it's a list (handle case where file might be corrupted or init as dict)
            if isinstance(data, list):
                return data
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def add_error_type_logic(error_name):
    errors = get_error_types()
    if error_name in errors:
        return False, f"Erro: Tipo de erro '{error_name}' já existe."
    
    errors.append(error_name)
    with open(ERROR_TYPES_FILE, 'w') as f:
        json.dump(errors, f, indent=4)
    return True, f"Tipo de erro '{error_name}' cadastrado."

def remove_error_type_logic(error_name):
    errors = get_error_types()
    if error_name not in errors:
        return False, f"Erro: Tipo de erro '{error_name}' não encontrado."
    
    errors.remove(error_name)
    with open(ERROR_TYPES_FILE, 'w') as f:
        json.dump(errors, f, indent=4)
    return True, f"Tipo de erro '{error_name}' excluído."

# --- Save Error Record Logic ---
def save_error_record(data):
    """Saves the error record to data_julia.json."""
    create_databases()
    try:
        with open(DATA_FILE, 'r') as f:
            records = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        records = []

    records.append(data)

    with open(DATA_FILE, 'w') as f:
        json.dump(records, f, indent=4)

# --- GUI Application Class ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Erros de Produção")
        self.root.geometry("450x450") # Increased height for more buttons
        
        create_databases()
        self.employees = get_employees()

        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack(expand=True)

        self.title_label = tk.Label(self.main_frame, text="Menu Principal", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

        # 1. Adicionar Erro
        self.btn_add_error = tk.Button(self.main_frame, text="Adicionar Erro", width=30, bg="#dddddd", command=self.show_add_error_window)
        self.btn_add_error.pack(pady=5)

        tk.Frame(self.main_frame, height=10).pack() # Spacer

        # 2. Cadastrar Tipo de Erro
        self.btn_add_type = tk.Button(self.main_frame, text="Cadastrar Tipo de Erro", width=30, command=self.show_add_type_window)
        self.btn_add_type.pack(pady=5)

        # 3. Excluir Tipo de Erro
        self.btn_rem_type = tk.Button(self.main_frame, text="Excluir Tipo de Erro", width=30, command=self.show_remove_type_window)
        self.btn_rem_type.pack(pady=5)

        tk.Frame(self.main_frame, height=10).pack() # Spacer

        # 4. Cadastrar Funcionario
        self.btn_add_employee = tk.Button(self.main_frame, text="Cadastrar Funcionario", width=30, command=self.show_add_employee_window)
        self.btn_add_employee.pack(pady=5)

        # 5. Remover Funcionario
        self.btn_remove_employee = tk.Button(self.main_frame, text="Remover Funcionario", width=30, command=self.show_remove_employee_window)
        self.btn_remove_employee.pack(pady=5)
    
    # ==========================================
    # WINDOW: Adicionar Erro (Replaces Formulas)
    # ==========================================
    def show_add_error_window(self):
        self.root.withdraw()
        
        self.error_win = tk.Toplevel(self.root)
        self.error_win.title("Registrar Erro")
        self.error_win.geometry("400x550")
        self.error_win.protocol("WM_DELETE_WINDOW", lambda: self.on_subwindow_close(self.error_win))
        
        main_frame = tk.Frame(self.error_win, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. NR Field
        tk.Label(main_frame, text="NR:", font=("Helvetica", 11)).pack(anchor="w")
        self.nr_entry = tk.Entry(main_frame)
        self.nr_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 2. Tipo de Erro (Dropdown)
        tk.Label(main_frame, text="Tipo de Erro:", font=("Helvetica", 11)).pack(anchor="w")
        error_types = get_error_types()
        self.error_type_var = tk.StringVar(self.error_win)
        self.error_type_dropdown = ttk.Combobox(main_frame, textvariable=self.error_type_var, values=error_types, state="readonly")
        self.error_type_dropdown.pack(fill=tk.X, pady=(0, 10))
        if not error_types:
            self.error_type_dropdown.set("Nenhum tipo cadastrado")
        
        # 3. Funcionario (Dropdown)
        tk.Label(main_frame, text="Funcionário (Quem errou):", font=("Helvetica", 11)).pack(anchor="w")
        employees_list = list(get_employees().keys())
        self.func_var = tk.StringVar(self.error_win)
        self.func_dropdown = ttk.Combobox(main_frame, textvariable=self.func_var, values=employees_list, state="readonly")
        self.func_dropdown.pack(fill=tk.X, pady=(0, 10))
        
        # 4. Valor (Float)
        tk.Label(main_frame, text="Valor (R$):", font=("Helvetica", 11)).pack(anchor="w")
        self.valor_entry = tk.Entry(main_frame)
        self.valor_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 5. Checkboxes (Desconto / Cobrado)
        self.desconto_var = tk.BooleanVar()
        self.cobrado_var = tk.BooleanVar()

        chk_frame = tk.Frame(main_frame)
        chk_frame.pack(pady=10, fill=tk.X)
        
        tk.Checkbutton(chk_frame, text="Desconto", variable=self.desconto_var, font=("Helvetica", 11)).pack(side=tk.LEFT, padx=(0, 20))
        tk.Checkbutton(chk_frame, text="Cobrado", variable=self.cobrado_var, font=("Helvetica", 11)).pack(side=tk.LEFT)

        # Save Button
        save_button = tk.Button(main_frame, text="Salvar Registro", bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"), command=self.save_error_data)
        save_button.pack(pady=20, fill=tk.X)
    
    def save_error_data(self):
        nr = self.nr_entry.get().strip()
        err_type = self.error_type_var.get()
        func = self.func_var.get()
        valor_str = self.valor_entry.get().strip()
        
        # Validation
        if not nr or not err_type or not func or not valor_str:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        if err_type == "Nenhum tipo cadastrado":
            messagebox.showerror("Erro", "Cadastre um Tipo de Erro no menu principal primeiro.")
            return

        # Float Validation (handling comma or dot)
        try:
            valor_str = valor_str.replace(",", ".")
            valor_float = float(valor_str)
        except ValueError:
            messagebox.showerror("Erro", "O campo Valor deve ser numérico.")
            return

        # Construct Data
        record = {
            "date": datetime.date.today().isoformat(),
            "time": datetime.datetime.now().strftime("%H:%M"),
            "nr": nr,
            "tipo_erro": err_type,
            "funcionario": func,
            "valor": valor_float,
            "desconto": self.desconto_var.get(),
            "cobrado": self.cobrado_var.get()
        }

        save_error_record(record)
        messagebox.showinfo("Sucesso", "Erro registrado com sucesso!")
        
        # Reset Fields
        self.nr_entry.delete(0, tk.END)
        self.valor_entry.delete(0, tk.END)
        self.desconto_var.set(False)
        self.cobrado_var.set(False)
        self.nr_entry.focus_set()

    # ==========================================
    # WINDOW: Cadastrar Tipo de Erro
    # ==========================================
    def show_add_type_window(self):
        win = tk.Toplevel(self.root)
        win.title("Cadastrar Tipo de Erro")
        win.geometry("350x150")
        
        tk.Label(win, text="Nome do Tipo de Erro:", font=("Helvetica", 11)).pack(pady=10)
        entry = tk.Entry(win, width=30)
        entry.pack(pady=5)
        
        def submit():
            name = entry.get().strip()
            if name:
                success, msg = add_error_type_logic(name)
                if success:
                    messagebox.showinfo("Sucesso", msg)
                    win.destroy()
                else:
                    messagebox.showerror("Erro", msg)
            else:
                messagebox.showerror("Erro", "Nome não pode ser vazio.")

        tk.Button(win, text="Cadastrar", command=submit).pack(pady=10)

    # ==========================================
    # WINDOW: Excluir Tipo de Erro
    # ==========================================
    def show_remove_type_window(self):
        win = tk.Toplevel(self.root)
        win.title("Excluir Tipo de Erro")
        win.geometry("350x180")
        
        errors = get_error_types()
        if not errors:
            tk.Label(win, text="Nenhum tipo cadastrado.").pack(pady=20)
            return

        tk.Label(win, text="Selecione o tipo para excluir:", font=("Helvetica", 11)).pack(pady=10)
        
        selected_var = tk.StringVar(win)
        selected_var.set(errors[0])
        dropdown = tk.OptionMenu(win, selected_var, *errors)
        dropdown.pack(pady=5)

        def submit():
            name = selected_var.get()
            if messagebox.askyesno("Confirmar", f"Deseja realmente excluir '{name}'?"):
                success, msg = remove_error_type_logic(name)
                if success:
                    messagebox.showinfo("Sucesso", msg)
                    win.destroy()
                else:
                    messagebox.showerror("Erro", msg)

        tk.Button(win, text="Excluir", fg="red", command=submit).pack(pady=10)

    # ==========================================
    # EXISTING EMPLOYEE WINDOWS (Renamed Logic)
    # ==========================================
    def show_add_employee_window(self):
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
        name = self.add_entry.get().strip()
        is_farmaceutico = self.farmaceutico_var.get()
        
        if name:
            success, message = add_employee_logic(name, is_farmaceutico)
            if success:
                messagebox.showinfo("Success", message)
                window.destroy()
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showerror("Error", "Nome não pode ser vazio.")

    def show_remove_employee_window(self):
        remove_win = tk.Toplevel(self.root)
        remove_win.title("Remover Funcionario")
        remove_win.geometry("300x200")

        employees = get_employees()
        
        if not employees:
            tk.Label(remove_win, text="Nenhum funcionario para remover.", font=("Helvetica", 12)).pack(pady=20)
            return

        tk.Label(remove_win, text="Selecione o funcionario:", font=("Helvetica", 12)).pack(pady=5)
        
        self.employee_var = tk.StringVar(remove_win)
        self.employee_var.set("Selecione...")
        self.employee_dropdown = tk.OptionMenu(remove_win, self.employee_var, *employees.keys())
        self.employee_dropdown.pack(pady=5)

        tk.Button(remove_win, text="Remover", command=lambda: self.handle_remove_employee(remove_win)).pack(pady=10)

    def handle_remove_employee(self, window):
        name = self.employee_var.get()
        if name and name != "Selecione...":
            success, message = remove_employee_logic(name)
            if success:
                messagebox.showinfo("Success", message)
                window.destroy()
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showerror("Error", "Por favor selecione um funcionario.")

    def on_subwindow_close(self, window):
        window.destroy()
        self.root.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()