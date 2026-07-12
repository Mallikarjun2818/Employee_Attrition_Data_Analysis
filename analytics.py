from __future__ import annotations

from pathlib import Path

import pandas as pd


DATA_PATH = Path("data/employee_attrition_enhanced_1000.csv")
ATTRITION_LABELS = {1: "Yes", 0: "No"}
EXPERIENCE_BINS = [-1, 2, 5, 10, 15, 20]
EXPERIENCE_LABELS = ["0-2 years", "3-5 years", "6-10 years", "11-15 years", "16-20 years"]
SALARY_BINS = [0, 50_000, 80_000, 110_000, 140_000, 200_000]
SALARY_LABELS = ["<=50K", "50K-80K", "80K-110K", "110K-140K", "140K+"]


def load_employee_data(source: str | Path | object = DATA_PATH) -> pd.DataFrame:
    """Load and normalize the employee attrition dataset."""
    if isinstance(source, pd.DataFrame):
        df = source.copy()
    else:
        df = pd.read_csv(source)
    df = df.rename(
        columns={
            "employee_id": "Employee_ID",
            "employee_name": "Employee_Name",
            "gender": "Gender",
            "department": "Department",
            "job_role": "Job_Role",
            "education_level": "Education_Level",
            "experience_years": "Experience_Years",
            "monthly_salary": "Monthly_Salary",
            "job_satisfaction": "Job_Satisfaction",
            "work_life_balance": "Work_Life_Balance",
            "performance_rating": "Performance_Rating",
            "overtime": "Overtime",
            "promotion_status": "Promotion_Status",
            "attrition": "Attrition",
        }
    )
    required_columns = {
        "Employee_ID",
        "Department",
        "Experience_Years",
        "Monthly_Salary",
        "Job_Satisfaction",
        "Work_Life_Balance",
        "Performance_Rating",
        "Overtime",
        "Promotion_Status",
        "Attrition",
    }
    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    cleaned = df.copy()
    cleaned["Attrition_Flag"] = cleaned["Attrition"].str.strip().str.lower().eq("yes").astype(int)
    cleaned["Experience_Group"] = pd.cut(
        cleaned["Experience_Years"],
        bins=EXPERIENCE_BINS,
        labels=EXPERIENCE_LABELS,
    )
    cleaned["Salary_Band"] = pd.cut(
        cleaned["Monthly_Salary"],
        bins=SALARY_BINS,
        labels=SALARY_LABELS,
        include_lowest=True,
    )
    return cleaned


def kpi_summary(df: pd.DataFrame) -> dict[str, float | int | str]:
    attrition_rate = df["Attrition_Flag"].mean()
    retained = int((df["Attrition_Flag"] == 0).sum())
    left = int(df["Attrition_Flag"].sum())
    return {
        "employees": int(len(df)),
        "attrition_rate": float(round(attrition_rate * 100, 2)),
        "retained": retained,
        "left": left,
        "avg_salary": float(round(df["Monthly_Salary"].mean(), 2)),
        "avg_experience": float(round(df["Experience_Years"].mean(), 2)),
    }


def attrition_by_category(df: pd.DataFrame, column: str) -> pd.DataFrame:
    summary = (
        df.groupby(column, observed=True)
        .agg(
            employees=("Employee_ID", "count"),
            attritions=("Attrition_Flag", "sum"),
            attrition_rate=("Attrition_Flag", "mean"),
            avg_salary=("Monthly_Salary", "mean"),
        )
        .reset_index()
    )
    summary["attrition_rate"] = summary["attrition_rate"] * 100
    return summary.sort_values("attrition_rate", ascending=False)


def performance_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Performance_Rating", observed=True)
        .agg(
            employees=("Employee_ID", "count"),
            attrition_rate=("Attrition_Flag", lambda x: x.mean() * 100),
            avg_salary=("Monthly_Salary", "mean"),
            promotion_rate=("Promotion_Status", lambda x: x.eq("Promoted").mean() * 100),
        )
        .reset_index()
        .sort_values("Performance_Rating")
    )
    return summary


