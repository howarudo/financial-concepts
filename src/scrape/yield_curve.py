from bs4 import BeautifulSoup
import pandas as pd
import requests

SAVE_PATH = "data/treasury_yield_curve.csv"
YEARS_MIN = 1991
YEARS_MAX = 2023
SAVE_EVERY = 10
TREASURY_DATA_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value="
SELECT_COLUMNS = ['Date', '3 Mo', '6 Mo', '1 Yr', '2 Yr', '3 Yr', '5 Yr', '7 Yr', '10 Yr', '30 Yr']


def clean_text(text):
    """
    Clean text by removing newlines and trailing whitespace.
    """
    clean_text = text.replace('\n', '').strip()
    if clean_text == "" or clean_text == "N/A":
        return None
    return clean_text

def text_to_date(text):
    """
    Convert text to datetime object. (09/30/2021 -> 2021-09-30)
    """
    return pd.to_datetime(text, format='%m/%d/%Y')

def text_to_float(text):
    """
    Convert text to float. (0.01% -> 0.0001)
    """
    if text is None:
        return None
    return float(text)

def get_treasury_data_df(year):
    """
    Get treasury yield curve data for a given year. Base URL defined in TREASURY_DATA_URL.
    """
    response = requests.get(TREASURY_DATA_URL + str(year))
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table')
    headers = [clean_text(col_name.text) for col_name in table.find('thead').find('tr').find_all('th')]
    data = []
    for row in table.find('tbody').find_all('tr'):
        data.append([clean_text(value.text) for value in row.find_all('td')])
    return pd.DataFrame(data, columns=headers)

def main():
    print("Scraping Treasury Yield Curve data...")

    dfs = []
    for year in range(YEARS_MIN, YEARS_MAX + 1):
        print(f"Scraping data for {year}")

        df = get_treasury_data_df(year)[SELECT_COLUMNS]
        # save every SAVE_EVERY days (to avoid memory issues)
        df = df.iloc[::SAVE_EVERY]
        df["Date"] = df["Date"].apply(text_to_date)
        for col in df.columns[1:]:
            df[col] = df[col].apply(text_to_float)
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df.to_csv(SAVE_PATH, index=False)

    print(f"Data saved to {SAVE_PATH}")

if __name__ == "__main__":
    main()
