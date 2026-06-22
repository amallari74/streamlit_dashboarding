import streamlit as st
import pandas as pd
import datetime as dt
from diagnostics.models.invoice_analytics import fetch_invoice_analytics
from billing_run.models.invoice_model import fetch_historical_invoice_totals_by_vendor

#swap out once cube agg_snapshot model is in place
vendor_options = [
    "Microsoft",
    "SentinelOne",
    "Proofpoint",
    "Adobe",
]
#swap out once cube agg_snapshot model is in place
business_unit_options = [
"pax8_my",
"tvg_sia",
"pax8_australia",
"resello_gmbh",
"pax8_id",
"pax8_sweden_ab",
"pax8_spain_sl",
"resello_bv",
"PAX8_UK",
"pax8_th",
"pax8_ph",
"tvg_uab",
"pax8_vn",
"tvg_eesti",
"PAX8_US",
"pax8_nz",
"pax8_sg",
"pax8_canada"
]

partner_tier_options = {
 "Inactive": "LEVEL_0", 
 "Welcome Period": "LEVEL_1",
 "Alliance": "LEVEL_2",
 "Ignite": "LEVEL_3",
 "Velocity": "LEVEL_4",
 "Titan": "LEVEL_5",
 "Galactic": "LEVEL_6"
}

def init():
    st.title("Historical Invoice Totals by Vendor")
    st.markdown("All Data in this table is normalized to USD. Please reach out to [mog-intake](https://pax8.enterprise.slack.com/archives/C09PCB08DUH) in slack to report any discrepancies.")

    single_period_report, multiple_period_report = st.tabs(["Single Period Report", "Multiple Period Report"])
    with single_period_report:
        single_period_business_unit = None
        single_period_vendor = None
        if (single_period_business_unit not in st.session_state) and (single_period_vendor not in st.session_state):
          with st.container(border=True):             
            single_period_invoice_month = st.date_input(label="Invoice Month", value=dt.datetime.now().replace(day=1), key="single_period_invoice_month", format="YYYY-MM-DD")
            schema = 'mart_observability_and_automation'
            database = 'redshift'
            df = fetch_historical_invoice_totals_by_vendor(single_period_invoice_month, schema, database)
            st.dataframe(df)

            col1, col2, col3 = st.columns(3)
            with col1:
                with st.container(border=True):
                    st.metric("Total Revenue (USD)", st.write(f'${df["revenue_billed_usd"].sum():,.2f}'))
            with col2:
                with st.container(border=True):
                    st.metric("Number of Items for Vendors", df.shape[0])
            with col3:
                with st.container(border=True):
                    st.metric("Top Item Share 'in %' for Vendors", st.write(f'{((df.iloc[0,3]/df["revenue_billed_usd"].sum())*100):,.2f}'))
            
            st.divider()
            st.caption("Aggregated Revenue Per Vendor")
            df_agg = df.groupby('vendor_name')['revenue_billed_usd'].sum()
            df_mod = df_agg.sort_values(ascending=False)
            total_revenue_all_vendors = df_mod.sum()
            df_mod_frame = df_mod.to_frame()
            df_mod_frame['%_of_revenue_per_vendor'] = (df_mod_frame["revenue_billed_usd"]/total_revenue_all_vendors) * 100
            st.dataframe(df_mod_frame)

    with multiple_period_report:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                multiple_period_invoice_month_start = st.date_input(label="Invoice Month Start", value=dt.datetime.now().replace(day=1), key="multiple_period_invoice_month_start", format="YYYY-MM-DD")
            with col2:
                multiple_period_invoice_month_end = st.date_input(label="Invoice Month End", value=dt.datetime.now().replace(day=1), key="multiple_period_invoice_month_end", format="YYYY-MM-DD")
            multiple_period_vendor = st.multiselect(label="Vendor", options=vendor_options, key="multiple_period_vendor")
            multiple_period_business_unit = st.multiselect(label="Business Unit", options=business_unit_options, key="multiple_period_business_unit")
            multiple_period_partner_tier = st.pills(label="Partner Tier", options=partner_tier_options.keys(), key="multiple_period_partner_tier", selection_mode="multi")

        col4, col5, col6, col7 = st.columns(4)
        with col4:
            with st.container(border=True):
                st.metric("Periods Compared", "0")
            with col5:
                with st.container(border=True):
                    st.metric("Total Vendors", "0")
            with col6:
                with st.container(border=True):
                    st.metric("Average Period Revenue (USD)", "0")
            with col7:
                with st.container(border=True):
                    st.metric("Trending Vendors", "0")
        with st.container(border=True):
            st.dataframe(pd.DataFrame(columns=["Invoice Date", "Product ID", "Vendor", "Invoice Type", "Target Audience", "Region", "Row Type", "Term", "Business Unit Code", "Currency Code", "Exchange Rate Conversion Rate", "Quantity", "Customer Cost Total (Non-USD)", "Partner Cost Total (Non-USD)", "Line Item Total (USD)", "Gross Revenue (Non-USD)", "Net Revenue (Non-USD)", "Gross Revenue (USD)", "Net Revenue (USD)"]), use_container_width=True)


if __name__ == "__page__":
    init()