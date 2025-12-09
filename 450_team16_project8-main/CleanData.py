import pandas as pd
import os
import re
from Mapping import COUNTRY_CODE, INCOME_MAP, SPONSOR_KEYWORDS

# create output folder if it doesn't exist
os.makedirs("CleanedData", exist_ok=True)

def classify_categories(sponsor_name):
    """
    Classify sponsor into one of four categories based on keywords in their name.
    Returns: Government, Industry, Non-profit, Other, or Unknown
    """
    if pd.isna(sponsor_name) or str(sponsor_name).upper() in ['UNKNOWN', '']:
        return "Unknown"
    sponsor_upper = str(sponsor_name).upper()

    # check against predefined keywords for each category
    if any(k in sponsor_upper for k in SPONSOR_KEYWORDS['Government']):
        return "Government"
    if any(k in sponsor_upper for k in SPONSOR_KEYWORDS['Industry']):
        return "Industry"
    if any(k in sponsor_upper for k in SPONSOR_KEYWORDS['Non-profit']):
        return "Non-profit"
    return "Other"


def map_income(code_str):
    """
    Map country code to income level (Low, Lower middle, Upper middle, High).
    Handles multiple codes separated by |, comma, semicolon, or space.
    """
    if pd.isna(code_str):
        return "Unknown"
    # extract first country code if multiple codes present
    code = re.split(r'[|,;/\s]+', str(code_str).strip().upper())[0]
    for lvl, codes in INCOME_MAP.items():
        if code in codes:
            return lvl
    return "Unknown"


# Load raw clinical trial data
file_path = "ictrp_data.csv"
df = pd.read_csv(file_path, on_bad_lines="skip", encoding="utf-8")
print(f"raw data: {len(df)} ")

# standardize date formats to YYYY-MM-DD
date_fields = ['date_registration', 'date_enrollment']
for field in date_fields:
    if field in df.columns:
        df[field] = pd.to_datetime(df[field], format='%Y-%m-%d', errors='coerce').dt.strftime('%Y-%m-%d')

# extract registration year for temporal analysis
df["Year"] = pd.to_datetime(df["date_registration"], format='%Y-%m-%d', errors="coerce").dt.year

