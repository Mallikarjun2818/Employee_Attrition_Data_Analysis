from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

from src.analytics import attrition_by_category, load_employee_data, performance_summary


OUTPUT_DIR = Path("report_visualizations")


def save_bar(data, x, y, title, filename, ylabel="Attrition Rate (%)"):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=data, x=x, y=y, ax=ax)
    ax.set_title(title, fontsize=15, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=25)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", padding=3)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_count(data, x, hue, title, filename):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(data=data, x=x, hue=hue, ax=ax)
    ax.set_title(title, fontsize=15, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Employees")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    sns.set_theme(style="whitegrid", palette="Set2")
    df = load_employee_data()

    save_count(
        df,
        "Attrition",
        "Attrition",
        "Overall Employee Attrition Count",
        "01_overall_attrition_count.png",
    )

    save_bar(
        attrition_by_category(df, "Department"),
        "Department",
        "attrition_rate",
        "Department-wise Attrition Rate",
        "02_department_wise_attrition_rate.png",
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df, x="Attrition", y="Monthly_Salary", ax=ax)
    ax.set_title("Salary Distribution by Attrition", fontsize=15, fontweight="bold")
    ax.set_xlabel("Attrition")
    ax.set_ylabel("Monthly Salary")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "03_salary_distribution_by_attrition.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    save_bar(
        attrition_by_category(df, "Salary_Band"),
        "Salary_Band",
        "attrition_rate",
        "Salary Band vs Attrition Rate",
        "04_salary_band_attrition_rate.png",
    )

    save_bar(
        attrition_by_category(df, "Job_Satisfaction"),
        "Job_Satisfaction",
        "attrition_rate",
        "Job Satisfaction Impact on Attrition",
        "05_job_satisfaction_attrition_rate.png",
    )

    save_bar(
        attrition_by_category(df, "Work_Life_Balance"),
        "Work_Life_Balance",
        "attrition_rate",
        "Work-Life Balance Impact on Attrition",
        "06_work_life_balance_attrition_rate.png",
    )

    save_bar(
        attrition_by_category(df, "Experience_Group"),
        "Experience_Group",
        "attrition_rate",
        "Experience-wise Attrition Rate",
        "07_experience_wise_attrition_rate.png",
    )

    save_bar(
        attrition_by_category(df, "Promotion_Status"),
        "Promotion_Status",
        "attrition_rate",
        "Promotion Impact on Attrition",
        "08_promotion_impact_attrition_rate.png",
    )

    save_bar(
        attrition_by_category(df, "Overtime"),
        "Overtime",
        "attrition_rate",
        "Overtime vs Attrition Rate",
        "09_overtime_attrition_rate.png",
    )

    performance = performance_summary(df)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    sns.lineplot(data=performance, x="Performance_Rating", y="attrition_rate", marker="o", ax=ax1, color="#2176ae")
    sns.lineplot(data=performance, x="Performance_Rating", y="promotion_rate", marker="o", ax=ax2, color="#d95d39")
    ax1.set_title("Performance Rating vs Attrition and Promotion", fontsize=15, fontweight="bold")
    ax1.set_xlabel("Performance Rating")
    ax1.set_ylabel("Attrition Rate (%)", color="#2176ae")
    ax2.set_ylabel("Promotion Rate (%)", color="#d95d39")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "10_performance_rating_attrition_promotion.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Generated {len(list(OUTPUT_DIR.glob('*.png')))} visualizations in {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