def filtered_data(
    df: pd.DataFrame,
    departments: list[str],
    job_roles: list[str],
    salary_range: tuple[int, int],
    experience_range: tuple[int, int],
) -> pd.DataFrame:
    mask = (
        df["Department"].isin(departments)
        & df["Job_Role"].isin(job_roles)
        & df["Monthly_Salary"].between(*salary_range)
        & df["Experience_Years"].between(*experience_range)
    )
    return df.loc[mask].copy()


def insight_lines(df: pd.DataFrame) -> list[str]:
    overall = kpi_summary(df)
    dept = attrition_by_category(df, "Department").iloc[0]
    overtime = attrition_by_category(df, "Overtime").set_index("Overtime")
    promotion = attrition_by_category(df, "Promotion_Status").set_index("Promotion_Status")
    satisfaction = attrition_by_category(df, "Job_Satisfaction").iloc[0]

    lines = [
        f"Overall attrition rate is {overall['attrition_rate']}% ({overall['left']} of {overall['employees']} employees).",
        f"{dept['Department']} has the highest department attrition rate at {dept['attrition_rate']:.2f}%.",
        f"Employees with job satisfaction level {satisfaction['Job_Satisfaction']} show the highest attrition rate at {satisfaction['attrition_rate']:.2f}%.",
    ]

    if {"Yes", "No"}.issubset(overtime.index):
        diff = overtime.loc["Yes", "attrition_rate"] - overtime.loc["No", "attrition_rate"]
        lines.append(f"Overtime attrition is {diff:+.2f} percentage points compared with non-overtime employees.")

    if {"Promoted", "Not Promoted"}.issubset(promotion.index):
        diff = promotion.loc["Not Promoted", "attrition_rate"] - promotion.loc["Promoted", "attrition_rate"]
        lines.append(f"Not-promoted employees attrition is {diff:+.2f} percentage points compared with promoted employees.")

    return lines


