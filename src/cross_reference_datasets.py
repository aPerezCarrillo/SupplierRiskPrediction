import ast
import os

import pandas as pd
from rapidfuzz import fuzz, process

DS_DIR = "../data"
# Load both datasets
df1 = pd.read_csv(DS_DIR + os.sep + "warning_letters" + os.sep + "warning_letters_with_metadata.csv")
df2 = pd.read_csv(DS_DIR + os.sep + "NCR" + os.sep + "eudra_non_compliance_reports.csv")

# Convert stringified dictionaries in df1["Company Info"] to actual dictionaries
df1["Company Info"] = df1["Company Info"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# Extract relevant fields from the dictionary
df1["company_name"] = df1["Company Info"].apply(lambda x: x.get("company_name", "").lower().strip())
df1["address"] = df1["Company Info"].apply(lambda x: x.get("address", "").lower().strip())
df1["locality"] = df1["Company Info"].apply(lambda x: x.get("locality", "").lower().strip())
df1["region"] = df1["Company Info"].apply(lambda x: x.get("region", "").lower().strip())
df1["postal_code"] = df1["Company Info"].apply(lambda x: x.get("postal_code", "").lower().strip())
df1["country"] = df1["Company Info"].apply(lambda x: x.get("country", "").lower().strip())

# Standardize df2 fields
df2["Site Name"] = df2["Site Name"].str.lower().str.strip()
df2["Site Address"] = df2["Site Address"].str.lower().str.strip()
df2["City"] = df2["City"].str.lower().str.strip()
df2["Postcode"] = df2["Postcode"].str.lower().str.strip()
df2["Country"] = df2["Country"].str.lower().str.strip()

# Function to compute a weighted match score
def get_match_score(row, df2):
    best_match = process.extractOne(row["company_name"], df2["Site Name"], scorer=fuzz.partial_ratio)

    if best_match and best_match[1] >= 80:  # Name similarity must be at least 80%
        matched_site = best_match[0]
        matched_row = df2[df2["site_name"] == matched_site].iloc[0]

        # Score components (higher weight for company name and country)
        name_score = best_match[1] * 0.6
        country_score = 20 if row["country"] == matched_row["Country"] else 0
        city_score = 10 if row["locality"] and row["locality"] == matched_row["City"] else 0
        postcode_score = 10 if row["postal_code"] and row["postal_code"] == matched_row["Postcode"] else 0

        total_score = name_score + country_score + city_score + postcode_score

        if total_score >= 85:  # Only accept strong matches
            return matched_site

    return None

# Apply fuzzy matching
df1["matched_site_name"] = df1.apply(lambda row: get_match_score(row, df2), axis=1)

# Merge on matched names
merged_df = df1.merge(df2, left_on="matched_site_name", right_on="Site Name", how="left")

# Save results
merged_df.to_csv("merged_companies.csv", index=False)

print("Matching complete! Results saved to 'merged_companies.csv'")