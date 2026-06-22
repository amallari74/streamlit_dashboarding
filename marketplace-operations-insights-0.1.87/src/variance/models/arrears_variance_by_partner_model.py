import streamlit as st
import pandas as pd
from utils import db_util

@st.cache_data(ttl=600)
def fetch_arrears_variance_by_partner_tasks(option: str | int, selected_dataset: str, schema: str = "", database: str = None):
    """
    Fetches arrears variance by partner report tasks data from the database

    Args:
        schema (str): Database schema prefix. Defaults to empty string.
        database (str): Database to query. Defaults to None, which will use postgresql if available, otherwise redshift.

    Returns:
        DataFrame: Pandas DataFrame containing arrears variance by partner report data

    Table used:
       agg_arrears_subscription_monthly_variance, from mart_observability_and_automation schema
    """

    if option and selected_dataset:
        selected_option = f"smv.{selected_dataset}"

        query = f"""
        SELECT
            smv.partner_id,
            smv.partner_name,
            smv.business_unit_code,
            smv.subscription_product_id,
            smv.subscription_product_name,
            smv.subscription_status,
            smv.subscription_start_date,
            smv.subscription_end_date,
            smv.subscription_id,
            smv.original_subscription_id,
            smv.type,
            smv.current_month_quantity,
            smv.usd_6_months_prior_gross_revenue,
            smv.usd_5_months_prior_gross_revenue,
            smv.usd_4_months_prior_gross_revenue,
            smv.usd_3_months_prior_gross_revenue,
            smv.usd_2_months_prior_gross_revenue,
            sum(smv.prior_month_revenue_usd) as usd_prior_month_revenue,
            sum(smv.current_month_revenue_usd) as usd_current_month_revenue,
            sum(smv.current_over_prior_month_variance) as prior_vs_current_revenue_difference,
            CASE
                WHEN usd_prior_month_revenue = 0 THEN null
                ELSE (((usd_current_month_revenue - usd_prior_month_revenue) / usd_prior_month_revenue) * 100.0)
            END as Percentage_Change
        FROM
            mart_observability_and_automation.agg_arrears_subscription_monthly_variance smv
        WHERE {selected_option} = '{option}'
        GROUP BY
            smv.partner_id,
            smv.business_unit_code,
            smv.partner_name,
            smv.subscription_product_id,
            smv.subscription_product_name,
            smv.subscription_status,
            smv.subscription_start_date,
            smv.subscription_end_date,
            smv.subscription_id,
            smv.original_subscription_id,
            smv.type,
            smv.current_month_quantity,
            smv.usd_6_months_prior_gross_revenue,
            smv.usd_5_months_prior_gross_revenue,
            smv.usd_4_months_prior_gross_revenue,
            smv.usd_3_months_prior_gross_revenue,
            smv.usd_2_months_prior_gross_revenue
        ORDER BY
            smv.partner_id
        """

        results = db_util.query(query, params={"option": option, "selected_dataset": selected_dataset})
        return results
