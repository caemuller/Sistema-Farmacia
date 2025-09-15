import os
import json
import datetime

def create_json(nr, funcionario_pesagem, funcionario_manipulacao, funcionario_pm, refeito_pm, refeito_exc):
    """
    Creates a JSON file with the provided formula data.

    Args:
        nr (int): The formula number.
        funcionario_pesagem (str): Name of the weighing employee.
        funcionario_manipulacao (str): Name of the manipulation employee.
        funcionario_pm (str): Name of the PM employee.
        refeito_pm (int): Number of times the PM was redone.
        refeito_exc (int): Number of times the excipient was redone.
    """
    date = datetime.date.today().isoformat()
    data = {
        "nr": nr,
        "funcionario_pesagem": funcionario_pesagem,
        "funcionario_manipulacao": funcionario_manipulacao,
        "funcionario_pm": funcionario_pm,
        "refeito_pm": refeito_pm,
        "refeito_exc": refeito_exc
    }

    # Ensure the directory exists
    os.makedirs("data", exist_ok=True)

    # Write to a JSON file
    formulas_file = "data/formulas.json"
    # Load existing formulas if the file exists
    if os.path.exists(formulas_file):
        with open(formulas_file, 'r') as json_file:
            formulas = json.load(json_file)
    else:
        formulas = []

    formulas.append(data)

    # Write the updated list back to the file
    with open(formulas_file, 'w') as json_file:
        json.dump(formulas, json_file, indent=4)

    print(f"Formula added to '{formulas_file}' successfully.")