import streamlit as st
import pandas as pd
from utils import db_util, auth_util
from variance.models.arrears_variance_by_vendor_model import fetch_arrears_variance_by_vendor

def show_arrears_variance_by_vendor_page():
    st.title("Arrears Variance by Vendor Report")

    df = fetch_arrears_variance_by_vendor()

    # Revenue columns to add $
    dollar_cols = [
        "current_month_revenue_usd",
        "prior_month_revenue_usd",
        "usd_2_months_prior_gross_revenue",
        "usd_3_months_prior_gross_revenue",
        "usd_4_months_prior_gross_revenue",
        "usd_5_months_prior_gross_revenue",
        "usd_6_months_prior_gross_revenue",
        "prior_vs_current_revenue_difference"
    ]

    # Identify your percent columns
    pct_cols = [
        "percent_change_current_vs_prior",
        "six_month_average_variance_percentage_reversed"
    ]

    # ---- Dollar Formatting ----
    for col in dollar_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: f"${x:,.2f}" if pd.notnull(x) else ""
            )

    # Convert numeric values → "12.34%"
    for col in pct_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: f"{x:.0f}%" if pd.notnull(x) else "NULL"
            )

    # Define color function for positive (green) / negative (red)
    def color_percent(val):
        if val == "" or val is None:
            return ""
        try:
            num = float(val.replace("%", ""))
            if num > 0:
                return "color: #16a34a;"  # green
            elif num < 0:
                return "color: #dc2626;"  # red
        except:
            pass
        return ""

    styled = df.style.applymap(color_percent, subset=pct_cols)

    st.dataframe(styled, use_container_width=True)

if __name__ == "__page__":
    show_arrears_variance_by_vendor_page()