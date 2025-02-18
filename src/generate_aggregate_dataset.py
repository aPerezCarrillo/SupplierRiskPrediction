import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility
np.random.seed(42)

# Number of suppliers and historical records to generate
n_suppliers = 1000  # Number of unique suppliers
n_records_per_supplier = np.random.randint(5, 50, n_suppliers)  # Random number of records per supplier

# Analysis and prediction windows
current_date = pd.Timestamp("2025-01-01")
analysis_window_start = current_date - pd.DateOffset(months=12)  # Past 12 months
prediction_window_end = current_date + pd.DateOffset(months=6)  # Next 6 months

# Generate mock historical data
def generate_historical_mock_data(n_suppliers, n_records_per_supplier):
    # Initialize an empty list to store historical records
    historical_data = []

    # Loop through each supplier
    for supplier_id in range(1, n_suppliers + 1):
        # Generate a random number of historical records for this supplier
        n_records = n_records_per_supplier[supplier_id - 1]

        for record_id in range(n_records):
            # Generate a single historical record
            record_date = current_date - pd.to_timedelta(np.random.randint(1, 730), unit="days")  # Random date in the past 2 years
            record = {
                "supplier_id": f"S{supplier_id}",  # Unique supplier ID
                "record_date": record_date,
                "severity_level": np.random.choice(["Minor", "Moderate", "Critical"]),
                "category_of_violation": np.random.choice(["Safety", "Quality", "Documentation", "Regulatory"]),
                "root_cause_category": np.random.choice(["Human Error", "Process Failure", "Equipment Malfunction"]),
                "corrective_actions_suggested": np.random.choice([0, 1]),  # 0 = No, 1 = Yes
                "affected_product": np.random.choice(["Product A", "Product B", "Product C", "Product D"]),
                "process_involved": np.random.choice(["Packaging", "Testing", "Shipping", "Manufacturing"]),
                "tone_of_letter": np.random.choice(["Formal", "Urgent", "Warning"]),
                "length_of_letter": np.random.randint(100, 1000),  # Length of the letter in words
                "deadline_for_resolution": np.random.randint(1, 30),  # Days to resolve the issue
                "resolution_status": np.random.choice(["Resolved", "Pending", "Unresolved"]),
                "follow_up_actions": np.random.choice([0, 1]),  # 0 = No, 1 = Yes
            }
            historical_data.append(record)

    # Create a DataFrame for historical records
    historical_df = pd.DataFrame(historical_data)

    # Aggregate features for analysis window
    analysis_data = historical_df[
        (historical_df["record_date"] >= analysis_window_start) &
        (historical_df["record_date"] < current_date)  # Only include records in the analysis window
    ]
    aggregated_data = analysis_data.groupby("supplier_id").agg(
        total_warnings=("severity_level", "count"),
        critical_issues=("severity_level", lambda x: (x == "Critical").sum()),
        moderate_issues=("severity_level", lambda x: (x == "Moderate").sum()),
        minor_issues=("severity_level", lambda x: (x == "Minor").sum()),
        safety_violations=("category_of_violation", lambda x: (x == "Safety").sum()),
        quality_violations=("category_of_violation", lambda x: (x == "Quality").sum()),
        documentation_violations=("category_of_violation", lambda x: (x == "Documentation").sum()),
        regulatory_violations=("category_of_violation", lambda x: (x == "Regulatory").sum()),
        unresolved_issues=("resolution_status", lambda x: (x == "Unresolved").sum()),
        follow_up_actions=("follow_up_actions", "sum"),
        avg_length_of_letter=("length_of_letter", "mean"),
        avg_deadline_for_resolution=("deadline_for_resolution", "mean"),
    ).reset_index()

    # Add general supplier features
    general_features = {
        "supplier_id": [f"S{i}" for i in range(1, n_suppliers + 1)],
        "supplier_location": np.random.choice(["North America", "Europe", "Asia", "South America"], n_suppliers),
        "supplier_size": np.random.choice(["Small", "Medium", "Large"], n_suppliers),
        "industry_type": np.random.choice(["Electronics", "Pharmaceuticals", "Manufacturing", "Food"], n_suppliers),
        "supplier_tenure": np.random.randint(1, 20, n_suppliers),  # Years working with the supplier
        "audit_frequency": np.random.randint(1, 5, n_suppliers),  # Number of audits per year
        "audit_score": np.random.uniform(50, 100, n_suppliers),  # Audit score (0-100 scale)
        "delivery_timeliness": np.random.uniform(80, 100, n_suppliers),  # Percentage of on-time deliveries
        "order_volume": np.random.randint(100, 10000, n_suppliers),  # Total order volume
        "payment_history": np.random.choice(["Good", "Average", "Poor"], n_suppliers),
        "communication_frequency": np.random.randint(1, 10, n_suppliers),  # Number of communications per month
        "dispute_history": np.random.randint(0, 5, n_suppliers),  # Number of disputes
        "criticality_of_product": np.random.choice(["Low", "Medium", "High"], n_suppliers),
        "product_complexity": np.random.choice(["Simple", "Moderate", "Complex"], n_suppliers),
        "region_risk": np.random.uniform(0, 1, n_suppliers),  # Risk score based on supplier region
    }

    general_df = pd.DataFrame(general_features)

    # Merge aggregated features with general supplier features
    final_df = pd.merge(general_df, aggregated_data, on="supplier_id", how="left").fillna(0)

    # Define target variable based on prediction window
    prediction_data = historical_df[
        (historical_df["record_date"] >= current_date) &
        (historical_df["record_date"] < prediction_window_end)  # Records in the prediction window
    ]
    final_df["ncr_or_warning_letter"] = final_df["supplier_id"].isin(
        prediction_data["supplier_id"]
    ).astype(int)  # Target = 1 if NCR or Warning Letter is found in prediction window

    return final_df, historical_df

# Generate the mock dataset
final_data, historical_data = generate_historical_mock_data(n_suppliers, n_records_per_supplier)

# Display the first few rows of the final dataset
print("Aggregated Supplier Data:")
print(final_data.head())

print("\nHistorical Records Data:")
print(historical_data.head())

# Save to CSV for further use
DATA_FOLDER = "../data/historical_ds/"
final_data.to_csv(DATA_FOLDER + "aggregated_supplier_data_with_target.csv", index=False)
print(final_data["ncr_or_warning_letter"].value_counts())
historical_data.to_csv(DATA_FOLDER + "historical_records_data_with_dates.csv", index=False)
