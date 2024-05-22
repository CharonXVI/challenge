from dataclasses import dataclass

@dataclass
class Employee:
    table_name: str = "employee"
    query: str = """
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        hire_datetime  timestamp with time zone NOT NULL,
        department_id INTEGER REFERENCES department(id),
        job_id INTEGER REFERENCES job(id)
    """