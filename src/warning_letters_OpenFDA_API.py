import requests
import pandas as pd

# Base URL for the openFDA API
FDA_API_URL = "https://api.fda.gov/food/enforcement.json"

def fetch_warning_letters(limit=10):
    """
    Fetch warning letters from the openFDA API.
    :param limit: Number of records to fetch (default is 10).
    :return: List of warning letters.
    """
    try:
        # Define query parameters
        params = {
            "limit": limit,  # Number of records to fetch
            "search": "report_date:[20220101+TO+20231231]"  # Example date range
        }

        # Send GET request to the API
        response = requests.get(FDA_API_URL, params=params)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the JSON response
        data = response.json()
        results = data.get("results", [])

        # Extract relevant fields
        warning_letters = []
        for item in results:
            warning_letters.append({
                "recall_number": item.get("recall_number"),
                "reason_for_recall": item.get("reason_for_recall"),
                "product_description": item.get("product_description"),
                "recalling_firm": item.get("recalling_firm"),
                "report_date": item.get("report_date"),
                "state": item.get("state"),
                "country": item.get("country")
            })

        return warning_letters

    except Exception as e:
        print(f"Error fetching warning letters: {e}")
        return []

# Fetch warning letters
warning_letters = fetch_warning_letters(limit=20)

# Convert to a DataFrame and save to CSV
if warning_letters:
    df = pd.DataFrame(warning_letters)
    df.to_csv("warning_letters_openFDA.csv", index=False)
    print("Warning letters saved to warning_letters.csv")
else:
    print("No warning letters found.")
