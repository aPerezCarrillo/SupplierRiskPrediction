import pandas as pd
import numpy as np

# Set the number of rows for the dataset
num_rows = 1_000_0  # Adjust this to generate a larger or smaller dataset

# Generate synthetic data
np.random.seed(42)  # For reproducibility
data = {
    'supplier_id': np.arange(1, num_rows + 1),  # Unique supplier IDs
    'audit_score': np.random.uniform(50, 100, num_rows),  # Random audit scores (50-100)
    'warning_count': np.random.poisson(2, num_rows),  # Random warning counts (Poisson distribution)
    'last_audit_days_ago': np.random.randint(0, 365, num_rows),  # Days since last audit
    'region': np.random.choice(['North America', 'Europe', 'Asia', 'South America'], num_rows),  # Supplier region
    'industry': np.random.choice(['Manufacturing', 'Retail', 'Technology', 'Healthcare'], num_rows),  # Industry type
    'target': np.random.choice([0, 1], num_rows, p=[0.8, 0.2])  # Compliance (80% compliant, 20% non-compliant)
}

# Create a DataFrame
df = pd.DataFrame(data)

# Save the dataset to a CSV file
output_file = '../data/historical_ds/supplier_compliance_dataset.csv'
df.to_csv(output_file, index=False)

print(f"Dataset with {num_rows} rows saved to '{output_file}'")
