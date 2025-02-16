import re

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from bs4 import BeautifulSoup
import pandas as pd


# URL of the FDA Warning Letters page
FDA_WARNING_LETTERS_URL = "https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/compliance-actions-and-activities/warning-letters?search_api_fulltext=&search_api_fulltext_issuing_office=&field_letter_issue_datetime=All&field_change_date_closeout_letter=&field_change_date_response_letter=&field_change_date_2=All&field_letter_issue_datetime_2=&export=yes"

# Directory to save downloaded letters
DOWNLOAD_DIR = "../data/warning_letters"
WARNING_LETTER_TABLE_FN = "warning_letters_table.csv"

METADATA_LABELS = ["Delivery Method:", "Reference #:", "Product:", "Issuing Office:"]

def scrape_warning_letters_table(url):
    """
    Scrape the warning letters table from the FDA website.
    """
    try:
        # Send a GET request to the FDA Warning Letters page
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table containing the warning letters
        table = soup.find('table')
        if not table:
            print("No table found on the page.")
            return None

        # Extract table headers
        headers = [header.text.strip() for header in table.find_all('th')]

        # Extract table rows
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip the header row
            cells = row.find_all('td')
            row_data = [cell.text.strip() for cell in cells]

            # Extract the link to the warning letter
            link = row.find('a', href=True)
            if link:
                row_data.append("https://www.fda.gov" + link['href'])
            else:
                row_data.append(None)

            rows.append(row_data)

        # Add the link column to headers
        headers.append("Link")

        # Create a DataFrame
        df = pd.DataFrame(rows, columns=headers)

        return df

    except Exception as e:
        print(f"Error scraping warning letters: {e}")
        return None

def download_warning_letters(df, download_dir):
    """
    Download the warning letters from the links in the DataFrame.
    """
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for index, row in df.iterrows():
        link = row['Link']
        if link:
            try:
                # Get the content of the warning letter
                response = requests.get(link)
                response.raise_for_status()

                # Save the warning letter as an HTML file
                filename = os.path.join(download_dir, f"warning_letter_{index + 1}.html")
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {filename}")

            except Exception as e:
                print(f"Error downloading warning letter from {link}: {e}")


def extract_metadata_and_text_from_html(file_path):
    """
    Extract metadata and letter text from the warning letter HTML file.
    :param file_path: Path to the HTML file.
    :return: A dictionary containing metadata and letter text.
    """
    try:
        # Open and parse the HTML file
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Extract metadata
        metadata = {}

        for label in METADATA_LABELS:
            element = soup.find('dt', string=label)
            if element:
                metadata[label.strip(":")] = element.find_next('dd').text.strip()
            else:
                metadata[label.strip(":")] = None

        # Extract company information
        '''company_info = {
            "recipient_name": soup.find("div", {"class": "field--name-field-recipient-name"}).find("div", {
                "class": "field--item"}).text.strip(),
            "recipient_title": soup.find("div", {"class": "field--name-field-recipient-title"}).find("div", {
                "class": "field--item"}).text.strip(),
            "company_name": soup.find("h1", {"class": "text-center content-title"}).contents[0].strip(),
            "address": soup.find("span", {"class": "address-line1"}).text.strip(),
            "locality": soup.find("span", {"class": "locality"}).text.strip(),
            "region": soup.find("span", {"class": "administrative-area"}).text.strip(),
            "postal_code": soup.find("span", {"class": "postal-code"}).text.strip(),
            "country": soup.find("span", {"class": "country"}).text.strip()
        }'''
        # Extract company information (adapted for different structures)
        company_info = {}
        # Try finding company name
        company_name = soup.find("h1", {"class": "text-center content-title"})
        if company_name:
            company_info["company_name"] = company_name.text.strip()
        else:
            company_info["company_name"] = soup.find("meta", {"property": "og:title"})["content"].split(" - ")[0]

        # Try finding recipient name
        recipient = soup.find("div", {"class": "field--name-field-recipient-name"})
        if recipient:
            company_info["recipient_name"] = recipient.find("div", {"class": "field--item"}).text.strip()
        else:
            company_info["recipient_name"] = "Not found"

        # Extract address details
        address_fields = ["address-line1", "address-line2", "locality", "administrative-area", "postal-code", "country"]
        for field in address_fields:
            tag = soup.find("span", {"class": field})
            company_info[field.replace("-", "_")] = tag.text.strip() if tag else "Not found"

        metadata["Company Info"] = company_info

        # Extract violations (different structures)
        violations = []
        violation_patterns = [
            r"fail.* to .*?\.?",  # Matches phrases like "failure to maintain records."
            r"deviat.* to .*?\.?",
            r"inadequat.* .*?\.?",  # Matches phrases like "inadequate documentation."
            r"lack of .*?\.?",  # Matches phrases like "lack of access controls."
        ]
        for header in soup.find_all(["strong", "b"]):
            for pattern in violation_patterns:
                matches = re.findall(pattern, header.text, re.IGNORECASE)
                violations.extend(matches)

        metadata["Violations"] = ';'.join(violations)
        return metadata

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None


