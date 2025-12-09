# map from country code to country name
COUNTRY_CODE = {
    'BRA': 'Brazil', 'IND': 'India', 'ARG': 'Argentina', 'KEN': 'Kenya',
    'TZA': 'Tanzania', 'ETH': 'Ethiopia', 'CIV': 'Côte d\'Ivoire', 'UGA': 'Uganda',
    'ESP': 'Spain', 'USA': 'United States', 'BGD': 'Bangladesh', 'SDN': 'Sudan',
    'CHN': 'China', 'BOL': 'Bolivia', 'COL': 'Colombia', 'SEN': 'Senegal',
    'NLD': 'Netherlands', 'GBR': 'United Kingdom', 'LAO': 'Laos', 'CHE': 'Switzerland',
    'PHL': 'Philippines', 'KHM': 'Cambodia', 'VNM': 'Vietnam', 'MEX': 'Mexico',
    'NPL': 'Nepal', 'DEU': 'Germany', 'FRA': 'France', 'ZWE': 'Zimbabwe',
    'BFA': 'Burkina Faso', 'MDG': 'Madagascar', 'IDN': 'Indonesia', 'ZMB': 'Zambia',
    'EGY': 'Egypt', 'GHA': 'Ghana', 'GAB': 'Gabon', 'CHL': 'Chile',
    'MOZ': 'Mozambique', 'THA': 'Thailand', 'CAN': 'Canada', 'ECU': 'Ecuador',
    'TLS': 'Timor-Leste', 'FJI': 'Fiji', 'LKA': 'Sri Lanka', 'GTM': 'Guatemala',
    'BEL': 'Belgium', 'GNB': 'Guinea-Bissau', 'MWI': 'Malawi', 'SLB': 'Solomon Islands',
    'RWA': 'Rwanda', 'HTI': 'Haiti', 'NER': 'Niger', 'PER': 'Peru',
    'VEN': 'Venezuela', 'LBR': 'Liberia', 'AUS': 'Australia', 'COD': 'DR Congo',
    'HND': 'Honduras', 'CMR': 'Cameroon', 'ZAF': 'South Africa', 'MLI': 'Mali',
    'SLV': 'El Salvador', 'MRT': 'Mauritania'
}

# sort countries by income level
INCOME_MAP = {
    "Low": [
        'BFA', 'MDG', 'MOZ', 'TZA', 'KEN', 'ETH', 'UGA', 'ZWE',
        'MWI', 'RWA', 'NER', 'LBR', 'COD', 'SDN', 'HTI', 'MRT',
        'GNB', 'MLI'
    ],
    "Lower middle": [
        'IND', 'BGD', 'PHL', 'VNM', 'IDN', 'EGY', 'GHA', 'ZMB',
        'CMR', 'NPL', 'KHM', 'LAO', 'LKA', 'TLS', 'HND', 'SLV',
        'SEN', 'SLB'
    ],
    "Upper middle": [
        'CHN', 'BRA', 'MEX', 'COL', 'THA', 'ZAF', 'PER', 'ECU',
        'GAB', 'ARG', 'VEN', 'BOL', 'CIV', 'GTM', 'FJI'
    ],
    "High": [
        'USA', 'GBR', 'DEU', 'FRA', 'ESP', 'NLD', 'CHE', 'CAN',
        'AUS', 'BEL', 'CHL'
    ]
}

# keywords to check what type of sponsor
SPONSOR_KEYWORDS = {
    'Government': [
        'MINISTRY', 'GOVERNMENT', 'NATIONAL INSTITUTE', 'CDC',
        'NIH', 'DEPARTMENT', 'COUNCIL'
    ],
    'Industry': [
        'PHARMA', 'INC', 'CORP', 'LTD', 'LLC', 'DIVISION',
        'LIMITED', 'KGAA'
    ],
    'Non-profit': [
        'UNIVERSITY', 'HOSPITAL', 'FOUNDATION', 'INTERNATIONAL',
        'NGO', 'TRUST', 'WHO', 'ORGANISATION', 'INSTITUTE',
        'INSTITUTIONAL', 'ACADEMY', 'DRUGS FOR NEGLECTED DISEASES INITIATIVE',
        'DRUGS FOR NEGLECTED DISEASES', 'SCHOOL', 'ACADEMIC', 'IDRI', 'PATH'
    ]
}

HIGH_BURDEN_COUNTRIES = [
    'India', 'Mexico', 'Tanzania', 'Bangladesh', 'Bolivia',
    'Côte d\'Ivoire', 'Kenya', 'Egypt'
]