def clean_html_tags(text):
    """
    Remove HTML tags and normalize whitespace from text fields.
    This is needed because some fields contain HTML markup.
    """
    if pd.isna(text):
        return text
    text = str(text)
    # strip all HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # normalize line breaks and whitespace
    text = text.replace('\\r\\n', ' ').replace('\\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else None

# clean HTML from text fields that may contain markup
html_fields = [ "inclusion_criteria", "exclusion_criteria","primary_outcome","secondary_outcome","intervention"]
for field in html_fields:
    if field in df.columns:
        df[field] = df[field].apply(clean_html_tags)

# Remove outliers - track how many records we drop
outliers_removed = 0

# filter out unrealistic sample sizes (keep values between 1 and 1 million)
if 'target_sample_size' in df.columns:
    df['target_sample_size'] = pd.to_numeric(df['target_sample_size'], errors='coerce')
    before = len(df)
    df = df[(df['target_sample_size'].isna()) |
            ((df['target_sample_size'] > 0) & (df['target_sample_size'] <= 1000000))]
    removed = before - len(df)
    outliers_removed += removed

def validate_age(age_text):
    """
    Validate age ranges to filter out data entry errors.
    Handles different age units: years, months, days, weeks.
    Returns True if the age is within reasonable bounds.
    """
    if pd.isna(age_text):
        return True
    age_text = str(age_text).lower()
    numbers = re.findall(r'\d+', age_text)
    if not numbers:
        return True
    age = int(numbers[0])
    # different validation rules based on unit
    if 'year' in age_text or 'y'in age_text:
        return 0 <= age <= 120
    elif 'month' in age_text or 'm'in age_text:
        return 0 <= age <= 1440  # 120 years in months
    elif 'day' in age_text or 'week' in age_text:
        return True
    return 0 <= age <= 120

# apply age validation to remove unrealistic values
if 'inclusion_age_min' in df.columns and 'inclusion_age_max' in df.columns:
    before = len(df)
    df = df[df['inclusion_age_min'].apply(validate_age)]
    df = df[df['inclusion_age_max'].apply(validate_age)]
    removed = before - len(df)
    outliers_removed += removed
print(f"deleted in total {outliers_removed} ")

# Drop fields that aren't needed for analysis
print("\nDelete information")
sensitive_fields = ['contact_affiliation', 'secondary_sponsor', 'web_address', 'results_url_link']
removed_fields = []
for field in sensitive_fields:
    if field in df.columns:
        df = df.drop(field, axis=1)
        removed_fields.append(field)

if removed_fields:
    print(f"Delete: {', '.join(removed_fields)}")

# Fill missing values in categorical fields with "Unknown"
fill_fields = ["standardised_condition", "countries", "primary_sponsor", "phase", "study_type"]
for field in fill_fields:
    if field in df.columns:
        df[field] = df[field].fillna("Unknown")

# results_ind defaults to "No" if not specified
if "results_ind" in df.columns:
    df["results_ind"] = df["results_ind"].fillna("No")

# impute missing sample sizes with median (better than mean for skewed data)
if "target_sample_size" in df.columns:
    median_value = df["target_sample_size"].median()
    df["target_sample_size"] = df["target_sample_size"].fillna(median_value)
    print(f"Fill in missing values of sample size with median: {median_value}")

# Add derived columns for analysis
df["sponsor_category"] = df["primary_sponsor"].apply(classify_categories)
df["income_level"] = df["country_codes"].apply(map_income)

# show distribution of sponsor types
all_sponsor_counts = df["sponsor_category"].value_counts()
print("\nSponsor Category Classification:")
for category, count in all_sponsor_counts.items():
    print(f"  {category}: {count} ({count / len(df) * 100:.1f}%)")

# Count trials per country (handling multi-country trials)
if 'country_codes' in df.columns:
    country_list = []
    for codes in df['country_codes'].dropna():
        codes_str = str(codes).strip()
        # split multi-country codes (separated by |)
        if '|' in codes_str:
            codes = [c.strip() for c in codes_str.split('|')]
        else:
            codes = [codes_str]

        # convert codes to country names
        for code in codes:
            code = code.upper()
            if code in COUNTRY_CODE:
                country_list.append(COUNTRY_CODE[code])

    country_counts = pd.Series(country_list).value_counts()
    country_counts.to_csv("CleanedData/country_statistics.csv", header=['count'], index_label='country', encoding="utf-8-sig")
    print(f"\nTotal countries with trials: {len(country_counts)}")

# Generate separate statistics for industry-sponsored trials
if 'country_codes' in df.columns and 'sponsor_category' in df.columns:
    industry_df = df[df['sponsor_category'] == 'Industry']

    industry_countries = []
    for codes in industry_df['country_codes'].dropna():
        for code in str(codes).upper().replace('|', ' ').split():
            if code in COUNTRY_CODE:
                industry_countries.append(COUNTRY_CODE[code])

    if industry_countries:
        pd.Series(industry_countries).value_counts().to_csv(
            "CleanedData/country_Industry.csv",
            header=['count'],
            index_label='country',
            encoding="utf-8-sig"
        )
        print(f"Industry: {len(industry_df)} trials across {len(set(industry_countries))} countries")

# Create boolean flag for results publication status
df["results_posted"] = df["results_ind"].str.upper().str.strip() == "YES"
published_df = df[df["results_posted"] == True].copy()

# Count trials with published results by country
if 'country_codes' in published_df.columns:
    published_country_list = []
    for codes in published_df['country_codes'].dropna():
        codes_str = str(codes).strip()
        if '|' in codes_str:
            codes = [c.strip() for c in codes_str.split('|')]
        else:
            codes = [codes_str]

        for code in codes:
            code = code.upper()
            if code in COUNTRY_CODE:
                published_country_list.append(COUNTRY_CODE[code])

    published_country_counts = pd.Series(published_country_list).value_counts()
    published_country_counts.to_csv(f"CleanedData/published_country_statistics.csv",header=['count'], index_label='country', encoding="utf-8-sig")

print(f"\nPublished: {len(published_df)} ({len(published_df) / len(df) * 100:.1f}%)")
print(f"Unpublished: {len(df) - len(published_df)} ({(len(df) - len(published_df)) / len(df) * 100:.1f}%)")

df.to_csv("CleanedData/cleaned_ictrp.csv", index=False, encoding="utf-8-sig")
published_df.to_csv("CleanedData/published_trials.csv", index=False, encoding="utf-8-sig")

print("\nData Cleaning Completed!")
print(f"Time Range: {int(df['Year'].min())} - {int(df['Year'].max())}")
print(f"Total Trials: {len(df)}")
print("\n All CleanData completed ")
