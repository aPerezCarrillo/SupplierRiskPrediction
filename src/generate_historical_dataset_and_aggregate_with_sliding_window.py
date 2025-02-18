import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Generate mock historical data for suppliers
n_suppliers = 1000
n_records = 1000

# Generate random historical data
historical_data = pd.DataFrame({
    "supplier_id": np.random.choice([f"S{i}" for i in range(1, n_suppliers + 1)], n_records),
    "record_date": pd.date_range(start="2023-01-01", end="2025-01-01", periods=n_records),
    "severity_level": np.random.choice(["Minor", "Moderate", "Critical"], n_records),
    "category_of_violation": np.random.choice(["Safety", "Quality", "Documentation", "Regulatory"], n_records),
    "resolution_status": np.random.choice(["Resolved", "Pending", "Unresolved"], n_records),
    "follow_up_actions": np.random.choice([0, 1], n_records),
    "length_of_letter": np.random.randint(100, 1000, n_records),
    "deadline_for_resolution": np.random.randint(1, 30, n_records),
    "ncr_or_warning_letter": np.random.choice([0, 1], n_records),  # Randomly assign target variable
})

# Define sliding window parameters
analysis_window_size = pd.DateOffset(months=12)  # 12-month analysis window
prediction_window_size = pd.DateOffset(months=6)  # 6-month prediction window
step_size = pd.DateOffset(months=3)  # 3-month step (overlap of 9 months)

# Define the start and end dates for sliding windows
start_date = historical_data["record_date"].min()
end_date = historical_data["record_date"].max()

# Initialize an empty list to store aggregated data for each window
sliding_window_data = []

# Perform sliding window aggregation
current_start = start_date
while current_start + analysis_window_size + prediction_window_size <= end_date:
    # Define the current analysis and prediction windows
    analysis_start = current_start
    analysis_end = current_start + analysis_window_size
    prediction_start = analysis_end
    prediction_end = analysis_end + prediction_window_size

    # Filter data for the analysis window
    analysis_window_data = historical_data[
        (historical_data["record_date"] >= analysis_start) &
        (historical_data["record_date"] < analysis_end)
    ]

    # Filter data for the prediction window
    prediction_window_data = historical_data[
        (historical_data["record_date"] >= prediction_start) &
        (historical_data["record_date"] < prediction_end)
    ]

    # Aggregate features for the analysis window
    aggregated_data = analysis_window_data.groupby("supplier_id").agg(
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

    # Add window metadata
    aggregated_data["analysis_start"] = analysis_start
    aggregated_data["analysis_end"] = analysis_end
    aggregated_data["prediction_start"] = prediction_start
    aggregated_data["prediction_end"] = prediction_end

    # Define the target variable for each supplier
    aggregated_data["ncr_or_warning_letter"] = aggregated_data["supplier_id"].isin(
        prediction_window_data[prediction_window_data["ncr_or_warning_letter"] == 1]["supplier_id"]
    ).astype(int)

    # Append the aggregated data for this window
    sliding_window_data.append(aggregated_data)

    # Move the window forward by the step size
    current_start += step_size

# Combine all sliding window data into a single DataFrame
final_sliding_window_data = pd.concat(sliding_window_data, ignore_index=True)

# Display the first few rows of the sliding window data
print(final_sliding_window_data.head())

# Save to CSV for further use
DATA_FOLDER = "../data/historical_ds/"
final_sliding_window_data.to_csv(DATA_FOLDER + "sliding_window_supplier_data_with_target.csv", index=False)
print(final_sliding_window_data["ncr_or_warning_letter"].value_counts())
