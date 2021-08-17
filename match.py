from difflib import SequenceMatcher
from typing import Dict, Tuple
import csv

from tqdm import tqdm


STATE_CODE_TO_NAME = {
    "AA": "Armed Forces America",
    "AE": "Armed Forces",
    "AK": "Alaska",
    "AL": "Alabama",
    "AP": "Armed Forces Pacific",
    "AR": "Arkansas",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "Washington DC",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VI": "Virgin Islands",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
    # Added posthoc
    "AS": "American Samoa"
}

missing_state_codes = set()


def string_similarity(string1: str, string2: str) -> float:
    """
    Scores the similarity between two strings.
    """
    string1 = string1.lower()
    string2 = string2.lower()
    return SequenceMatcher(None, string1, string2).ratio()


def match(row_one: Dict, row_two: Dict) -> Tuple:
    """
    Checks if two rows belong to the same company or not.
    If it matches, it returns a matching tuple. Otherwise returns None.
    """

    index_1 = row_one["index"]
    index_2 = row_two["index"]

    company_1 = row_one["company"]
    company_2 = row_two["company"]

    county_1 = row_one["county"]
    county_2 = row_two["county"]

    state_1 = row_one["state"]
    state_2 = row_two["state"]

    if state_1 not in STATE_CODE_TO_NAME:
        if state_1 not in missing_state_codes:
            print(f"WARNING: State code {state_1} not found.")
            missing_state_codes.add(state_1)
        return None

    state_1 = STATE_CODE_TO_NAME[state_1].lower().strip()
    state_2 = state_2.lower().strip()

    if state_1 != state_2:
        return None

    if string_similarity(county_1, county_2) < 0.7:
        return None

    if string_similarity(company_1, company_2) < 0.7:
        return None

    return (index_1, index_2, company_1, company_2,
            county_1, county_2, state_1, state_2)


def main():

    rows_one, rows_two = [], []

    with open('one.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows_one.append({
                "index": row[""],
                "company": row["Provider Name"],
                "county": row["County Name"],
                "state": row["State"]
            })

    with open('two.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows_two.append({
                "index": row[""],
                "company": row[" Local_Co_Name"],
                "county": row[" County"],
                "state": row[" State"]
            })

    matching_tuples = set()
    matching_tuples_without_index = set() # There are many matches identical except their indices.

    for row_one in tqdm(rows_one):
        for row_two in rows_two:
            matching_tuple = match(row_one, row_two)

            if matching_tuple and matching_tuple not in matching_tuples:
                matching_tuples.add(matching_tuple)
                matching_tuple_without_index = matching_tuple[2:]
                if matching_tuple_without_index not in matching_tuples_without_index:
                    print(matching_tuple_without_index)
                    matching_tuples_without_index.add(matching_tuple_without_index)


    print(f"\n There are {len(matching_tuples)} matches.")
    with open("matches.txt", "w") as file:
        for matching_tuple in matching_tuples:
            file.write("\t".join(matching_tuple))


if __name__ == '__main__':
    main()
