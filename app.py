from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src.analytics import (
    DATA_PATH,
    attrition_by_category,
    filtered_data,
    kpi_summary,
    load_employee_data,
    objective_insights,
    performance_summary,
    section_insights,
)


st.set_page_config(
    page_title="Employee Attrition Analysis",
    page_icon=":bar_chart:",
    layout="wide",
)

sns.set_theme(style="whitegrid", palette="Set2")


@st.cache_data(show_spinner=False)
def cached_csv_load(uploaded_file):
    if uploaded_file is not None:
        return load_employee_data(uploaded_file)
    return load_employee_data(DATA_PATH)


def bar_chart(data: pd.DataFrame, x: str, y: str, title: str, hue: str | None = None):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    sns.barplot(data=data, x=x, y=y, hue=hue, ax=ax)
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Attrition Rate (%)" if y == "attrition_rate" else y.replace("_", " ").title())
    ax.tick_params(axis="x", rotation=25)
    ax.bar_label(ax.containers[0], fmt="%.1f", padding=3)
    fig.tight_layout()
    return fig


def count_chart(data: pd.DataFrame, x: str, hue: str, title: str):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    sns.countplot(data=data, x=x, hue=hue, ax=ax)
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Employees")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    return fig


def salary_boxplot(data: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    sns.boxplot(data=data, x="Attrition", y="Monthly_Salary", ax=ax)
    ax.set_title("Salary Distribution by Attrition", fontweight="bold")
    ax.set_xlabel("Attrition")
    ax.set_ylabel("Monthly Salary")
    fig.tight_layout()
    return fig


def performance_dual_axis(data: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(8, 4.6))
    ax2 = ax1.twinx()
    sns.lineplot(data=data, x="Performance_Rating", y="attrition_rate", marker="o", ax=ax1, color="#2176ae")
    sns.lineplot(data=data, x="Performance_Rating", y="promotion_rate", marker="o", ax=ax2, color="#d95d39")
    ax1.set_title("Performance Rating vs Attrition and Promotion", fontweight="bold")
    ax1.set_ylabel("Attrition Rate (%)", color="#2176ae")
    ax2.set_ylabel("Promotion Rate (%)", color="#d95d39")
    ax1.set_xlabel("Performance Rating")
    fig.tight_layout()
    return fig


st.title("Employee Attrition Analysis Dashboard")
st.caption("Python Pandas analysis with Matplotlib and Seaborn visuals.")

with st.sidebar:
    st.header("Data Source")
    uploaded_file = st.file_uploader("Upload replacement CSV", type=["csv"])
    df = cached_csv_load(uploaded_file)

    st.header("Filters")
    departments = st.multiselect("Department", sorted(df["Department"].unique()), default=sorted(df["Department"].unique()))
    job_roles = st.multiselect("Job Role", sorted(df["Job_Role"].unique()), default=sorted(df["Job_Role"].unique()))
    salary_range = st.slider(
        "Monthly Salary",
        int(df["Monthly_Salary"].min()),
        int(df["Monthly_Salary"].max()),
        (int(df["Monthly_Salary"].min()), int(df["Monthly_Salary"].max())),
        step=1000,
    )
    experience_range = st.slider(
        "Experience Years",
        int(df["Experience_Years"].min()),
        int(df["Experience_Years"].max()),
        (int(df["Experience_Years"].min()), int(df["Experience_Years"].max())),
    )

filtered = filtered_data(df, departments, job_roles, salary_range, experience_range)
if filtered.empty:
    st.warning("No employees match the selected filters.")
    st.stop()

kpis = kpi_summary(filtered)
tab_insights = section_insights(filtered)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Employees", f"{kpis['employees']:,}")
col2.metric("Attrition Rate", f"{kpis['attrition_rate']:.2f}%")
col3.metric("Left", f"{kpis['left']:,}")
col4.metric("Avg Salary", f"{kpis['avg_salary']:,.0f}")
col5.metric("Avg Experience", f"{kpis['avg_experience']:.1f} yrs")

st.subheader("Objective-wise Insights")
for item in objective_insights(filtered):
    with st.container(border=True):
        st.markdown(f"**{item['objective']}**")
        st.write(item["insight"])

tab1, tab2, tab3, tab4 = st.tabs(
    ["Attrition Overview", "Compensation & Experience", "Satisfaction & Balance", "Promotion & Performance"]
)

with tab1:
    st.subheader("Attrition Overview Insights")
    for line in tab_insights["Attrition Overview"]:
        st.write(f"- {line}")
    c1, c2 = st.columns(2)
    dept_summary = attrition_by_category(filtered, "Department")
    c1.pyplot(bar_chart(dept_summary, "Department", "attrition_rate", "Department-wise Attrition Rate"))
    c2.pyplot(count_chart(filtered, "Department", "Attrition", "Department Employee Count by Attrition"))
    st.dataframe(dept_summary, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Compensation & Experience Insights")
    for line in tab_insights["Compensation & Experience"]:
        st.write(f"- {line}")
    c1, c2 = st.columns(2)
    c1.pyplot(salary_boxplot(filtered))
    salary_summary = attrition_by_category(filtered, "Salary_Band")
    c2.pyplot(bar_chart(salary_summary, "Salary_Band", "attrition_rate", "Salary Band vs Attrition"))
    exp_summary = attrition_by_category(filtered, "Experience_Group")
    st.pyplot(bar_chart(exp_summary, "Experience_Group", "attrition_rate", "Experience-wise Attrition"))

with tab3:
    st.subheader("Satisfaction & Balance Insights")
    for line in tab_insights["Satisfaction & Balance"]:
        st.write(f"- {line}")
    c1, c2 = st.columns(2)
    satisfaction = attrition_by_category(filtered, "Job_Satisfaction")
    balance = attrition_by_category(filtered, "Work_Life_Balance")
    c1.pyplot(bar_chart(satisfaction, "Job_Satisfaction", "attrition_rate", "Job Satisfaction Impact"))
    c2.pyplot(bar_chart(balance, "Work_Life_Balance", "attrition_rate", "Work-Life Balance Impact"))

with tab4:
    st.subheader("Promotion & Performance Insights")
    for line in tab_insights["Promotion & Performance"]:
        st.write(f"- {line}")
    c1, c2 = st.columns(2)
    promotion = attrition_by_category(filtered, "Promotion_Status")
    overtime = attrition_by_category(filtered, "Overtime")
    c1.pyplot(bar_chart(promotion, "Promotion_Status", "attrition_rate", "Promotion Impact on Attrition"))
    c2.pyplot(bar_chart(overtime, "Overtime", "attrition_rate", "Overtime vs Attrition"))
    perf = performance_summary(filtered)
    st.pyplot(performance_dual_axis(perf))
    st.dataframe(perf, use_container_width=True, hide_index=True)

with st.expander("View Filtered Employee Records"):
    st.dataframe(filtered.drop(columns=["Attrition_Flag"]), use_container_width=True, hide_index=True)
