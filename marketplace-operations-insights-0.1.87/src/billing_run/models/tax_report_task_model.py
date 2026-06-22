import streamlit as st
import pandas as pd
from utils import db_util

@st.cache_data(ttl=600)
def fetch_tax_report_tasks(schema: str = "", database: str = None, invoice_date=None, partner_id=None):
    """
    Fetches tax report tasks data from the database

    Args:
        schema (str): Database schema prefix. Defaults to empty string.
        database (str): Database to query. Defaults to None, which will use postgresql if available, otherwise redshift.

    Returns:
        DataFrame: Pandas DataFrame containing tax report tasks data

    Tables used:
       cira, invoice tables of the cc schema 
       sales_tax - derived by joining the cira and invoice tables
    """

    query = f"""
    WITH sales_tax AS (
    SELECT
      i.invoice_date,
      CASE
        WHEN i.partner_id is not null then 'Partner'
        ELSE 'Company'
      END AS invoice_type,
      i.business_unit_code AS business_unit,
      cira.partner_name,
      COALESCE(i.partner_id, -1) AS invoice_partner_id,
      COALESCE(i.company_id, -1) AS invoice_company_id,
      CASE
        WHEN i.partner_id IS NOT NULL THEN sum(cira.partner_sales_tax_total)
        ELSE SUM(cira.company_sales_tax_total)
      END::DECIMAL(18,2) AS tax_total,
      LAG(tax_total) over (partition by invoice_partner_id, invoice_company_id order by i.invoice_date asc) AS prior_month_tax_total
    FROM cc.csv_invoice_row_archive cira
    JOIN cc.invoice i on cira.invoice_id=i.id
    WHERE i.invoice_date>= :invoice_date + INTERVAL '1 month'
      AND i.partner_id=:partner_id
      AND i.status!='Void'
    GROUP BY
      i.invoice_date,
      i.business_unit_code,
      cira.partner_name,
      i.partner_id,
      i.company_id
    ORDER BY i.invoice_date desc
    )

    SELECT
      invoice_date,
      invoice_type,
      business_unit,
      partner_name,
      invoice_partner_id,
      invoice_company_id,
      tax_total,
      prior_month_tax_total,
      tax_total - prior_month_tax_total as month_over_month_tax_difference,
      CASE
    	WHEN prior_month_tax_total is null or prior_month_tax_total = 0 then null
    	ELSE ( ((tax_total - prior_month_tax_total) / prior_month_tax_total) * 100.0 )
      END as month_over_month_tax_variance
    FROM sales_tax
    """

    results = db_util.query(query, params={"invoice_date": invoice_date, "partner_id": partner_id})
    return results


