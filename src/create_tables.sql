-- Table 1: Companies
CREATE TABLE companies (
    company_id UUID PRIMARY KEY, -- Unique identifier for each company
    company_name VARCHAR(255) NOT NULL, -- Name of the company
    address TEXT, -- Address of the company
    locality VARCHAR(255), -- City or locality
    region VARCHAR(255), -- State or region
    postal_code VARCHAR(20), -- Postal code
    country VARCHAR(255), -- Country
    oms_organisation_id VARCHAR(50), -- OMS Organisation Identifier (optional)
    oms_location_id VARCHAR(50) -- OMS Location Identifier (optional)
);

-- Table 2: Warning Letters
CREATE TABLE warning_letters (
    warning_letter_id SERIAL PRIMARY KEY, -- Unique identifier for each warning letter
    posted_date DATE, -- Date the warning letter was posted
    letter_issue_date DATE, -- Date the warning letter was issued
    issuing_office VARCHAR(255), -- Office that issued the warning letter
    subject TEXT, -- Subject of the warning letter
    response_letter TEXT, -- Response letter details
    closeout_letter TEXT, -- Closeout letter details
    excerpt TEXT, -- Excerpt from the warning letter
    link TEXT, -- Link to the warning letter
    delivery_method VARCHAR(255), -- Delivery method of the warning letter
    reference_number VARCHAR(255), -- Reference number of the warning letter
    product TEXT, -- Product(s) mentioned in the warning letter
    violations TEXT, -- Violations described in the warning letter
    company_id UUID NOT NULL, -- Foreign key referencing the companies table
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- Table 3: Eudra Non-Compliance Reports
CREATE TABLE eudra_non_compliance_reports (
    report_id SERIAL PRIMARY KEY, -- Unique identifier for each report
    report_number VARCHAR(255) NOT NULL, -- Report number
    eudragmdp_document_reference_number VARCHAR(255), -- EudraGMDP document reference number
    wda_api_reg_no VARCHAR(255), -- WDA No./API Reg. No.
    oms_organisation_id VARCHAR(50), -- OMS Organisation Identifier
    oms_location_id VARCHAR(50), -- OMS Location Identifier
    inspection_end_date DATE, -- Date the inspection ended
    issue_date DATE, -- Date the report was issued
    company_id UUID NOT NULL, -- Foreign key referencing the companies table
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

INSERT INTO companies (
    company_id, company_name, address, locality, region, postal_code, country, oms_organisation_id, oms_location_id
) VALUES (
    gen_random_uuid(), 'ABC Pharma', '123 Main St', 'New York', 'NY', '10001', 'USA', NULL, NULL
);

INSERT INTO warning_letters (
    posted_date, letter_issue_date, issuing_office, subject, response_letter, closeout_letter, excerpt, link, delivery_method, reference_number, product, violations, company_id
) VALUES (
    '2025-02-01', '2025-01-15', 'FDA Office', 'Subject of Warning Letter', 'Response Letter Details', 'Closeout Letter Details', 'Excerpt Text', 'http://example.com', 'Email', 'REF-001', 'Product Name', 'Violation Details', 'UUID-OF-COMPANY'
);

INSERT INTO eudra_non_compliance_reports (
    report_number, eudragmdp_document_reference_number, wda_api_reg_no, oms_organisation_id, oms_location_id, inspection_end_date, issue_date, company_id
) VALUES (
    'RPT-001', 'DOC-001', 'WDA-001', 'ORG-12345', 'LOC-54321', '2025-01-15', '2025-02-01', 'UUID-OF-COMPANY'
);
