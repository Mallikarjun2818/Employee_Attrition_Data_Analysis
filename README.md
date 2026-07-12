# Employee Attrition Analysis Dashboard

Streamlit dashboard for analyzing employee attrition using Python, Pandas, Matplotlib, Seaborn, and optional PostgreSQL storage.

## Project Objectives Covered

1. Overall attrition rate analysis
2. Department-wise attrition analysis
3. Salary vs attrition analysis
4. Job satisfaction impact analysis
5. Work-life balance analysis
6. Experience-wise attrition analysis
7. Promotion impact on attrition analysis
8. Overtime vs attrition analysis
9. Performance rating analysis

## Files

- `app.py` - Streamlit dashboard.
- `src/analytics.py` - Reusable Pandas analysis logic.
- `data/employee_attrition_enhanced_1000.csv` - Local copy of the provided dataset.
- `database/schema.sql` - PostgreSQL table schema and indexes.
- `load_to_postgres.py` - CSV-to-PostgreSQL loader.
- `requirements.txt` - Python dependencies.

## Run the Dashboard

```powershell
pip install -r requirements.txt
streamlit run app.py
```

The app uses the CSV by default. You can also upload another CSV from the sidebar.

## Optional PostgreSQL Setup

Create a PostgreSQL database named `employee_attrition`, then load the CSV:

```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/employee_attrition"
python load_to_postgres.py
streamlit run app.py
```

In the app sidebar, choose `PostgreSQL` and enter the same database URL.