def objective_insights(df: pd.DataFrame) -> list[dict[str, str]]:
    overall = kpi_summary(df)
    department = attrition_by_category(df, "Department")
    salary = attrition_by_category(df, "Salary_Band")
    satisfaction = attrition_by_category(df, "Job_Satisfaction")
    balance = attrition_by_category(df, "Work_Life_Balance")
    experience = attrition_by_category(df, "Experience_Group")
    promotion = attrition_by_category(df, "Promotion_Status")
    overtime = attrition_by_category(df, "Overtime")
    performance = performance_summary(df)

    top_dept = department.iloc[0]
    low_dept = department.iloc[-1]
    top_salary = salary.iloc[0]
    low_salary = salary.iloc[-1]
    top_satisfaction = satisfaction.iloc[0]
    low_satisfaction = satisfaction.iloc[-1]
    top_balance = balance.iloc[0]
    low_balance = balance.iloc[-1]
    top_experience = experience.iloc[0]
    low_experience = experience.iloc[-1]
    top_overtime = overtime.iloc[0]
    low_overtime = overtime.iloc[-1]
    top_performance = performance.sort_values("attrition_rate", ascending=False).iloc[0]
    best_promotion_perf = performance.sort_values("promotion_rate", ascending=False).iloc[0]

    salary_left = df.loc[df["Attrition_Flag"] == 1, "Monthly_Salary"].mean()
    salary_retained = df.loc[df["Attrition_Flag"] == 0, "Monthly_Salary"].mean()
    salary_gap = salary_left - salary_retained

    promotion_text = "Promotion status has only one available group in the selected filters."
    if {"Promoted", "Not Promoted"}.issubset(set(promotion["Promotion_Status"])):
        promotion_index = promotion.set_index("Promotion_Status")
        not_promoted_rate = promotion_index.loc["Not Promoted", "attrition_rate"]
        promoted_rate = promotion_index.loc["Promoted", "attrition_rate"]
        promotion_text = (
            f"Not-promoted employees have {not_promoted_rate:.2f}% attrition, compared with "
            f"{promoted_rate:.2f}% for promoted employees, a gap of {not_promoted_rate - promoted_rate:+.2f} percentage points."
        )

    overtime_text = "Overtime status has only one available group in the selected filters."
    if {"Yes", "No"}.issubset(set(overtime["Overtime"])):
        overtime_index = overtime.set_index("Overtime")
        overtime_rate = overtime_index.loc["Yes", "attrition_rate"]
        no_overtime_rate = overtime_index.loc["No", "attrition_rate"]
        overtime_text = (
            f"Employees working overtime have {overtime_rate:.2f}% attrition, compared with "
            f"{no_overtime_rate:.2f}% for employees without overtime, a gap of {overtime_rate - no_overtime_rate:+.2f} percentage points."
        )

    return [
        {
            "objective": "1. Overall Attrition Rate Analysis",
            "insight": (
                f"The selected workforce has {overall['employees']:,} employees, with {overall['left']:,} attritions "
                f"and an overall attrition rate of {overall['attrition_rate']:.2f}%."
            ),
        },
        {
            "objective": "2. Department-wise Attrition Analysis",
            "insight": (
                f"{top_dept['Department']} has the highest attrition rate at {top_dept['attrition_rate']:.2f}%, "
                f"while {low_dept['Department']} has the lowest at {low_dept['attrition_rate']:.2f}%."
            ),
        },
        {
            "objective": "3. Salary vs Attrition Analysis",
            "insight": (
                f"The highest attrition appears in the {top_salary['Salary_Band']} salary band at {top_salary['attrition_rate']:.2f}%; "
                f"the lowest is in {low_salary['Salary_Band']} at {low_salary['attrition_rate']:.2f}%. "
                f"Average salary for employees who left is {salary_left:,.0f}, versus {salary_retained:,.0f} for retained employees "
                f"({salary_gap:+,.0f} difference)."
            ),
        },
        {
            "objective": "4. Job Satisfaction Impact Analysis",
            "insight": (
                f"Job satisfaction level {top_satisfaction['Job_Satisfaction']} has the highest attrition rate at "
                f"{top_satisfaction['attrition_rate']:.2f}%, while level {low_satisfaction['Job_Satisfaction']} has the lowest at "
                f"{low_satisfaction['attrition_rate']:.2f}%."
            ),
        },
        {
            "objective": "5. Work-Life Balance Analysis",
            "insight": (
                f"Work-life balance rating {top_balance['Work_Life_Balance']} has the highest attrition rate at "
                f"{top_balance['attrition_rate']:.2f}%, while rating {low_balance['Work_Life_Balance']} has the lowest at "
                f"{low_balance['attrition_rate']:.2f}%."
            ),
        },
        {
            "objective": "6. Experience-wise Attrition Analysis",
            "insight": (
                f"The {top_experience['Experience_Group']} experience group has the highest attrition rate at "
                f"{top_experience['attrition_rate']:.2f}%, while {low_experience['Experience_Group']} has the lowest at "
                f"{low_experience['attrition_rate']:.2f}%."
            ),
        },
        {
            "objective": "7. Promotion Impact on Attrition Analysis",
            "insight": promotion_text,
        },
        {
            "objective": "8. Overtime vs Attrition Analysis",
            "insight": (
                f"{overtime_text} The highest overtime-related segment is {top_overtime['Overtime']} at "
                f"{top_overtime['attrition_rate']:.2f}%, and the lowest is {low_overtime['Overtime']} at "
                f"{low_overtime['attrition_rate']:.2f}%."
            ),
        },
        {
            "objective": "9. Performance Rating Analysis",
            "insight": (
                f"Performance rating {top_performance['Performance_Rating']:.0f} has the highest attrition rate at "
                f"{top_performance['attrition_rate']:.2f}%. Rating {best_promotion_perf['Performance_Rating']:.0f} has the highest "
                f"promotion rate at {best_promotion_perf['promotion_rate']:.2f}% with an average salary of "
                f"{best_promotion_perf['avg_salary']:,.0f}."
            ),
        },
    ]