# Defining main function
def main():
    # Scrape the warning letters table and save the data
    file_path = DOWNLOAD_DIR + os.sep + WARNING_LETTER_TABLE_FN
    if os.path.exists(file_path):
        warning_letters_df =  pd.read_csv(file_path)
    else:
        warning_letters_df = scrape_warning_letters_table(FDA_WARNING_LETTERS_URL)
        warning_letters_df.to_csv(file_path)

    # Add metadata and letter text to the DataFrame
    metadata_list = []
    for i, row in warning_letters_df.iterrows():
        html_file_path = DOWNLOAD_DIR + os.sep +  'warning_letter_' + str(i+1) + '.html'
        metadata = extract_metadata_and_text_from_html(html_file_path)
        if metadata:
            metadata_list.append(metadata)
        else:
            metadata_list.append({key: None for key in METADATA_LABELS})
    # Merge metadata with the original DataFrame
    metadata_df = pd.DataFrame(metadata_list)
    final_df = pd.concat([warning_letters_df, metadata_df], axis=1)

    # Save the final DataFrame to a CSV file
    final_df.to_csv(DOWNLOAD_DIR + os.sep +  "warning_letters_with_metadata.csv", index=False)
    print("Warning letters with metadata saved to warning_letters_with_metadata.csv")

def trend_analysis(warning_letters_df):

    # Example columns: ['Recipient', 'Issuing Office', 'Reference #', 'Product', 'Violations', 'Corrective Actions']

    # Analyze the frequency of violations
    violation_counts = warning_letters_df['Violations'].str.split(';').explode().value_counts()
    print("Frequency of Violations:")
    print(violation_counts)

    # Identify high-risk suppliers
    high_risk_suppliers = warning_letters_df[warning_letters_df['Violations'].str.contains("data integrity|quality unit", case=False)]
    print("\nHigh-Risk Suppliers:")
    print(high_risk_suppliers[['Recipient', 'Violations']])

    # Assess trends over time (if date column is available)
    warning_letters_df['Date'] = pd.to_datetime(warning_letters_df['Date'])
    trend_analysis = warning_letters_df.groupby(warning_letters_df['Date'].dt.year)['Violations'].count()
    print("\nTrend Analysis (Violations Over Time):")
    print(trend_analysis)



if __name__=="__main__":
    main()
    #trend analysis
    # Load the warning letters data
    '''try:
        # warning_letters_df = pd.read_csv("../data/mock/mock_wrning_letters_wiht_metadata.csv")
        warning_letters_df = pd.read_csv("../data/warning_letters/warning_letters_with_metadata.csv")
        trend_analysis(warning_letters_df)
    except:
        print("Could not open file")'''

    #extract_metadata_from_warning_letters_html()

