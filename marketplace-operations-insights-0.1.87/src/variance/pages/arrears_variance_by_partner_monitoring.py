import streamlit as st
import pandas as pd
from utils import db_util, auth_util
from variance.models.arrears_variance_by_partner_model import fetch_arrears_variance_by_partner_tasks
from datetime import datetime


def show_arrears_variance_by_partner_monitoring_page():
    st.title("Arrears Variance by Partner Report")
    schema = 'mart_observability_and_automation.'
    database = 'redshift'
    dataset_options = ["partner_id", "partner_name"]
    selected_dataset = st.selectbox("Select Dataset Options", dataset_options)
    if selected_dataset == "partner_id":
        option = st.text_input("Partner id", key="partner_id_input")
        df = fetch_arrears_variance_by_partner_tasks(option, selected_dataset, schema, database)
        st.dataframe(df)
    elif selected_dataset == "partner_name":
        option = st.text_input("Partner name", key="partner_name_input")
        df = fetch_arrears_variance_by_partner_tasks(option, selected_dataset, schema, database)
        st.dataframe(df)

if __name__ == "__page__":
    show_arrears_variance_by_partner_monitoring_page()
