import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime

# --- Configuration ---
DATABASE_FILE = "funcionarios.json"
FORMULAS_FILE = "formulas.json"
LOGO_FILE = "logo.png"

# -------------------------
# JSON HELPERS
# -------------------------

def load_json(filename, default_value):
    if not os.path.exists(filename):
        save_json(filename, default_value)
        return default_value
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_value

def save_json(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(e)
        return False

def get_employees():
    return load_json(DATABASE_FILE, {})

def add_employee_logic(name, is_farmaceutico):
    employees = get_employees()

    if name in employees:
        return False, "Funcionário já existe."

    role = "Farmaceutico" if is_farmaceutico else "Operador"
    employees[name] = {"role": role}

    if save_json(DATABASE_FILE, employees):
        return True, f"Funcionário {name} cadastrado!"
    return False, "Erro ao salvar."

def remove_employee_logic(name):
    employees = get_employees()

    if name in employees:
        del employees[name]
        if save_json(DATABASE_FILE, employees):
            return True, "Funcionário removido."
        return False, "Erro ao salvar."

    return False, "Funcionário não encontrado."

def save_formula_logic(formula_data):
    formulas = load_json(FORMULAS_FILE, [])
    formulas.append(formula_data)
    return save_json(FORMULAS_FILE, formulas)


# -------------------------
# APP
# -------------------------

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Produção (Modo Local)")
        self.root.geometry("450x650") # Adjusted height for logo + buttons

        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack(expand=True)

        # --- LOGO SECTION ---
        if os.path.exists(LOGO_FILE):
            try:
                self.logo_img = tk.PhotoImage(file=LOGO_FILE)
                self.logo_label = tk.Label(self.main_frame, image=self.logo_img)
                self.logo_label.pack(pady=(0, 10))
            except Exception as e:
                print(f"Error loading logo: {e}")

        tk.Label(self.main_frame, text="Modo: Arquivos Locais",
                 fg="blue", font=("Arial", 8)).pack()

        tk.Label(self.main_frame, text="Selecione uma opção:",
                 font=("Helvetica", 16, "bold")).pack(pady=10)

        # --- MAIN BUTTONS ---
        
        # 1. Add Formula
        tk.Button(self.main_frame, text="Adicionar Formulas",
                  width=25, command=self.show_formulas_window).pack(pady=5)
        
        # 2. Add Employee
        tk.Button(self.main_frame, text="Cadastrar Funcionario", 
                  width=25, command=self.show_add_employee_window).pack(pady=5)

        # 3. Remove Employee
        tk.Button(self.main_frame, text="Remover Funcionario", 
                  width=25, command=self.show_remove_employee_window).pack(pady=5)

        # Load employees into memory on start
        self.employees = get_employees()

    # -------------------------
    # FORMULAS WINDOW
    # -------------------------

    def show_formulas_window(self):
        self.root.withdraw()

        self.formulas_win = tk.Toplevel(self.root)
        self.formulas_win.title("Adicionar Formula")
        self.formulas_win.geometry("450x800")
        self.formulas_win.protocol("WM_DELETE_WINDOW", self.on_formulas_window_close)

        main_frame = tk.Frame(self.formulas_win, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Date
        tk.Label(main_frame, text="Data (YYYY-MM-DD) [Vazio = Hoje]:").pack()
        self.date_entry = tk.Entry(main_frame, width=30)
        self.date_entry.pack(pady=5)

        # TURN SECTION (From your newer version)
        tk.Label(main_frame, text="Turno:", font=("Helvetica", 12)).pack(pady=5)

        self.turno_var = tk.StringVar(value="manha")

        turno_frame = tk.Frame(main_frame)
        turno_frame.pack()

        tk.Radiobutton(turno_frame, text="Manhã",
                       variable=self.turno_var,
                       value="manha").pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(turno_frame, text="Tarde",
                       variable=self.turno_var,
                       value="tarde").pack(side=tk.LEFT, padx=10)

        # NR
        tk.Label(main_frame, text="NR da Formula:").pack(pady=5)
        self.nr_entry = tk.Entry(main_frame, width=30)
        self.nr_entry.pack()

        # Tipo
        tk.Label(main_frame, text="Tipo de Formula:").pack(pady=5)
        formula_types = ["Cápsulas", "Sachês",
                         "Sub-Lingual/Cápsulas Oleosas",
                         "Semi-Sólidos", "Líquidos Orais"]

        self.formula_type_var = tk.StringVar()
        dropdown = ttk.Combobox(main_frame,
                                textvariable=self.formula_type_var,
                                values=formula_types,
                                state="readonly")
        dropdown.pack()
        dropdown.set(formula_types[0])

        # Employees (Refresh list when opening window)
        self.employees = get_employees()
        employee_names = list(self.employees.keys())

        tk.Label(main_frame, text="Funcionario Pesagem:").pack(pady=5)
        self.pesagem_var = tk.StringVar()
        ttk.Combobox(main_frame,
                     textvariable=self.pesagem_var,
                     values=employee_names,
                     state="readonly").pack()

        tk.Label(main_frame, text="Funcionario Manipulação:").pack(pady=5)
        self.manipulacao_var = tk.StringVar()
        ttk.Combobox(main_frame,
                     textvariable=self.manipulacao_var,
                     values=employee_names,
                     state="readonly").pack()

        tk.Label(main_frame, text="Funcionario PM:").pack(pady=5)
        self.pm_var = tk.StringVar()
        ttk.Combobox(main_frame,
                     textvariable=self.pm_var,
                     values=employee_names,
                     state="readonly").pack()

        # FLAGS
        self.refeito_pm_var = tk.BooleanVar()
        self.refeito_exc_var = tk.BooleanVar()
        self.estoque_usado_var = tk.BooleanVar()
        self.estoque_feito_var = tk.BooleanVar()
        self.pm_plus_20_var = tk.BooleanVar()

        refeito_frame = tk.Frame(main_frame)
        refeito_frame.pack(pady=10)

        tk.Checkbutton(refeito_frame,
                       text="Refeito PM",
                       variable=self.refeito_pm_var).pack(side=tk.LEFT, padx=10)

        tk.Checkbutton(refeito_frame,
                       text="Refeito EXC",
                       variable=self.refeito_exc_var).pack(side=tk.LEFT, padx=10)

        tk.Checkbutton(main_frame,
                       text="PM +20",
                       variable=self.pm_plus_20_var).pack(pady=5)

        estoque_frame = tk.Frame(main_frame)
        estoque_frame.pack(pady=5)

        tk.Checkbutton(estoque_frame,
                       text="Estoque Usado",
                       variable=self.estoque_usado_var).pack(side=tk.LEFT, padx=10)

        tk.Checkbutton(estoque_frame,
                       text="Estoque Feito",
                       variable=self.estoque_feito_var).pack(side=tk.LEFT, padx=10)

        tk.Button(main_frame, text="Salvar Formula",
                  command=self.save_formula_data).pack(pady=20)

    def save_formula_data(self):
        nr = self.nr_entry.get().strip()
        pesagem = self.pesagem_var.get()
        manipulacao = self.manipulacao_var.get()

        if not nr or not pesagem or not manipulacao:
            messagebox.showerror("Erro", "Preencha NR, Pesagem e Manipulação.")
            return

        try:
            nr = int(nr)
        except:
            messagebox.showerror("Erro", "NR deve ser número.")
            return

        manual_date = self.date_entry.get().strip()
        final_date = datetime.date.today().isoformat()

        if manual_date:
            try:
                datetime.datetime.strptime(manual_date, '%Y-%m-%d')
                final_date = manual_date
            except:
                messagebox.showerror("Erro", "Data inválida.")
                return

        formula_data = {
            "date": final_date,
            "nr": nr,
            "turno": self.turno_var.get(),  # Capturing the Shift
            "tipo_formula": self.formula_type_var.get(),
            "funcionario_pesagem": pesagem,
            "funcionario_manipulacao": manipulacao,
            "funcionario_pm": self.pm_var.get(),
            "refeito_pm": self.refeito_pm_var.get(),
            "refeito_exc": self.refeito_exc_var.get(),
            "estoque_usado": self.estoque_usado_var.get(),
            "estoque_feito": self.estoque_feito_var.get(),
            "pm_mais_20": self.pm_plus_20_var.get()
        }

        if save_formula_logic(formula_data):
            messagebox.showinfo("Sucesso", "Fórmula salva!")
            self.nr_entry.delete(0, tk.END)

    def on_formulas_window_close(self):
        self.formulas_win.destroy()
        self.root.deiconify()

    # -------------------------
    # EMPLOYEE MANAGEMENT WINDOWS
    # -------------------------

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
                messagebox.showinfo("Sucesso", message)
                self.employees = get_employees() 
                window.destroy()
            else:
                messagebox.showerror("Erro", message)
        else:
            messagebox.showerror("Erro", "Nome não pode estar vazio.")

    def show_remove_employee_window(self):
        remove_win = tk.Toplevel(self.root)
        remove_win.title("Remover Funcionario")
        remove_win.geometry("300x200")
        
        # Refresh list
        self.employees = get_employees()

        if not self.employees:
            tk.Label(remove_win, text="Sem funcionários cadastrados.", font=("Helvetica", 12)).pack(pady=20)
            return

        tk.Label(remove_win, text="Selecione o funcionario:", font=("Helvetica", 12)).pack(pady=5)
        
        self.remove_var = tk.StringVar(remove_win)
        self.remove_var.set("Selecione...")
        options = list(self.employees.keys())
        self.employee_dropdown = tk.OptionMenu(remove_win, self.remove_var, *options)
        self.employee_dropdown.pack(pady=5)

        tk.Button(remove_win, text="Remover", command=lambda: self.handle_remove_employee(remove_win)).pack(pady=10)

    def handle_remove_employee(self, window):
        name = self.remove_var.get()
        if name and name != "Selecione...":
            success, message = remove_employee_logic(name)
            if success:
                messagebox.showinfo("Sucesso", message)
                self.employees = get_employees() 
                window.destroy()
            else:
                messagebox.showerror("Erro", message)
        else:
            messagebox.showerror("Erro", "Selecione um funcionário.")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()