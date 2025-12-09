#Version 1.14.2
#Data 02.12.2025
import pandas as pd
import os
import re
from Mapping import COUNTRY_CODE, INCOME_MAP, SPONSOR_KEYWORDS

os.makedirs("CleanedData", exist_ok=True)
# 赞助商分类 Sponsor classification
def classify_categories(sponsor_name):
    #根据赞助商名称分类为：政府、公司、非营利组织或其他
    #Classified by sponsor name: government, industry, non-profit organization, or othe
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
    if pd.isna(code_str):
        return "Unknown"
    code = re.split(r'[|,;/\s]+', str(code_str).strip().upper())[0]
    for lvl, codes in INCOME_MAP.items():
        if code in codes:
            return lvl
    return "Unknown"


# 读取原始数据 Read raw data
file_path = "ictrp_data.csv"
df = pd.read_csv(file_path, on_bad_lines="skip", encoding="utf-8")
print(f"raw data: {len(df)} ")

# 处理日期字段 Process date fields
date_fields = ['date_registration', 'date_enrollment']
for field in date_fields:
    if field in df.columns:
        df[field] = pd.to_datetime(df[field], format='%Y-%m-%d', errors='coerce').dt.strftime('%Y-%m-%d')
# 提取注册年份 Extract registration year
df["Year"] = pd.to_datetime(df["date_registration"], format='%Y-%m-%d', errors="coerce").dt.year

# 清理HTML标签函数 Clean HTML tags function
def clean_html_tags(text):
    if pd.isna(text):
        return text
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('\\r\\n', ' ').replace('\\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else None

#清除所选列名的html标签 Clear the HTML tags of the selected column names
html_fields = [ "inclusion_criteria", "exclusion_criteria","primary_outcome","secondary_outcome","intervention"]
for field in html_fields:
    if field in df.columns:
        df[field] = df[field].apply(clean_html_tags)




# # print("\noutlier detection...")
outliers_removed = 0
# 检测样本量异常值 Check sample size outliers <=1000000 >0
if 'target_sample_size' in df.columns:
    df['target_sample_size'] = pd.to_numeric(df['target_sample_size'], errors='coerce')
    before = len(df)
    df = df[(df['target_sample_size'].isna()) |
            ((df['target_sample_size'] > 0) & (df['target_sample_size'] <= 1000000))]
    removed = before - len(df)
    outliers_removed += removed
    # print(f"样本量异常: 删除 {removed} 条")

# 年龄验证 Age validation
def validate_age(age_text):
    if pd.isna(age_text):
        return True
    age_text = str(age_text).lower()
    numbers = re.findall(r'\d+', age_text)
    if not numbers:
        return True
    age = int(numbers[0])
    if 'year' in age_text or 'y'in age_text:#年最大等于120 最小大于等于0
        return 0 <= age <= 120
    elif 'month' in age_text or 'm'in age_text:#120*12 = 1440
        return 0 <= age <= 1440
    elif 'day' in age_text or 'week' in age_text:
        return True
    return 0 <= age <= 120

# 检测年龄异常值 Check age outliers
# 检查年龄逻辑是否合理 Check age logic validity
if 'inclusion_age_min' in df.columns and 'inclusion_age_max' in df.columns:
    before = len(df)
    # 检查最小和最大年龄都有效 Check that both the minimum and maximum age are valid
    df = df[df['inclusion_age_min'].apply(validate_age)]
    df = df[df['inclusion_age_max'].apply(validate_age)]
    removed = before - len(df)
    outliers_removed += removed
print(f"deleted in total {outliers_removed} ")
#
# print("\nDelete information")
sensitive_fields = ['contact_affiliation', 'secondary_sponsor', 'web_address', 'results_url_link']
removed_fields = []
for field in sensitive_fields:
    if field in df.columns:
        df = df.drop(field, axis=1)
        removed_fields.append(field)

if removed_fields:
    print(f"Delete: {', '.join(removed_fields)}")

# print("\nfill...")
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
# 赞助商分类 Sponsor classification
df["sponsor_category"] = df["primary_sponsor"].apply(classify_categories)
##世界收入分类 Worldbank Classification
df["income_level"] = df["country_codes"].apply(map_income)
#统计赞助商分类占比 Proportion of sponsor classification
all_sponsor_counts = df["sponsor_category"].value_counts()
print("\nSponsor Category Classification:")
for category, count in all_sponsor_counts.items():
    print(f"  {category}: {count} ({count / len(df) * 100:.1f}%)")
 
# 统计各国实验数量 Count the number of experiments in each country
if 'country_codes' in df.columns:
    # 处理多国家情况进行统计 Handling multi country situations for statistical analysis
    country_list = []
    for codes in df['country_codes'].dropna():
        codes_str = str(codes).strip()
        if '|' in codes_str:
            codes = [c.strip() for c in codes_str.split('|')]
        else:
            codes = [codes_str]

        # Escaping country codes
        for code in codes:
            code = code.upper()
            if code in COUNTRY_CODE:
                country_list.append(COUNTRY_CODE[code])

    country_counts = pd.Series(country_list).value_counts()
    # 保存完整的国家统计 Save complete national statistics
    country_counts.to_csv("CleanedData/country_statistics.csv", header=['count'], index_label='country', encoding="utf-8-sig")
    print(f"\nTotal countries with trials: {len(country_counts)}")
    #按赞助商分类统计各国实验数量 Count the number of experiments in each country by sponsor classification
if 'country_codes' in df.columns and 'sponsor_category' in df.columns:
    # 筛选Industry类别 Filter Industry Category
    industry_df = df[df['sponsor_category'] == 'Industry']

    # 提取所有国家代码 Extract all country codes
    industry_countries = []
    for codes in industry_df['country_codes'].dropna():
        for code in str(codes).upper().replace('|', ' ').split():
            if code in COUNTRY_CODE:
                industry_countries.append(COUNTRY_CODE[code])

    # 统计并保存 Statistics and Save
    if industry_countries:
        pd.Series(industry_countries).value_counts().to_csv(
            "CleanedData/country_Industry.csv",
            header=['count'],
            index_label='country',
            encoding="utf-8-sig"
        )
        print(f"Industry: {len(industry_df)} trials across {len(set(industry_countries))} countries")
        #统计已发表的国家 Statistics published
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

        # Escaping country codes
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

# 根据 pregnant_participants 字段筛选孕妇相关试验
#Screening pregnant women related trials based on the pregnant_participants field
# if 'pregnant_participants' in df.columns:
#     pregnant_trials = df[df['pregnant_participants'].str.upper().str.strip() == 'INCLUDED'].copy()
#     pregnant_trials.to_csv("CleanedData/pregnant_trials.csv", index=False, encoding="utf-8-sig")
#     print(f"Pregnant Trials: {len(pregnant_trials)}")
# else:
#     print("Warning: 'pregnant_participants' column not found in data")
#     pregnant_trials = pd.DataFrame()

print("\nData Cleaning Completed!")
print(f"Time Range: {int(df['Year'].min())} - {int(df['Year'].max())}")
print(f"Total Trials: {len(df)}")
print("\n All CleanData completed ")
