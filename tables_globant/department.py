from dataclasses import dataclass

@dataclass
class Department:
    table_name: str = "department"
    query: str = "id SERIAL PRIMARY KEY, department VARCHAR(255) NOT NULL"