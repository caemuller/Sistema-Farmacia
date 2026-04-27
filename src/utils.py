import json
import os

# --- Configurations ---
EMPLOYEES_FILE = "funcionarios.json" 
SALES_DATA_FILE = "data_julia.json"
SALES_ERROR_TYPES = "tipos_erro.json"
PROD_DATA_FILE = "formulas.json"
PROD_ERROR_DATA = "erros_producao.json" 
PROD_ERROR_TYPES = "tipos_erro_producao.json" 

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
    except:
        return False

# --- Employees ---
def get_employees():
    return load_json(EMPLOYEES_FILE, {})

def add_employee(name, is_farmaceutico, setor):
    employees = get_employees()
    if name in employees:
        return False, "Funcionário já existe."
    
    # Save role and sector
    employees[name] = {
        "role": "Farmaceutico" if is_farmaceutico else "Operador",
        "setor": setor
    }
    save_json(EMPLOYEES_FILE, employees)
    return True, "Cadastrado com sucesso!"

def remove_employee(name):
    employees = get_employees()
    if name in employees:
        del employees[name]
        save_json(EMPLOYEES_FILE, employees)
        return True, "Removido com sucesso."
    return False, "Não encontrado."

# --- Error Types ---
def get_error_types(file_path):
    return load_json(file_path, [])

def add_error_type(file_path, name):
    errors = get_error_types(file_path)
    if name not in errors:
        errors.append(name)
        save_json(file_path, errors)
        return True, "Adicionado."
    return False, "Já existe."

def remove_error_type(file_path, name):
    errors = get_error_types(file_path)
    if name in errors:
        errors.remove(name)
        save_json(file_path, errors)
        return True, "Removido."
    return False, "Não encontrado."

# --- Records Savers ---
def save_record(file_path, data):
    records = load_json(file_path, [])
    records.append(data)
    return save_json(file_path, records)

def search_by_nr(file_path, target_nr):
    records = load_json(file_path, [])
    return [r for r in records if str(r.get('nr')) == str(target_nr)]