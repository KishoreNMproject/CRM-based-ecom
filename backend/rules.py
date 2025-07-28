import pandas as pd

def get_business_rules(rfm_df: pd.DataFrame):
    rules = []

    # Safety check: Is RFM data usable?
    if rfm_df.empty or not all(col in rfm_df.columns for col in ["CustomerID", "Recency", "Frequency", "Monetary"]):
        return [{
            "rule": "Invalid or missing RFM data",
            "criteria": "Missing required RFM columns or empty DataFrame",
            "matched_customers": []
        }]

    try:
        # Rule 1: High Value Customers
        high_value = rfm_df[
            (rfm_df['Recency'] <= 90) &
            (rfm_df['Frequency'] >= 3) &
            (rfm_df['Monetary'] > 500)
        ]
        rules.append({
            "rule": "High Value Customers",
            "criteria": "Recency ≤ 90, Frequency ≥ 3, Monetary > 500",
            "matched_customers": high_value['CustomerID'].tolist()
        })

        # Rule 2: Potential Loyalists
        loyal = rfm_df[
            (rfm_df['Recency'] <= 60) &
            (rfm_df['Frequency'] >= 2)
        ]
        rules.append({
            "rule": "Potential Loyalists",
            "criteria": "Recency ≤ 60, Frequency ≥ 2",
            "matched_customers": loyal['CustomerID'].tolist()
        })

        # Rule 3: At Risk Customers
        at_risk = rfm_df[
            (rfm_df['Recency'] > 120) &
            (rfm_df['Frequency'] <= 2)
        ]
        rules.append({
            "rule": "At Risk Customers",
            "criteria": "Recency > 120, Frequency ≤ 2",
            "matched_customers": at_risk['CustomerID'].tolist()
        })

        # Rule 4: Lost Customers
        lost = rfm_df[
            (rfm_df['Recency'] > 180)
        ]
        rules.append({
            "rule": "Lost Customers",
            "criteria": "Recency > 180",
            "matched_customers": lost['CustomerID'].tolist()
        })

        # Rule 5: New Customers
        new_customers = rfm_df[
            (rfm_df['Recency'] <= 30) &
            (rfm_df['Frequency'] == 1)
        ]
        rules.append({
            "rule": "New Customers",
            "criteria": "Recency ≤ 30, Frequency = 1",
            "matched_customers": new_customers['CustomerID'].tolist()
        })

        return rules or [{
            "rule": "No Matches",
            "criteria": "Rules applied but no customers matched any criteria",
            "matched_customers": []
        }]

    except Exception as e:
        return [{
            "rule": "Error in Rule Evaluation",
            "criteria": str(e),
            "matched_customers": []
        }]
