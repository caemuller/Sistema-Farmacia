import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime

# --- File Management Functions ---
EMPLOYEES_FILE = "funcionarios_julia.json"
DATA_FILE = "data_julia.json"
ERROR_TYPES_FILE = "tipos_erro.json"
LOGO_FILE = "logo.png"

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

# --- Search Logic ---
def search_by_nr(target_nr):
    """Searches for records matching the NR."""
    try:
        with open(DATA_FILE, 'r') as f:
            records = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
    # Filter records where NR matches
    # converting to str to ensure match even if saved as int
    return [r for r in records if str(r.get('nr')) == str(target_nr)]

# --- GUI Application Class ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Erros de Produção")
        self.root.geometry("450x650") 
        
        create_databases()
        self.employees = get_employees()

        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # ================= LOGO =================
        if os.path.exists(LOGO_FILE):
            try:
                self.logo_image = tk.PhotoImage(file=LOGO_FILE)
                self.logo_label = tk.Label(self.main_frame, image=self.logo_image)
                self.logo_label.pack(pady=(0, 10))
            except Exception:
                tk.Label(self.main_frame, text="[Logo Error]", fg="red").pack()
        else:
            tk.Label(self.main_frame, text="(Logo ausente)", fg="gray", font=("Helvetica", 8)).pack(pady=(0, 10))
        # ========================================

        self.title_label = tk.Label(self.main_frame, text="Menu Principal", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

        # 1. Adicionar Erro
        self.btn_add_error = tk.Button(self.main_frame, text="Adicionar Erro", width=30, bg="#dddddd", height=2, command=self.show_add_error_window)
        self.btn_add_error.pack(pady=5)

        # 2. Consultar NR (NEW BUTTON)
        self.btn_search = tk.Button(self.main_frame, text="Consultar NR", width=30, bg="#b3e5fc", height=2, command=self.show_search_input_window)
        self.btn_search.pack(pady=5)

        tk.Frame(self.main_frame, height=10).pack() # Spacer

        # 3. Cadastrar Tipo de Erro
        self.btn_add_type = tk.Button(self.main_frame, text="Cadastrar Tipo de Erro", width=30, command=self.show_add_type_window)
        self.btn_add_type.pack(pady=5)

        # 4. Excluir Tipo de Erro
        self.btn_rem_type = tk.Button(self.main_frame, text="Excluir Tipo de Erro", width=30, command=self.show_remove_type_window)
        self.btn_rem_type.pack(pady=5)

        tk.Frame(self.main_frame, height=10).pack() # Spacer

        # 5. Cadastrar Funcionario
        self.btn_add_employee = tk.Button(self.main_frame, text="Cadastrar Funcionario", width=30, command=self.show_add_employee_window)
        self.btn_add_employee.pack(pady=5)

        # 6. Remover Funcionario
        self.btn_remove_employee = tk.Button(self.main_frame, text="Remover Funcionario", width=30, command=self.show_remove_employee_window)
        self.btn_remove_employee.pack(pady=5)
    
    # ==========================================
    # WINDOW: Search NR
    # ==========================================
    def show_search_input_window(self):
        """Small window to input the NR to search"""
        win = tk.Toplevel(self.root)
        win.title("Consultar NR")
        win.geometry("300x150")

        tk.Label(win, text="Digite o NR:", font=("Helvetica", 12)).pack(pady=15)
        entry = tk.Entry(win, font=("Helvetica", 12))
        entry.pack(pady=5)
        entry.focus()

        def perform_search(event=None):
            nr = entry.get().strip()
            if not nr:
                messagebox.showwarning("Atenção", "Digite um NR.")
                return
            
            results = search_by_nr(nr)
            if not results:
                messagebox.showinfo("Resultado", f"Nenhum registro encontrado para o NR: {nr}")
            else:
                win.destroy() # Close input window
                self.show_search_results_window(nr, results)

        # Bind Enter key to search as well
        win.bind('<Return>', perform_search)
        tk.Button(win, text="Buscar", command=perform_search, bg="#2196F3", fg="white").pack(pady=10)

    def show_search_results_window(self, nr, results):
        """Displays the details of the found NR(s)"""
        res_win = tk.Toplevel(self.root)
        res_win.title(f"Detalhes do NR: {nr}")
        res_win.geometry("500x600")

        # Scrollable Text Area
        txt = tk.Text(res_win, padx=10, pady=10, font=("Helvetica", 10))
        scrollbar = tk.Scrollbar(res_win, command=txt.yview)
        txt.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Format and insert data
        for i, data in enumerate(results):
            txt.insert(tk.END, f"=== REGISTRO {i+1} ===\n", "header")
            txt.insert(tk.END, f"Data/Hora: {data.get('date')} às {data.get('time')}\n")
            txt.insert(tk.END, f"Funcionário: {data.get('funcionario')}\n")
            
            # Format Value
            val = data.get('valor', 0)
            txt.insert(tk.END, f"Valor: R$ {val:.2f}\n")
            
            # Error Types
            types = data.get('tipos_erro', [])
            if isinstance(types, list):
                types_str = ", ".join(types)
            else:
                types_str = str(types)
            txt.insert(tk.END, f"Tipos de Erro: {types_str}\n\n")

            # --- Checkbox Solutions (Only True ones) ---
            txt.insert(tk.END, "Solução / Detalhes:\n", "subheader")
            solutions = []
            
            # Map internal keys to readable labels
            bool_map = {
                "desconto": "Desconto",
                "cobrado": "Cobrado",
                "acrescimo": "Acréscimo",
                "deixado_credito": "Deixado de Crédito",
                "reaproveitamento": "Reaproveitamento",
                "nao_mudou_valor": "Não mudou valor",
                "produto_refeito": "Produto Refeito"
            }

            for key, label in bool_map.items():
                if data.get(key) is True:
                    solutions.append(f"• {label}")
            
            if solutions:
                txt.insert(tk.END, "\n".join(solutions) + "\n\n")
            else:
                txt.insert(tk.END, "• Nenhuma opção selecionada\n\n")

            # Observations
            obs = data.get('observacoes', '')
            txt.insert(tk.END, f"OBS:\n{obs}\n")
            txt.insert(tk.END, "-"*50 + "\n\n")

        # Styles
        txt.tag_config("header", font=("Helvetica", 12, "bold"), background="#eeeeee")
        txt.tag_config("subheader", font=("Helvetica", 10, "bold", "underline"))
        
        # Make read-only
        txt.config(state=tk.DISABLED)

    # ==========================================
    # WINDOW: Adicionar Erro 
    # ==========================================
    def show_add_error_window(self):
        self.root.withdraw()
        
        self.error_win = tk.Toplevel(self.root)
        self.error_win.title("Registrar Erro")
        self.error_win.geometry("500x750") 
        self.error_win.protocol("WM_DELETE_WINDOW", lambda: self.on_subwindow_close(self.error_win))
        
        main_frame = tk.Frame(self.error_win, padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. NR Field
        tk.Label(main_frame, text="NR:", font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.nr_entry = tk.Entry(main_frame)
        self.nr_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 2. Tipos de Erro (LISTBOX MULTIPLE)
        tk.Label(main_frame, text="Tipos de Erro (Selecione um ou mais):", font=("Helvetica", 11, "bold")).pack(anchor="w")
        
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.X, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.error_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=5, yscrollcommand=scrollbar.set, exportselection=False)
        self.error_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.config(command=self.error_listbox.yview)

        error_types = get_error_types()
        for err in error_types:
            self.error_listbox.insert(tk.END, err)

        if not error_types:
            self.error_listbox.insert(tk.END, "Nenhum tipo cadastrado")
            self.error_listbox.config(state=tk.DISABLED)
        
        # 3. Funcionario (Dropdown)
        tk.Label(main_frame, text="Funcionário (Quem errou):", font=("Helvetica", 11, "bold")).pack(anchor="w")
        employees_list = list(get_employees().keys())
        self.func_var = tk.StringVar(self.error_win)
        self.func_dropdown = ttk.Combobox(main_frame, textvariable=self.func_var, values=employees_list, state="readonly")
        self.func_dropdown.pack(fill=tk.X, pady=(0, 10))
        
        # 4. Valor (Float)
        tk.Label(main_frame, text="Valor (R$):", font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.valor_entry = tk.Entry(main_frame)
        self.valor_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 5. Checkboxes 
        tk.Label(main_frame, text="Detalhes:", font=("Helvetica", 11, "bold")).pack(anchor="w")

        self.desconto_var = tk.BooleanVar()
        self.cobrado_var = tk.BooleanVar()
        self.acrescimo_var = tk.BooleanVar()
        self.deixado_credito_var = tk.BooleanVar()
        self.reaproveitamento_var = tk.BooleanVar()
        self.nao_mudou_valor_var = tk.BooleanVar()
        self.produto_refeito_var = tk.BooleanVar()

        chk_container = tk.Frame(main_frame)
        chk_container.pack(fill=tk.X, pady=5)

        # Column 1
        c1 = tk.Frame(chk_container)
        c1.pack(side=tk.LEFT, fill=tk.Y, expand=True, anchor="n")
        tk.Checkbutton(c1, text="Desconto", variable=self.desconto_var).pack(anchor="w")
        tk.Checkbutton(c1, text="Cobrado", variable=self.cobrado_var).pack(anchor="w")
        tk.Checkbutton(c1, text="Acréscimo", variable=self.acrescimo_var).pack(anchor="w")
        tk.Checkbutton(c1, text="Não mudou valor", variable=self.nao_mudou_valor_var).pack(anchor="w")

        # Column 2
        c2 = tk.Frame(chk_container)
        c2.pack(side=tk.LEFT, fill=tk.Y, expand=True, anchor="n")
        tk.Checkbutton(c2, text="Deixado de Crédito", variable=self.deixado_credito_var).pack(anchor="w")
        tk.Checkbutton(c2, text="Reaproveitamento", variable=self.reaproveitamento_var).pack(anchor="w")
        tk.Checkbutton(c2, text="Produto Refeito", variable=self.produto_refeito_var).pack(anchor="w")

        # 6. OBS (Text Box)
        tk.Label(main_frame, text="OBS:", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(10, 0))
        self.obs_text = tk.Text(main_frame, height=4, width=50)
        self.obs_text.pack(fill=tk.X, pady=(0, 10))

        # Save Button
        save_button = tk.Button(main_frame, text="Salvar Registro", bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), command=self.save_error_data)
        save_button.pack(pady=15, fill=tk.X)
    
    def save_error_data(self):
        nr = self.nr_entry.get().strip()
        func = self.func_var.get()
        valor_str = self.valor_entry.get().strip()
        
        selected_indices = self.error_listbox.curselection()
        selected_errors = [self.error_listbox.get(i) for i in selected_indices]
        
        obs_content = self.obs_text.get("1.0", tk.END).strip()

        if not nr or not func or not valor_str:
            messagebox.showerror("Erro", "Preencha NR, Funcionário e Valor.")
            return

        if not selected_errors or (len(selected_errors) == 1 and selected_errors[0] == "Nenhum tipo cadastrado"):
            messagebox.showerror("Erro", "Selecione pelo menos um Tipo de Erro.")
            return

        try:
            valor_str = valor_str.replace(",", ".")
            valor_float = float(valor_str)
        except ValueError:
            messagebox.showerror("Erro", "O campo Valor deve ser numérico.")
            return

        record = {
            "date": datetime.date.today().isoformat(),
            "time": datetime.datetime.now().strftime("%H:%M"),
            "nr": nr,
            "tipos_erro": selected_errors,
            "funcionario": func,
            "valor": valor_float,
            "desconto": self.desconto_var.get(),
            "cobrado": self.cobrado_var.get(),
            "acrescimo": self.acrescimo_var.get(),
            "deixado_credito": self.deixado_credito_var.get(),
            "reaproveitamento": self.reaproveitamento_var.get(),
            "nao_mudou_valor": self.nao_mudou_valor_var.get(),
            "produto_refeito": self.produto_refeito_var.get(),
            "observacoes": obs_content
        }

        save_error_record(record)
        messagebox.showinfo("Sucesso", "Erro registrado com sucesso!")
        
        self.nr_entry.delete(0, tk.END)
        self.valor_entry.delete(0, tk.END)
        self.obs_text.delete("1.0", tk.END)
        self.error_listbox.selection_clear(0, tk.END)
        
        self.desconto_var.set(False)
        self.cobrado_var.set(False)
        self.acrescimo_var.set(False)
        self.deixado_credito_var.set(False)
        self.reaproveitamento_var.set(False)
        self.nao_mudou_valor_var.set(False)
        self.produto_refeito_var.set(False)
        
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
    # EMPLOYEE WINDOWS
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