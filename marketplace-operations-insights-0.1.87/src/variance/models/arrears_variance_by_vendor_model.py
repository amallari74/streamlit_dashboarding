from utils import db_util

def fetch_arrears_variance_by_vendor():
    query = """
    SELECT
      product.vendor,
      variance.business_unit_code,
      SUM(variance.usd_6_months_prior_gross_revenue) AS usd_6_months_prior_gross_revenue,
      SUM(variance.usd_5_months_prior_gross_revenue) AS usd_5_months_prior_gross_revenue,
      SUM(variance.usd_4_months_prior_gross_revenue) AS usd_4_months_prior_gross_revenue,
      SUM(variance.usd_3_months_prior_gross_revenue) AS usd_3_months_prior_gross_revenue,
      SUM(variance.usd_2_months_prior_gross_revenue) AS usd_2_months_prior_gross_revenue,
      SUM(variance.prior_month_revenue_usd) AS prior_month_revenue_usd,
      SUM(variance.current_month_revenue_usd) AS current_month_revenue_usd,
      SUM(variance.current_over_prior_month_variance) AS prior_vs_current_revenue_difference,
      CASE
        WHEN SUM(variance.prior_month_revenue_usd) = 0 THEN NULL
        ELSE
          ROUND(
            (
              (SUM(variance.current_month_revenue_usd) - SUM(variance.prior_month_revenue_usd))
              / NULLIF(SUM(variance.prior_month_revenue_usd), 0)
            ) * 100
          , 2)
      END AS percent_change_current_vs_prior,
      CASE
        WHEN (
          SUM(
            variance.usd_2_months_prior_gross_revenue +
            variance.usd_3_months_prior_gross_revenue +
            variance.usd_4_months_prior_gross_revenue +
            variance.usd_5_months_prior_gross_revenue +
            variance.usd_6_months_prior_gross_revenue
          ) / 5.0
        ) = 0 THEN NULL
        ELSE
          ROUND(
            (
              (
                SUM(variance.current_month_revenue_usd) -
                (
                  SUM(
                    variance.usd_2_months_prior_gross_revenue +
                    variance.usd_3_months_prior_gross_revenue +
                    variance.usd_4_months_prior_gross_revenue +
                    variance.usd_5_months_prior_gross_revenue +
                    variance.usd_6_months_prior_gross_revenue
                  ) / 5.0
                )
              )
              /
              NULLIF(
                SUM(
                  variance.usd_2_months_prior_gross_revenue +
                  variance.usd_3_months_prior_gross_revenue +
                  variance.usd_4_months_prior_gross_revenue +
                  variance.usd_5_months_prior_gross_revenue +
                  variance.usd_6_months_prior_gross_revenue
                ) / 5.0,
              0)
            ) * 100
          , 2)
      END AS six_month_average_variance_percentage_reversed
    FROM
      mart_observability_and_automation.agg_arrears_subscription_monthly_variance AS variance
    LEFT JOIN
      mart_observability_and_automation.stg__cc_product AS product
      ON variance.subscription_product_id = product.id
    GROUP BY
      variance.business_unit_code,
      product.vendor
    ORDER BY
      product.vendor,
      variance.business_unit_code;
    """

    return db_util.query(query)