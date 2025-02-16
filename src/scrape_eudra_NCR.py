import os

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

EUDRA_GMDP_NCR = "https://eudragmdp.ema.europa.eu/inspections/gmpc/searchGMPNonCompliance.do"
DOWNLOAD_DIR = "data/NCR"
MOCK_HTML_PATH = "data/mock/EUDRA_NCR.html"

def scrape_eudra_non_compliance_reports(source='request'):
    """
    Scrape non-compliance reports from the Eudra GMDP database.
    :return: A DataFrame containing the scraped data.
    """

    # Extract rows
    df = pd.DataFrame()

    html_content = ""
    if source == 'request':
        # Send a GET request to the webpage
        response = requests.get(EUDRA_GMDP_NCR)
        if response.status_code != 200:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            return None
        html_content = response.content
    elif source == 'mock_html':
        with open('../' + MOCK_HTML_PATH, 'r', encoding='utf-8') as file:
            html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the containing div
    div = soup.find("div", {"id": "gdpDraftForm:resultsDataTable", "class": "ui-datatable ui-widget stable"})

    if div:
        # Locate the table inside the div
        table = div.find("table")

    # Find the table using the correct ID and class
    #table = soup.find("table", {"id": "gdpDraftForm:resultsDataTable", "class": "ui-datatable ui-widget stable"})

        if not table:
            print("No table found on the webpage.")
            return None

        data = []
        # Extract headers
        headers = [th.get_text(strip=True) for th in table.find_all("th")]

        for row in table.find_all("tr")[1:]:  # Skip the header row
            cols = row.find_all("td")
            data.append([col.get_text(strip=True) for col in cols])

        # Convert to DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Save the data to a CSV file
        df.to_csv('..' + os.sep + DOWNLOAD_DIR + os.sep + "eudra_non_compliance_reports.csv", index=False)
        print("Non-compliance reports saved to eudra_non_compliance_reports.csv")

    return df




if __name__=="__main__":
    # Run the scraper
    non_compliance_data = scrape_eudra_non_compliance_reports(source='mock_html')

    # Display the scraped data
    if non_compliance_data is not None:
        print(non_compliance_data.head())