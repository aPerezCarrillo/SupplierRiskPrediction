import pandas as pd
import uuid
from fuzzywuzzy import fuzz

# Example "companies" table
companies_data = [
    {
        "company_id": str(uuid.uuid4()),
        "company_name": "ABC Pharma",
        "address": "123 Main St",
        "locality": "New York",
        "region": "NY",
        "postal_code": "10001",
        "country": "USA",
        "oms_organisation_id": None,
        "oms_location_id": None
    }
]

# Example "Warning Letters" dataset
warning_letters_data = [
    {
        "id": 1,
        "Company Info": {
            "recipient_name": "John Doe",
            "recipient_title": "CEO",
            "company_name": "ABC Pharma Inc.",
            "address": "123 Main St",
            "locality": "New York",
            "region": "NY",
            "postal_code": "10001",
            "country": "USA"
        },
        "violation": "Failure to maintain laboratory control records"
    },
    {
        "id": 2,
        "Company Info": {
            "recipient_name": "Jane Smith",
            "recipient_title": "Director",
            "company_name": "XYZ Biotech",
            "address": "456 Elm St",
            "locality": "San Francisco",
            "region": "CA",
            "postal_code": "94107",
            "country": "USA"
        },
        "violation": "Inadequate documentation"
    }
]

# Example "Eudra Non-Compliance Reports" dataset
eudra_data = [
    {
        "Report Number": "RPT-001",
        "EudraGMDP Document Reference Number": "DOC-001",
        "WDA No./API Reg.No.": "WDA-001",
        "OMS Organisation Identifier": "ORG-12345",
        "OMS Location Identifier": "LOC-54321",
        "Site Name": "XYZ Biotech",
        "Site Address": "456 Elm St",
        "City": "San Francisco",
        "Postcode": "94107",
        "Country": "USA",
        "Inspection End Date": "2025-01-15",
        "Issue Date": "2025-02-01"
    }
]

# Convert datasets to pandas DataFrames
companies_df = pd.DataFrame(companies_data)
warning_letters_df = pd.DataFrame(warning_letters_data)
eudra_df = pd.DataFrame(eudra_data)

# Function to normalize text
def normalize_text(text):
    if not isinstance(text, str):
        return ""
    return ''.join(e for e in text.lower() if e.isalnum() or e.isspace()).strip()

# Function to generate a unique company ID
def generate_company_id():
    return str(uuid.uuid4())

# Function to compute similarity between two company records
def is_similar(company_info, company_row, threshold=85):
    # Normalize fields for comparison
    company_name_sim = fuzz.ratio(
        normalize_text(company_info["company_name"]),
        normalize_text(company_row["company_name"])
    )
    address_sim = fuzz.ratio(
        normalize_text(company_info["address"]),
        normalize_text(company_row["address"])
    )
    locality_sim = fuzz.ratio(
        normalize_text(company_info["locality"]),
        normalize_text(company_row["locality"])
    )
    region_sim = fuzz.ratio(
        normalize_text(company_info["region"]),
        normalize_text(company_row["region"])
    )
    postal_code_sim = fuzz.ratio(
        normalize_text(company_info["postal_code"]),
        normalize_text(company_row["postal_code"])
    )
    country_sim = fuzz.ratio(
        normalize_text(company_info["country"]),
        normalize_text(company_row["country"])
    )

    # Compute overall similarity (weighted average)
    overall_similarity = (
        company_name_sim * 0.4 +
        address_sim * 0.3 +
        locality_sim * 0.1 +
        region_sim * 0.1 +
        postal_code_sim * 0.05 +
        country_sim * 0.05
    )

    return overall_similarity >= threshold

# Function to cross-reference Warning Letters dataset
def cross_reference_warning_letters(warning_letters_df, companies_df):
    # Extract company info from warning letters
    company_info_list = warning_letters_df["Company Info"].apply(pd.Series)

    # Add a column for company_id in the warning letters dataset
    warning_letters_df["company_id"] = None

    # Iterate through each company in the warning letters dataset
    for index, company_info in company_info_list.iterrows():
        matched = False

        # Check for matches in the companies table
        for _, company_row in companies_df.iterrows():
            if is_similar(company_info, company_row):
                # If a match is found, assign the existing company_id
                warning_letters_df.at[index, "company_id"] = company_row["company_id"]
                matched = True
                break

        if not matched:
            # If no match is found, create a new company entry
            new_company_id = generate_company_id()
            warning_letters_df.at[index, "company_id"] = new_company_id

            # Add the new company to the companies table
            new_company = {
                "company_id": new_company_id,
                "company_name": company_info["company_name"],
                "address": company_info["address"],
                "locality": company_info["locality"],
                "region": company_info["region"],
                "postal_code": company_info["postal_code"],
                "country": company_info["country"],
                "oms_organisation_id": None,
                "oms_location_id": None
            }
            companies_df = pd.concat([companies_df, pd.DataFrame([new_company])], ignore_index=True)

    return warning_letters_df, companies_df

# Function to cross-reference Eudra dataset
def cross_reference_eudra(eudra_df, companies_df):
    # Add a column for company_id in the Eudra dataset
    eudra_df["company_id"] = None

    # Iterate through each company in the Eudra dataset
    for index, eudra_row in eudra_df.iterrows():
        matched = False

        # Check for matches in the companies table
        for _, company_row in companies_df.iterrows():
            if is_similar({
                "company_name": eudra_row["Site Name"],
                "address": eudra_row["Site Address"],
                "locality": eudra_row["City"],
                "region": None,  # Region is not provided in the Eudra dataset
                "postal_code": eudra_row["Postcode"],
                "country": eudra_row["Country"]
            }, company_row):
                # If a match is found, assign the existing company_id
                eudra_df.at[index, "company_id"] = company_row["company_id"]
                matched = True
                break

        if not matched:
            # If no match is found, create a new company entry
            new_company_id = generate_company_id()
            eudra_df.at[index, "company_id"] = new_company_id

            # Add the new company to the companies table
            new_company = {
                "company_id": new_company_id,
                "company_name": eudra_row["Site Name"],
                "address": eudra_row["Site Address"],
                "locality": eudra_row["City"],
                "region": None,
                "postal_code": eudra_row["Postcode"],
                "country": eudra_row["Country"],
                "oms_organisation_id": eudra_row["OMS Organisation Identifier"],
                "oms_location_id": eudra_row["OMS Location Identifier"]
            }
            companies_df = pd.concat([companies_df, pd.DataFrame([new_company])], ignore_index=True)

    return eudra_df, companies_df

# Cross-reference both datasets
updated_warning_letters_df, companies_df = cross_reference_warning_letters(warning_letters_df, companies_df)
updated_eudra_df, companies_df = cross_reference_eudra(eudra_df, companies_df)

# Display the updated datasets
print("Updated Warning Letters:")
print(updated_warning_letters_df)

print("\nUpdated Eudra Non-Compliance Reports:")
print(updated_eudra_df)

print("\nUpdated Companies Table:")
print(companies_df)
