import streamlit as st
from utils import db_util
from variance.models.arrears_variance_by_vendor_model import fetch_arrears_variance_by_vendor

def main():
    # Check if we need to update navigation
    if st.session_state.get("nav_section") != "Subscription Level Variances":
        # Update navigation mode
        st.session_state.nav_section = "Subscription Level Variances"
        # Rerun the app to refresh navigation
        st.rerun()
    
    # Billing landing page content
    st.title("Subscription Level Variances")
    
    st.markdown("""
    This page contains the **MOG Observability Reports** that was formerly located in PowerBI
    
    - Arrears Variance by Vendor
    - Arrears Variance by Partner
    - Invoice Row Variance
    - Invoice Row Variance by Vendor
    """)

if __name__ == "__page__":
    main() 