def section_insights(df: pd.DataFrame) -> dict[str, list[str]]:
    overall = kpi_summary(df)
    department = attrition_by_category(df, "Department")
    salary = attrition_by_category(df, "Salary_Band")
    satisfaction = attrition_by_category(df, "Job_Satisfaction")
    balance = attrition_by_category(df, "Work_Life_Balance")
    experience = attrition_by_category(df, "Experience_Group")
    promotion = attrition_by_category(df, "Promotion_Status")
    overtime = attrition_by_category(df, "Overtime")
    performance = performance_summary(df)

    top_dept = department.iloc[0]
    low_dept = department.iloc[-1]
    top_salary = salary.iloc[0]
    low_salary = salary.iloc[-1]
    top_experience = experience.iloc[0]
    low_experience = experience.iloc[-1]
    top_satisfaction = satisfaction.iloc[0]
    low_satisfaction = satisfaction.iloc[-1]
    top_balance = balance.iloc[0]
    low_balance = balance.iloc[-1]
    top_overtime = overtime.iloc[0]
    top_performance = performance.sort_values("attrition_rate", ascending=False).iloc[0]
    top_promotion_performance = performance.sort_values("promotion_rate", ascending=False).iloc[0]

    salary_left = df.loc[df["Attrition_Flag"] == 1, "Monthly_Salary"].mean()
    salary_retained = df.loc[df["Attrition_Flag"] == 0, "Monthly_Salary"].mean()

    promotion_line = "Promotion comparison is limited because only one promotion group is present after filtering."
    if {"Promoted", "Not Promoted"}.issubset(set(promotion["Promotion_Status"])):
        promotion_index = promotion.set_index("Promotion_Status")
        not_promoted_rate = promotion_index.loc["Not Promoted", "attrition_rate"]
        promoted_rate = promotion_index.loc["Promoted", "attrition_rate"]
        promotion_line = (
            f"Not-promoted employees record {not_promoted_rate:.2f}% attrition versus "
            f"{promoted_rate:.2f}% for promoted employees."
        )

    overtime_line = "Overtime comparison is limited because only one overtime group is present after filtering."
    if {"Yes", "No"}.issubset(set(overtime["Overtime"])):
        overtime_index = overtime.set_index("Overtime")
        overtime_rate = overtime_index.loc["Yes", "attrition_rate"]
        no_overtime_rate = overtime_index.loc["No", "attrition_rate"]
        overtime_line = (
            f"Overtime employees show {overtime_rate:.2f}% attrition versus "
            f"{no_overtime_rate:.2f}% for non-overtime employees."
        )

    return {
        "Attrition Overview": [
            f"Overall attrition is {overall['attrition_rate']:.2f}% with {overall['left']:,} employees leaving out of {overall['employees']:,}.",
            f"{top_dept['Department']} is the highest-risk department at {top_dept['attrition_rate']:.2f}% attrition.",
            f"{low_dept['Department']} is the strongest retention department at {low_dept['attrition_rate']:.2f}% attrition.",
        ],
        "Compensation & Experience": [
            f"The {top_salary['Salary_Band']} salary band has the highest attrition rate at {top_salary['attrition_rate']:.2f}%.",
            f"The {low_salary['Salary_Band']} salary band has the lowest attrition rate at {low_salary['attrition_rate']:.2f}%.",
            f"Employees who left average {salary_left:,.0f} monthly salary, compared with {salary_retained:,.0f} for retained employees.",
            f"The {top_experience['Experience_Group']} group has the highest experience-wise attrition at {top_experience['attrition_rate']:.2f}%, while {low_experience['Experience_Group']} is lowest at {low_experience['attrition_rate']:.2f}%.",
        ],
        "Satisfaction & Balance": [
            f"Job satisfaction level {top_satisfaction['Job_Satisfaction']} has the highest attrition at {top_satisfaction['attrition_rate']:.2f}%.",
            f"Job satisfaction level {low_satisfaction['Job_Satisfaction']} has the lowest attrition at {low_satisfaction['attrition_rate']:.2f}%.",
            f"Work-life balance rating {top_balance['Work_Life_Balance']} has the highest attrition at {top_balance['attrition_rate']:.2f}%.",
            f"Work-life balance rating {low_balance['Work_Life_Balance']} has the lowest attrition at {low_balance['attrition_rate']:.2f}%.",
        ],
        "Promotion & Performance": [
            promotion_line,
            overtime_line,
            f"The highest overtime segment is {top_overtime['Overtime']} with {top_overtime['attrition_rate']:.2f}% attrition.",
            f"Performance rating {top_performance['Performance_Rating']:.0f} has the highest attrition rate at {top_performance['attrition_rate']:.2f}%.",
            f"Performance rating {top_promotion_performance['Performance_Rating']:.0f} has the highest promotion rate at {top_promotion_performance['promotion_rate']:.2f}%.",
        ],
    }
