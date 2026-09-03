from pathlib import Path
from sqlalchemy import text
from connection import get_engine


SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def init_db():
    engine=get_engine()
    schema_sql = SCHEMA_PATH.read_text()
    with engine.begin() as conn:
        conn.execute(text(schema_sql))
        print(f"Schema applied sucesfully from {SCHEMA_PATH.name}")

if __name__== "__main__":
    init_db()