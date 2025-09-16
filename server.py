from flask import Flask, request, jsonify
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

DATABASE_FILE = "funcionarios.json"
FORMULAS_FILE = "formulas.json"

def create_databases():
    for file_path in [DATABASE_FILE, FORMULAS_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump({} if "funcionarios" in file_path else [], f)

create_databases()

@app.route("/employees", methods=["GET"])
def get_employees():
    with open(DATABASE_FILE, 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/employees", methods=["POST"])
def add_employee():
    content = request.json
    name = content.get("name")
    role = content.get("role")

    with open(DATABASE_FILE, 'r') as f:
        data = json.load(f)

    if name in data:
        return jsonify({"error": f"Employee '{name}' already exists."}), 400

    data[name] = {"name": name}
    if role == "Farmaceutico":
        data[name]["role"] = "Farmaceutico"

    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

    return jsonify({"success": True, "message": f"Employee '{name}' added."})

@app.route("/employees/<name>", methods=["DELETE"])
def remove_employee(name):
    with open(DATABASE_FILE, 'r') as f:
        data = json.load(f)

    if name not in data:
        return jsonify({"error": f"Employee '{name}' not found."}), 404

    del data[name]

    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

    return jsonify({"success": True, "message": f"Employee '{name}' removed."})

@app.route("/formulas", methods=["POST"])
def add_formula():
    content = request.json
    with open(FORMULAS_FILE, 'r') as f:
        formulas = json.load(f)

    formulas.append(content)

    with open(FORMULAS_FILE, 'w') as f:
        json.dump(formulas, f, indent=4)

    return jsonify({"success": True, "message": "Formula added."})

@app.route("/formulas", methods=["GET"])
def get_formulas():
    with open(FORMULAS_FILE, 'r') as f:
        formulas = json.load(f)
    return jsonify(formulas)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
