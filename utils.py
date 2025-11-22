
# Shared constants and utility functions

# Chicago South Side Community Area IDs (approximate list based on user request)
SOUTH_SIDE_CAS = [
    35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 67, 68, 58
]

# ACS Variable Mapping (Code -> Human Readable Name)
# Based on standard ACS definitions
ACS_VARIABLES = {
    'B19013_001E': 'median_household_income',
    'B15003_017E': 'edu_hs_diploma',
    'B15003_022E': 'edu_bachelors',
    'B03002_003E': 'race_white',
    'B03002_004E': 'race_black',
    'B03002_012E': 'race_hispanic',
    'B01001_001E': 'total_population',
    'B23025_004E': 'employed_civilians', # Verify specific table content if possible
    'B08301_001E': 'transport_total_commuters', # Usually means of transport
    'B08301_010E': 'transport_public_transit', # Adding public transit specifically if needed, asking user to confirm later
    'B17001_002E': 'poverty_count',
    'B25077_001E': 'median_housing_value'
}

# List of variables to download (keys of the dict)
# Note: censusdata expects a list of strings
ACS_VARS_LIST = list(ACS_VARIABLES.keys())

