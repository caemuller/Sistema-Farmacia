import json
import random
from datetime import datetime, timedelta

# Original template fields
tipo_formulas = [
    "Cápsulas",
    "Semi-Sólidos",
    "Sub-Lingual/Cápsulas Oleosas",
    "Líquidos Orais"
]

employees = ["Alice", "Bob", "Charlie", "Dani", "David", "Tati", "cae"]

# Date range: from 6 months before 2025-09-15
end_date = datetime(2025, 9, 15)
start_date = end_date - timedelta(days=180)

def random_date():
    return start_date + timedelta(days=random.randint(0, 180))

def generate_entry(nr_base):
    return {
        "date": random_date().strftime("%Y-%m-%d"),
        "horario": f"{random.randint(7, 18):02}:{random.randint(0, 59):02}",
        "nr": nr_base + random.randint(1, 1000000),
        "tipo_formula": random.choice(tipo_formulas),
        "funcionario_pesagem": random.choice(employees),
        "funcionario_manipulacao": random.choice(employees),
        "funcionario_pm": random.choice(employees),
        "refeito_pm": random.choice([True, False, False]),  # more likely to be False
        "refeito_exc": random.choice([True, False, False]),
        "estoque_usado": random.choice([True, False]),
        "estoque_feito": random.choice([True, False])
    }

# Generate 300+ fake entries
fake_data = [generate_entry(nr_base=1000000) for _ in range(900)]


full_data = fake_data 

with open("fake_data.json", "w", encoding="utf-8") as f:
    json.dump(full_data, f, ensure_ascii=False, indent=4)

print(f"✅ Generated {len(full_data)} fake records and saved to fake_data.json")
