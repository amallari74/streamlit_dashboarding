from utils import db_util
import pandas as pd


def fetch_invoice_analytics(invoice_start_date, invoice_end_date=None, db="cube"):
    # if invoice_end_date is not None:
    #     parameter = f"WHERE invoice_date >= '{invoice_start_date}' AND invoice_date <= '{invoice_end_date}'"
    # else:
    #     parameter = f"WHERE invoice_date >= '{invoice_start_date}'"
    # query = f"""
    # SELECT 
    #     invoice_date, 
    #     product_id, 
    #     vendor, 
    #     invoice_type, 
    #     target_audience, 
    #     region, 
    #     row_type, 
    #     term, 
    #     business_unit_code, 
    #     currency_code, 
    #     exchange_rate_conversion_rate, 
    #     quantity, 
    #     customer_cost_total_non_usd, 
    #     partner_cost_total_non_usd, 
    #     line_item_total_usd, 
    #     gross_revenue_non_usd, 
    #     net_revenue_non_usd, 
    #     gross_revenue_usd, 
    #     net_revenue_usd
    # FROM agg_snapshot
    # {parameter}
    # """
    # return db_util.query(query, db=db)
    None