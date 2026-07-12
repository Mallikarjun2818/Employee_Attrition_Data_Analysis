from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


DEFAULT_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/employee_attrition"
DEFAULT_CSV = Path("data/employee_attrition_enhanced_1000.csv")
SCHEMA_PATH = Path("database/schema.sql")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load employee attrition CSV into PostgreSQL.")
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="Path to the employee attrition CSV.")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
        help="SQLAlchemy PostgreSQL URL. Can also be set with DATABASE_URL.",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    df.columns = [column.lower() for column in df.columns]

    engine = create_engine(args.database_url)
    with engine.begin() as conn:
        for statement in SCHEMA_PATH.read_text(encoding="utf-8").split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
        df.to_sql("employee_attrition", conn, if_exists="append", index=False)

    print(f"Loaded {len(df)} rows into employee_attrition.")


if __name__ == "__main__":
    main()
