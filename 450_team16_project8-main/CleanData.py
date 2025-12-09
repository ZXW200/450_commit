import pandas as pd
import os
import re
from Mapping import COUNTRY_CODE, INCOME_MAP, SPONSOR_KEYWORDS

os.makedirs("CleanedData", exist_ok=True)

def classify_categories(sponsor_name):
    # check sponsor name and put into different types
    if pd.isna(sponsor_name) or str(sponsor_name).upper() in ['UNKNOWN', '']:
        return "Unknown"
    sponsor_upper = str(sponsor_name).upper()

    if any(k in sponsor_upper for k in SPONSOR_KEYWORDS['Government']):
        return "Government"
    if any(k in sponsor_upper for k in SPONSOR_KEYWORDS['Industry']):
        return "Industry"
    if any(k in sponsor_upper for k in SPONSOR_KEYWORDS['Non-profit']):
        return "Non-profit"
    return "Other"


def map_income(code_str):
    # use country code to find income level
    if pd.isna(code_str):
        return "Unknown"
    code = re.split(r'[|,;/\s]+', str(code_str).strip().upper())[0]
    for lvl, codes in INCOME_MAP.items():
        if code in codes:
            return lvl
    return "Unknown"


file_path = "ictrp_data.csv"
df = pd.read_csv(file_path, on_bad_lines="skip", encoding="utf-8")
print(f"raw data: {len(df)} ")

date_fields = ['date_registration', 'date_enrollment']
for field in date_fields:
    if field in df.columns:
        df[field] = pd.to_datetime(df[field], format='%Y-%m-%d', errors='coerce').dt.strftime('%Y-%m-%d')

df["Year"] = pd.to_datetime(df["date_registration"], format='%Y-%m-%d', errors="coerce").dt.year

def clean_html_tags(text):
    # remove html tags from text
    if pd.isna(text):
        return text
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('\\r\\n', ' ').replace('\\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else None

html_fields = [ "inclusion_criteria", "exclusion_criteria","primary_outcome","secondary_outcome","intervention"]
for field in html_fields:
    if field in df.columns:
        df[field] = df[field].apply(clean_html_tags)


outliers_removed = 0

if 'target_sample_size' in df.columns:
    df['target_sample_size'] = pd.to_numeric(df['target_sample_size'], errors='coerce')
    before = len(df)
    df = df[(df['target_sample_size'].isna()) |
            ((df['target_sample_size'] > 0) & (df['target_sample_size'] <= 1000000))]
    removed = before - len(df)
    outliers_removed += removed

def validate_age(age_text):
    # check if age value is reasonable
    if pd.isna(age_text):
        return True
    age_text = str(age_text).lower()
    numbers = re.findall(r'\d+', age_text)
    if not numbers:
        return True
    age = int(numbers[0])
    if 'year' in age_text or 'y'in age_text:
        return 0 <= age <= 120
    elif 'month' in age_text or 'm'in age_text:
        return 0 <= age <= 1440
    elif 'day' in age_text or 'week' in age_text:
        return True
    return 0 <= age <= 120

if 'inclusion_age_min' in df.columns and 'inclusion_age_max' in df.columns:
    before = len(df)
    df = df[df['inclusion_age_min'].apply(validate_age)]
    df = df[df['inclusion_age_max'].apply(validate_age)]
    removed = before - len(df)
    outliers_removed += removed
print(f"deleted in total {outliers_removed} ")

print("\nDelete information")
sensitive_fields = ['contact_affiliation', 'secondary_sponsor', 'web_address', 'results_url_link']
removed_fields = []
for field in sensitive_fields:
    if field in df.columns:
        df = df.drop(field, axis=1)
        removed_fields.append(field)

if removed_fields:
    print(f"Delete: {', '.join(removed_fields)}")

fill_fields = ["standardised_condition", "countries", "primary_sponsor", "phase", "study_type"]
for field in fill_fields:
    if field in df.columns:
        df[field] = df[field].fillna("Unknown")

if "results_ind" in df.columns:
    df["results_ind"] = df["results_ind"].fillna("No")

if "target_sample_size" in df.columns:
    median_value = df["target_sample_size"].median()
    df["target_sample_size"] = df["target_sample_size"].fillna(median_value)
    print(f"Fill in missing values of sample size with median: {median_value}")

df["sponsor_category"] = df["primary_sponsor"].apply(classify_categories)

df["income_level"] = df["country_codes"].apply(map_income)

all_sponsor_counts = df["sponsor_category"].value_counts()
print("\nSponsor Category Classification:")
for category, count in all_sponsor_counts.items():
    print(f"  {category}: {count} ({count / len(df) * 100:.1f}%)")

if 'country_codes' in df.columns:
    # count how many trials each country has
    country_list = []
    for codes in df['country_codes'].dropna():
        codes_str = str(codes).strip()
        if '|' in codes_str:
            codes = [c.strip() for c in codes_str.split('|')]
        else:
            codes = [codes_str]

        for code in codes:
            code = code.upper()
            if code in COUNTRY_CODE:
                country_list.append(COUNTRY_CODE[code])

    country_counts = pd.Series(country_list).value_counts()
    country_counts.to_csv("CleanedData/country_statistics.csv", header=['count'], index_label='country', encoding="utf-8-sig")
    print(f"\nTotal countries with trials: {len(country_counts)}")

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

df["results_posted"] = df["results_ind"].str.upper().str.strip() == "YES"
published_df = df[df["results_posted"] == True].copy()
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
