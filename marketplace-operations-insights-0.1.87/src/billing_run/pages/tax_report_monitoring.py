import streamlit as st
import pandas as pd
from utils import db_util, auth_util
from billing_run.models.tax_report_task_model import fetch_tax_report_tasks
from datetime import datetime


def show_tax_report_monitoring_page():
    st.title("Tax Report")
    min_date = datetime(2021, 1, 1)
    max_date = datetime.now()
    schema = 'cc'
    database = 'redshift'
    invoice_date = st.date_input("Select invoice date", max_value=max_date, min_value=min_date)
    partner_id = st.text_input("Partner id", key="partner_id_input")
    df = fetch_tax_report_tasks(schema, database, invoice_date, partner_id)
    st.dataframe(df)

if __name__ == "__page__":
    show_tax_report_monitoring_page()
